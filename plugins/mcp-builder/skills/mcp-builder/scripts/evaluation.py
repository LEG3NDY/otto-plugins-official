"""MCP Server Evaluation Harness.

This script evaluates MCP servers by running test questions against them
through `otto -p`. It preserves the original CLI shape (`stdio`, `sse`,
`http`, headers, env, report output) while removing any direct dependency on
provider-specific SDKs from the public marketplace.
"""

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

EVALUATION_PROMPT = """You are Otto with access to MCP tools.

When given a task, you MUST:
1. Use the available tools to complete the task
2. Provide summary of each step in your approach, wrapped in <summary> tags
3. Provide feedback on the tools provided, wrapped in <feedback> tags
4. Provide your final response, wrapped in <response> tags

Summary Requirements:
- In your <summary> tags, you must explain:
  - The steps you took to complete the task
  - Which tools you used, in what order, and why
  - The inputs you provided to each tool
  - The outputs you received from each tool
  - A summary for how you arrived at the response

Feedback Requirements:
- In your <feedback> tags, provide constructive feedback on the tools:
  - Comment on tool names: Are they clear and descriptive?
  - Comment on input parameters: Are they well-documented? Are required vs optional parameters clear?
  - Comment on descriptions: Do they accurately describe what the tool does?
  - Comment on any errors encountered during tool usage: Did the tool fail to execute? Did the tool return too many tokens?
  - Identify specific areas for improvement and explain WHY they would help
  - Be specific and actionable in your suggestions

Response Requirements:
- Your response should be concise and directly address what was asked
- Always wrap your final response in <response> tags
- If you cannot solve the task return <response>NOT_FOUND</response>
- For numeric responses, provide just the number
- For IDs, provide just the ID
- For names or text, provide the exact text requested
- Your response should go last"""

REPORT_HEADER = """
# Evaluation Report

## Summary

- **Accuracy**: {correct}/{total} ({accuracy:.1f}%)
- **Average Task Duration**: {average_duration_s:.2f}s
- **Average Tool Calls per Task**: {average_tool_calls:.2f}
- **Total Tool Calls**: {total_tool_calls}

---
"""

TASK_TEMPLATE = """
### Task {task_num}

**Question**: {question}
**Ground Truth Answer**: `{expected_answer}`
**Actual Answer**: `{actual_answer}`
**Correct**: {correct_indicator}
**Duration**: {total_duration:.2f}s
**Tool Calls**: {tool_calls}

**Summary**
{summary}

**Feedback**
{feedback}

---
"""


def parse_evaluation_file(file_path: Path) -> list[dict[str, str]]:
    """Parse XML evaluation file with qa_pair elements."""
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
    except Exception as exc:
        print(f"Error parsing evaluation file {file_path}: {exc}")
        return []

    evaluations: list[dict[str, str]] = []
    for qa_pair in root.findall(".//qa_pair"):
        question_elem = qa_pair.find("question")
        answer_elem = qa_pair.find("answer")
        if question_elem is None or answer_elem is None:
            continue
        evaluations.append(
            {
                "question": (question_elem.text or "").strip(),
                "answer": (answer_elem.text or "").strip(),
            }
        )
    return evaluations


def extract_xml_content(text: str | None, tag: str) -> str | None:
    """Extract content from XML tags."""
    if not text:
        return None
    pattern = rf"<{tag}>(.*?)</{tag}>"
    matches = re.findall(pattern, text, re.DOTALL)
    return matches[-1].strip() if matches else None


def parse_headers(header_list: list[str] | None) -> dict[str, str]:
    """Parse header strings in format 'Key: Value' into a dictionary."""
    headers: dict[str, str] = {}
    if not header_list:
        return headers
    for header in header_list:
        if ":" not in header:
            print(f"Warning: Ignoring malformed header: {header}")
            continue
        key, value = header.split(":", 1)
        headers[key.strip()] = value.strip()
    return headers


def parse_env_vars(env_list: list[str] | None) -> dict[str, str]:
    """Parse environment variable strings in format 'KEY=VALUE' into a dictionary."""
    env: dict[str, str] = {}
    if not env_list:
        return env
    for env_var in env_list:
        if "=" not in env_var:
            print(f"Warning: Ignoring malformed environment variable: {env_var}")
            continue
        key, value = env_var.split("=", 1)
        env[key.strip()] = value.strip()
    return env


def _resolve_path_like(value: str, base_dir: Path) -> str:
    candidate = base_dir / value
    if value and not Path(value).is_absolute() and candidate.exists():
        return str(candidate.resolve())
    return value


def build_server_config(args: argparse.Namespace, headers: dict[str, str], env_vars: dict[str, str]) -> dict[str, Any]:
    """Build a temporary .mcp.json config for otto -p."""
    base_dir = Path.cwd()

    if args.transport == "stdio":
        if not args.command:
            raise ValueError("stdio transport requires --command")
        command = _resolve_path_like(args.command, base_dir)
        resolved_args = [_resolve_path_like(arg, base_dir) for arg in (args.args or [])]
        if os.name == "nt":
            full_command = subprocess.list2cmdline([command, *resolved_args])
            wrapped_command = "cmd"
            wrapped_args = ["/d", "/s", "/c", f"cd /d {base_dir} && {full_command}"]
        else:
            full_command = shlex.join([command, *resolved_args])
            wrapped_command = "/bin/sh"
            wrapped_args = ["-lc", f"cd {shlex.quote(str(base_dir))} && exec {full_command}"]
        return {
            "mcpServers": {
                "evaluation-target": {
                    "command": wrapped_command,
                    "args": wrapped_args,
                    "env": env_vars or None,
                }
            }
        }

    if not args.url:
        raise ValueError(f"{args.transport} transport requires --url")

    remote_config: dict[str, Any] = {
        "type": args.transport,
        "url": args.url,
    }
    if headers:
        remote_config["headers"] = headers

    return {"mcpServers": {"evaluation-target": remote_config}}


def normalize_config(config: dict[str, Any]) -> dict[str, Any]:
    """Drop empty values before writing .mcp.json."""
    servers = config.get("mcpServers", {})
    cleaned_servers: dict[str, Any] = {}
    for name, server in servers.items():
        cleaned_servers[name] = {
            key: value for key, value in server.items() if value not in (None, {}, [])
        }
    return {"mcpServers": cleaned_servers}


def get_otto_command() -> list[str]:
    """Resolve the Otto CLI command, allowing an explicit override."""
    override = os.environ.get("OTTO_EVAL_COMMAND", "").strip()
    if override:
        return shlex.split(override)
    return ["otto"]


def run_single_task_with_otto(
    question: str,
    config: dict[str, Any],
    model: str | None,
    timeout_seconds: int,
) -> tuple[str | None, dict[str, dict[str, Any]], str]:
    """Run a single evaluation question through Otto and return parsed output."""
    prompt = f"{EVALUATION_PROMPT}\n\nTask:\n{question}"
    env = {key: value for key, value in os.environ.items() if key != "OTTOCODE"}

    with tempfile.TemporaryDirectory(prefix="otto-mcp-eval-") as temp_dir:
        temp_path = Path(temp_dir)
        (temp_path / ".mcp.json").write_text(
            json.dumps(normalize_config(config), indent=2) + "\n"
        )

        cmd = [
            *get_otto_command(),
            "-p",
            prompt,
            "--output-format",
            "stream-json",
            "--verbose",
            "--include-partial-messages",
        ]
        if model:
            cmd.extend(["--model", model])

        try:
            completed = subprocess.run(
                cmd,
                cwd=temp_path,
                env=env,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
            )
        except FileNotFoundError as exc:
            raise RuntimeError(
                "Could not find `otto` on PATH. Install Otto Code, or set OTTO_EVAL_COMMAND to an explicit Otto CLI command."
            ) from exc
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(f"Otto timed out after {timeout_seconds}s") from exc

    tool_metrics: dict[str, dict[str, Any]] = {}
    response_text: str | None = None

    for raw_line in completed.stdout.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue

        if event.get("type") == "stream_event":
            stream_event = event.get("event", {})
            if stream_event.get("type") == "content_block_start":
                content_block = stream_event.get("content_block", {})
                if content_block.get("type") == "tool_use":
                    tool_name = content_block.get("name", "unknown")
                    metric = tool_metrics.setdefault(
                        tool_name, {"count": 0, "durations": []}
                    )
                    metric["count"] += 1
                    metric["durations"].append(0.0)
        elif event.get("type") == "assistant":
            message = event.get("message", {})
            text_parts = [
                item.get("text", "")
                for item in message.get("content", [])
                if item.get("type") == "text"
            ]
            if text_parts:
                response_text = "\n".join(part for part in text_parts if part)
        elif event.get("type") == "result" and not response_text:
            result_text = event.get("result")
            if isinstance(result_text, str):
                response_text = result_text

    if completed.returncode != 0 and not response_text:
        stderr = completed.stderr.strip()
        raise RuntimeError(stderr or f"otto exited with code {completed.returncode}")

    return response_text, tool_metrics, completed.stderr.strip()


def evaluate_single_task(
    qa_pair: dict[str, str],
    task_index: int,
    config: dict[str, Any],
    model: str | None,
    timeout_seconds: int,
) -> dict[str, Any]:
    """Evaluate a single QA pair."""
    start_time = time.time()
    print(f"Task {task_index + 1}: Running task with question: {qa_pair['question']}")

    response_text: str | None = None
    tool_metrics: dict[str, dict[str, Any]] = {}
    stderr_summary = ""

    try:
        response_text, tool_metrics, stderr_summary = run_single_task_with_otto(
            qa_pair["question"],
            config,
            model,
            timeout_seconds,
        )
    except Exception as exc:
        stderr_summary = str(exc)

    duration_seconds = time.time() - start_time
    response_value = extract_xml_content(response_text, "response")
    summary = extract_xml_content(response_text, "summary")
    feedback = extract_xml_content(response_text, "feedback")

    if not summary and stderr_summary:
        summary = stderr_summary
    if not feedback:
        feedback = "N/A"
    if not response_value and response_text and not response_text.lstrip().startswith("<"):
        response_value = response_text.strip()

    num_tool_calls = sum(len(metrics["durations"]) for metrics in tool_metrics.values())
    return {
        "question": qa_pair["question"],
        "expected": qa_pair["answer"],
        "actual": response_value,
        "score": int(response_value == qa_pair["answer"]) if response_value else 0,
        "total_duration": duration_seconds,
        "tool_calls": tool_metrics,
        "num_tool_calls": num_tool_calls,
        "summary": summary or "N/A",
        "feedback": feedback or "N/A",
    }


def run_evaluation(
    eval_path: Path,
    config: dict[str, Any],
    model: str | None,
    timeout_seconds: int,
) -> str:
    """Run the full evaluation and return a markdown report."""
    print("🚀 Starting Evaluation")

    qa_pairs = parse_evaluation_file(eval_path)
    print(f"📋 Loaded {len(qa_pairs)} evaluation tasks")

    results = []
    for index, qa_pair in enumerate(qa_pairs):
        print(f"Processing task {index + 1}/{len(qa_pairs)}")
        results.append(
            evaluate_single_task(qa_pair, index, config, model, timeout_seconds)
        )

    correct = sum(result["score"] for result in results)
    accuracy = (correct / len(results)) * 100 if results else 0
    average_duration_s = (
        sum(result["total_duration"] for result in results) / len(results)
        if results
        else 0
    )
    average_tool_calls = (
        sum(result["num_tool_calls"] for result in results) / len(results)
        if results
        else 0
    )
    total_tool_calls = sum(result["num_tool_calls"] for result in results)

    report = REPORT_HEADER.format(
        correct=correct,
        total=len(results),
        accuracy=accuracy,
        average_duration_s=average_duration_s,
        average_tool_calls=average_tool_calls,
        total_tool_calls=total_tool_calls,
    )

    report += "".join(
        TASK_TEMPLATE.format(
            task_num=index + 1,
            question=qa_pair["question"],
            expected_answer=qa_pair["answer"],
            actual_answer=result["actual"] or "N/A",
            correct_indicator="✅" if result["score"] else "❌",
            total_duration=result["total_duration"],
            tool_calls=json.dumps(result["tool_calls"], indent=2),
            summary=result["summary"],
            feedback=result["feedback"],
        )
        for index, (qa_pair, result) in enumerate(zip(qa_pairs, results))
    )

    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate MCP servers using test questions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Evaluate a local stdio MCP server
  python evaluation.py -t stdio -c python -a my_server.py eval.xml

  # Evaluate an SSE MCP server
  python evaluation.py -t sse -u https://example.com/mcp -H "Authorization: Bearer token" eval.xml

  # Evaluate an HTTP MCP server with custom model
  python evaluation.py -t http -u https://example.com/mcp -m your-model-id eval.xml
        """,
    )

    parser.add_argument("eval_file", type=Path, help="Path to evaluation XML file")
    parser.add_argument(
        "-t",
        "--transport",
        choices=["stdio", "sse", "http"],
        default="stdio",
        help="Transport type (default: stdio)",
    )
    parser.add_argument(
        "-m",
        "--model",
        default=os.environ.get("OTTO_EVAL_MODEL"),
        help="Model to use (default: OTTO_EVAL_MODEL or Otto default)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=600,
        help="Per-question timeout in seconds (default: 600)",
    )

    stdio_group = parser.add_argument_group("stdio options")
    stdio_group.add_argument("-c", "--command", help="Command to run MCP server (stdio only)")
    stdio_group.add_argument("-a", "--args", nargs="+", help="Arguments for the command (stdio only)")
    stdio_group.add_argument(
        "-e",
        "--env",
        nargs="+",
        help="Environment variables in KEY=VALUE format (stdio only)",
    )

    remote_group = parser.add_argument_group("sse/http options")
    remote_group.add_argument("-u", "--url", help="MCP server URL (sse/http only)")
    remote_group.add_argument(
        "-H",
        "--header",
        nargs="+",
        dest="headers",
        help="HTTP headers in 'Key: Value' format (sse/http only)",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output file for evaluation report (default: stdout)",
    )

    args = parser.parse_args()

    if not args.eval_file.exists():
        print(f"Error: Evaluation file not found: {args.eval_file}")
        sys.exit(1)

    headers = parse_headers(args.headers)
    env_vars = parse_env_vars(args.env)

    try:
        config = build_server_config(args, headers, env_vars)
    except ValueError as exc:
        print(f"Error: {exc}")
        sys.exit(1)

    report = run_evaluation(args.eval_file, config, args.model, args.timeout)
    if args.output:
        args.output.write_text(report)
        print(f"\n✅ Report saved to {args.output}")
    else:
        print("\n" + report)


if __name__ == "__main__":
    main()

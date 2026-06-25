#!/usr/bin/env python3
"""Snapshot or watch OpenAI organization costs and completion usage."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


COSTS_URL = "https://api.openai.com/v1/organization/costs"
USAGE_COMPLETIONS_URL = "https://api.openai.com/v1/organization/usage/completions"
EARLY_DELTA_USD = 0.25
MEDIUM_DELTA_USD = 0.50
LATE_DELTA_USD = 1.00
COST_GROUP_FIELDS = {"project_id", "api_key_id", "line_item"}
USAGE_GROUP_FIELDS = {"project_id", "user_id", "api_key_id", "model", "batch", "service_tier"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Monitor OpenAI organization costs or completion usage with OPENAI_ADMIN_KEY."
    )
    parser.add_argument(
        "--source",
        choices=("costs", "usage-completions"),
        default="costs",
        help="Monitor dollar costs or completions request/token usage.",
    )
    parser.add_argument("--days", type=int, default=1, help="Days to include in the query window.")
    parser.add_argument("--minutes", type=int, default=10, help="Minutes to include for usage snapshots.")
    parser.add_argument("--start-time", type=int, help="Unix seconds for query start, inclusive.")
    parser.add_argument("--end-time", type=int, help="Unix seconds for query end, exclusive.")
    parser.add_argument(
        "--group-by",
        action="append",
        choices=tuple(sorted(COST_GROUP_FIELDS | USAGE_GROUP_FIELDS)),
        help="Group results. Repeatable.",
    )
    parser.add_argument("--project-id", action="append", help="Filter to an OpenAI project id.")
    parser.add_argument("--api-key-id", action="append", help="Filter to an OpenAI API key id.")
    parser.add_argument("--model", action="append", help="Filter usage-completions to a model.")
    parser.add_argument(
        "--bucket-width",
        choices=("1m", "1h", "1d"),
        help="Usage bucket width. Costs always use 1d. Usage defaults to 1m.",
    )
    parser.add_argument("--limit", type=int, default=7, help="Cost or usage buckets to request.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of compact text.")
    parser.add_argument("--watch", action="store_true", help="Poll repeatedly and report deltas.")
    parser.add_argument("--interval", type=int, default=120, help="Seconds between watch polls.")
    parser.add_argument("--max-polls", type=int, default=0, help="Maximum watch polls; 0 means until stopped.")
    parser.add_argument(
        "--early-threshold-usd",
        type=float,
        default=EARLY_DELTA_USD,
        help="Label cost interval deltas at or above this amount as early.",
    )
    parser.add_argument(
        "--medium-threshold-usd",
        type=float,
        default=MEDIUM_DELTA_USD,
        help="Label cost interval deltas at or above this amount as medium.",
    )
    parser.add_argument(
        "--late-threshold-usd",
        type=float,
        default=LATE_DELTA_USD,
        help="Label cost interval deltas at or above this amount as late.",
    )
    parser.add_argument(
        "--stop-threshold-usd",
        type=float,
        help="Exit with status 2 when a cost interval delta reaches this amount.",
    )
    parser.add_argument(
        "--continue-after-flag",
        action="store_true",
        help="Keep polling after a flagged interval instead of exiting for user approval.",
    )
    parser.add_argument(
        "--allow-fast-polling",
        action="store_true",
        help="Allow intervals under 120 seconds. Use sparingly.",
    )
    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> None:
    if args.limit < 1 or args.limit > 180:
        raise SystemExit("limit must be between 1 and 180")
    group_fields = set(args.group_by or [])
    if args.source == "costs":
        invalid = group_fields - COST_GROUP_FIELDS
        if invalid:
            raise SystemExit(f"costs source does not support group_by={sorted(invalid)}")
    else:
        invalid = group_fields - USAGE_GROUP_FIELDS
        if invalid:
            raise SystemExit(f"usage-completions source does not support group_by={sorted(invalid)}")


def bucket_seconds(args: argparse.Namespace) -> int:
    if args.bucket_width == "1d":
        return 86_400
    if args.bucket_width == "1h":
        return 3_600
    return 60


def query_window(args: argparse.Namespace) -> tuple[int, int]:
    end_time = args.end_time or int(time.time())
    if args.start_time:
        start_time = args.start_time
    elif args.source == "usage-completions":
        start_time = end_time - max(args.minutes, 1) * 60
    else:
        start_time = end_time - max(args.days, 1) * 86_400
    if start_time >= end_time:
        raise SystemExit("start time must be earlier than end time")
    return start_time, end_time


def build_url(args: argparse.Namespace, start_time: int, end_time: int) -> str:
    if args.source == "costs":
        base_url = COSTS_URL
        bucket_width = "1d"
    else:
        base_url = USAGE_COMPLETIONS_URL
        bucket_width = args.bucket_width or "1m"
    params: list[tuple[str, str]] = [
        ("start_time", str(start_time)),
        ("end_time", str(end_time)),
        ("bucket_width", bucket_width),
        ("limit", str(args.limit)),
    ]
    for field in args.group_by or []:
        params.append(("group_by[]", field))
    for project_id in args.project_id or []:
        params.append(("project_ids[]", project_id))
    for api_key_id in args.api_key_id or []:
        params.append(("api_key_ids[]", api_key_id))
    for model in args.model or []:
        params.append(("models[]", model))
    return f"{base_url}?{urllib.parse.urlencode(params)}"


def fetch_payload(args: argparse.Namespace) -> dict[str, Any]:
    admin_key = os.environ.get("OPENAI_ADMIN_KEY")
    if not admin_key:
        raise SystemExit("OPENAI_ADMIN_KEY is not set")
    start_time, end_time = query_window(args)
    request = urllib.request.Request(
        build_url(args, start_time, end_time),
        headers={
            "Authorization": f"Bearer {admin_key}",
            "Content-Type": "application/json",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"OpenAI admin request failed: HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"OpenAI admin request failed: {exc.reason}") from exc


def utc_label(timestamp: int) -> str:
    return dt.datetime.fromtimestamp(timestamp, tz=dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")


def bucket_cost_total(bucket: dict[str, Any]) -> float:
    total = 0.0
    for result in bucket.get("results", []):
        amount = result.get("amount") or {}
        value = amount.get("value")
        if isinstance(value, (int, float)):
            total += float(value)
    return total


def response_cost_total(payload: dict[str, Any]) -> float:
    return sum(bucket_cost_total(bucket) for bucket in payload.get("data", []))


def response_usage_totals(payload: dict[str, Any]) -> dict[str, int]:
    totals = {
        "num_model_requests": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "input_cached_tokens": 0,
    }
    for bucket in payload.get("data", []):
        for result in bucket.get("results", []):
            for key in totals:
                value = result.get(key)
                if isinstance(value, int):
                    totals[key] += value
    return totals


def summarize(payload: dict[str, Any], source: str) -> dict[str, Any]:
    buckets = payload.get("data", [])
    start_times = [bucket.get("start_time") for bucket in buckets if bucket.get("start_time")]
    end_times = [bucket.get("end_time") for bucket in buckets if bucket.get("end_time")]
    summary: dict[str, Any] = {
        "observed_at": utc_label(int(time.time())),
        "source": source,
        "bucket_count": len(buckets),
        "start": utc_label(min(start_times)) if start_times else None,
        "end": utc_label(max(end_times)) if end_times else None,
        "has_more": payload.get("has_more", False),
    }
    if source == "costs":
        summary["total_usd"] = round(response_cost_total(payload), 6)
    else:
        summary.update(response_usage_totals(payload))
    return summary


def cost_delta_flag(delta: float | None, args: argparse.Namespace) -> str | None:
    if delta is None:
        return None
    if delta >= args.late_threshold_usd:
        return "late"
    if delta >= args.medium_threshold_usd:
        return "medium"
    if delta >= args.early_threshold_usd:
        return "early"
    if delta > 0:
        return "nonzero"
    return None


def usage_delta_flag(delta: int | None) -> str | None:
    if delta is None:
        return None
    if delta > 0:
        return "nonzero"
    return None


def print_text(summary: dict[str, Any], delta: float | int | None = None, flag: str | None = None) -> None:
    parts = [
        f"observed_at={summary['observed_at']}",
        f"source={summary['source']}",
    ]
    if summary["source"] == "costs":
        parts.append(f"total_usd=${summary['total_usd']:.6f}")
    else:
        parts.extend(
            [
                f"requests={summary['num_model_requests']}",
                f"input_tokens={summary['input_tokens']}",
                f"output_tokens={summary['output_tokens']}",
                f"cached_input_tokens={summary['input_cached_tokens']}",
            ]
        )
    parts.extend(
        [
            f"window={summary.get('start')}..{summary.get('end')}",
            f"buckets={summary['bucket_count']}",
        ]
    )
    if delta is not None and summary["source"] == "costs":
        parts.append(f"interval_delta_usd=${float(delta):.6f}")
    elif delta is not None:
        parts.append(f"interval_requests_delta={delta}")
    if flag:
        parts.append(f"interval_flag={flag}")
    if summary.get("has_more"):
        parts.append("has_more=true")
    print(" ".join(parts), flush=True)


def emit(
    summary: dict[str, Any],
    raw: dict[str, Any],
    as_json: bool,
    delta: float | int | None = None,
    flag: str | None = None,
) -> None:
    if as_json:
        output = {"summary": summary, "interval_delta": delta, "interval_flag": flag, "raw": raw}
        print(json.dumps(output, indent=2, sort_keys=True), flush=True)
    else:
        print_text(summary, delta, flag)


def primary_value(summary: dict[str, Any]) -> float | int:
    if summary["source"] == "costs":
        return float(summary["total_usd"])
    return int(summary["num_model_requests"])


def run_once(args: argparse.Namespace) -> int:
    payload = fetch_payload(args)
    emit(summarize(payload, args.source), payload, args.json)
    return 0


def run_watch(args: argparse.Namespace) -> int:
    if args.interval < 120 and not args.allow_fast_polling:
        raise SystemExit("refusing to poll faster than 120 seconds without --allow-fast-polling")
    if not args.start_time:
        args.start_time = int(time.time()) - bucket_seconds(args)
    previous_value: float | int | None = None
    poll_count = 0
    while True:
        payload = fetch_payload(args)
        summary = summarize(payload, args.source)
        current_value = primary_value(summary)
        if previous_value is None:
            delta: float | int | None = None
        elif args.source == "costs":
            delta = round(float(current_value) - float(previous_value), 6)
        else:
            delta = int(current_value) - int(previous_value)
        flag = cost_delta_flag(delta if isinstance(delta, float) else None, args)
        if args.source == "usage-completions":
            flag = usage_delta_flag(delta if isinstance(delta, int) else None)
        emit(summary, payload, args.json, delta, flag)
        if flag and not args.continue_after_flag:
            print(
                f"interval flag {flag} requires user approval before additional OpenAI API calls",
                file=sys.stderr,
            )
            return 2
        if args.source == "costs" and args.stop_threshold_usd is not None and isinstance(delta, float):
            if delta >= args.stop_threshold_usd:
                print(
                    f"interval delta ${delta:.6f} reached stop threshold ${args.stop_threshold_usd:.6f}",
                    file=sys.stderr,
                )
                return 2
        previous_value = current_value
        poll_count += 1
        if args.max_polls and poll_count >= args.max_polls:
            return 0
        time.sleep(args.interval)


def main() -> int:
    args = parse_args()
    validate_args(args)
    if args.watch:
        return run_watch(args)
    return run_once(args)


if __name__ == "__main__":
    raise SystemExit(main())

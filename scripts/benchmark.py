"""Benchmark the autopilot system by running multiple test workflows."""

import asyncio
import time
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.services.workflow_service import WorkflowService


BENCHMARK_TASKS = [
    ("Email Notification", "Send a test email notification to admin@example.com about system maintenance scheduled for this weekend."),
    ("Data Query", "Query the workflow database for all completed workflows from the last 7 days and summarize the results."),
    ("Document Generation", "Generate a brief performance report document in markdown format summarizing Q4 metrics."),
]


async def run_benchmark():
    service = WorkflowService()
    print("=" * 60)
    print("Enterprise Autopilot Agent - Benchmark Suite")
    print("=" * 60)
    print()

    results = []

    for name, task in BENCHMARK_TASKS:
        print(f"Test: {name}")
        print(f"Task: {task[:80]}...")
        print("-" * 40)

        wf = await service.create_workflow(name=name, task=task, created_by="benchmark", tags=["benchmark"])
        print(f"Workflow ID: {wf.id}")

        start = time.time()
        final_event = None
        async for event in service.run_workflow(wf.id):
            if event.get("type") in ("workflow_completed", "workflow_failed"):
                final_event = event

        elapsed = time.time() - start

        if final_event and final_event.get("type") == "workflow_completed":
            tokens = final_event.get("total_tokens", 0)
            print(f"Status: COMPLETED")
            print(f"Time: {elapsed:.2f}s")
            print(f"Tokens: {tokens}")
            results.append({"name": name, "status": "completed", "time": elapsed, "tokens": tokens})
        else:
            error = final_event.get("error", "unknown") if final_event else "no result"
            print(f"Status: FAILED - {error}")
            results.append({"name": name, "status": "failed", "time": elapsed, "tokens": 0})

        print()

    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    completed = [r for r in results if r["status"] == "completed"]
    if completed:
        avg_time = sum(r["time"] for r in completed) / len(completed)
        avg_tokens = sum(r["tokens"] for r in completed) / len(completed)
        print(f"Completed: {len(completed)}/{len(results)}")
        print(f"Avg Time: {avg_time:.2f}s")
        print(f"Avg Tokens: {avg_tokens:.0f}")
    else:
        print("No benchmarks completed successfully.")


if __name__ == "__main__":
    asyncio.run(run_benchmark())

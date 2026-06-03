"""Seed sample workflow data for demonstration and testing purposes."""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.services.workflow_service import WorkflowService


SAMPLE_TASKS = [
    ("Quarterly Review", "Send a Q4 business performance review email to all department heads with attached report and schedule a follow-up meeting for next week."),
    ("Customer Onboarding", "Process the new customer onboarding request: send welcome email, create CRM contact, schedule onboarding call, and generate account setup document."),
    ("Code Review Pipeline", "Analyze the latest pull request for security vulnerabilities, check code style compliance, suggest fixes, and notify the development team."),
    ("Data Analysis Report", "Query the sales database for last month's performance metrics, generate a comprehensive analytics report with charts, and email it to the management team."),
    ("Incident Response", "Investigate the system alert about high CPU usage, analyze logs for root cause, suggest remediation steps, and escalate if critical."),
]


async def seed():
    service = WorkflowService()
    print(f"Seeding {len(SAMPLE_TASKS)} sample workflows...")

    for name, task in SAMPLE_TASKS:
        wf = await service.create_workflow(name=name, task=task, created_by="seed_script", tags=["sample", "demo"])
        print(f"  Created: {wf.id[:12]}... - {name}")

    print("\nSeed complete! Run the API server and use these workflow IDs to test.")


if __name__ == "__main__":
    asyncio.run(seed())

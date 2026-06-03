import logging
from typing import Dict, List
from datetime import datetime, timedelta

from app.db.models import Workflow
from app.db.session import SessionLocal

logger = logging.getLogger(__name__)


class AnalyticsService:
    def get_dashboard_stats(self) -> Dict:
        session = SessionLocal()
        try:
            workflows = session.query(Workflow).all()
            now = datetime.utcnow()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

            total = len(workflows)
            today = sum(1 for w in workflows if w.created_at and w.created_at >= today_start)
            completed = sum(1 for w in workflows if w.status == "completed")
            failed = sum(1 for w in workflows if w.status == "failed")
            running = sum(1 for w in workflows if w.status == "running")

            total_tokens = sum(w.total_tokens_used or 0 for w in workflows)
            today_tokens = sum(w.total_tokens_used or 0 for w in workflows if w.created_at and w.created_at >= today_start)

            return {
                "total_workflows": total,
                "workflows_today": today,
                "completed": completed,
                "failed": failed,
                "running": running,
                "success_rate": round(completed / max(total, 1) * 100, 1),
                "total_tokens_used": total_tokens,
                "tokens_today": today_tokens,
                "avg_tokens_per_workflow": round(total_tokens / max(total, 1)),
                "human_interventions": sum(w.human_intervention_count or 0 for w in workflows),
            }
        finally:
            session.close()

    def get_workflow_timeline(self, days: int = 7) -> List[Dict]:
        session = SessionLocal()
        try:
            cutoff = datetime.utcnow() - timedelta(days=days)
            workflows = session.query(Workflow).filter(Workflow.created_at >= cutoff).order_by(Workflow.created_at).all()

            daily = {}
            for w in workflows:
                day = w.created_at.strftime("%Y-%m-%d") if w.created_at else "unknown"
                if day not in daily:
                    daily[day] = {"date": day, "total": 0, "completed": 0, "failed": 0, "tokens": 0}
                daily[day]["total"] += 1
                if w.status == "completed":
                    daily[day]["completed"] += 1
                elif w.status == "failed":
                    daily[day]["failed"] += 1
                daily[day]["tokens"] += w.total_tokens_used or 0

            return sorted(daily.values(), key=lambda x: x["date"])
        finally:
            session.close()


analytics_service = AnalyticsService()

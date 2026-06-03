import re
from typing import Dict, Any, List, Optional
from datetime import datetime


class InputValidator:
    @staticmethod
    def validate_email(email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_url(url: str) -> bool:
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return bool(re.match(pattern, url))

    @staticmethod
    def sanitize_task_input(task: str) -> str:
        return task.strip()[:2000]

    @staticmethod
    def validate_workflow_name(name: str) -> bool:
        return bool(name) and len(name) <= 255


class ResponseFormatter:
    @staticmethod
    def success(data: Any, message: str = "Success") -> Dict:
        return {
            "status": "success",
            "message": message,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
        }

    @staticmethod
    def error(message: str, code: str = "ERROR", details: Optional[Any] = None) -> Dict:
        return {
            "status": "error",
            "error": {
                "code": code,
                "message": message,
                "details": details,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

    @staticmethod
    def paginated(data: List, total: int, limit: int, offset: int) -> Dict:
        return {
            "status": "success",
            "data": data,
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

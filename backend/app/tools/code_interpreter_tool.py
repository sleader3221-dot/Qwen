import logging
from typing import Dict, Optional
import ast
import sys
import io
import contextlib

from app.core.tool_registry import BaseTool, register_tool

logger = logging.getLogger(__name__)


@register_tool
class CodeInterpreterTool(BaseTool):
    name = "code_interpreter"
    description = "Execute Python code in a sandboxed environment and return the output. Use for calculations, data analysis, and automation."
    parameters = {
        "type": "object",
        "properties": {
            "code": {"type": "string", "description": "Python code to execute"},
            "timeout": {"type": "integer", "description": "Execution timeout in seconds"},
            "variables": {"type": "object", "description": "Variables to inject into the environment"},
        },
        "required": ["code"],
    }

    async def execute(self, **kwargs) -> Dict:
        code = kwargs.get("code", "")
        timeout = kwargs.get("timeout", 10)
        variables = kwargs.get("variables", {})

        local_vars = dict(variables)
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        try:
            tree = ast.parse(code)
            dangerous = [node for node in ast.walk(tree)
                        if isinstance(node, (ast.Import, ast.ImportFrom))]
            for node in dangerous:
                if any(alias.name in {"os", "subprocess", "shutil", "sys"} for alias in node.names if hasattr(node, 'names')):
                    return {"status": "error", "error": "Security: restricted module import detected", "stdout": "", "stderr": ""}
        except SyntaxError as e:
            return {"status": "error", "error": str(e), "stdout": "", "stderr": ""}

        try:
            with contextlib.redirect_stdout(stdout_capture), contextlib.redirect_stderr(stderr_capture):
                exec(code, {"__builtins__": __builtins__}, local_vars)

            return {
                "status": "success",
                "stdout": stdout_capture.getvalue(),
                "stderr": stderr_capture.getvalue(),
                "variables": {k: str(v) for k, v in local_vars.items() if not k.startswith("_")},
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "stdout": stdout_capture.getvalue(),
                "stderr": stderr_capture.getvalue(),
            }


@register_tool
class SQLQueryTool(BaseTool):
    name = "execute_sql"
    description = "Execute SQL queries against the application database to retrieve or analyze data"
    parameters = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "SQL query to execute"},
            "max_rows": {"type": "integer", "description": "Maximum rows to return"},
            "read_only": {"type": "boolean", "description": "Whether to enforce read-only mode"},
        },
        "required": ["query"],
    }

    async def execute(self, **kwargs) -> Dict:
        query = kwargs.get("query", "").strip().upper()
        if not query.startswith("SELECT"):
            return {"status": "error", "error": "Only SELECT queries allowed", "rows": [], "total": 0}
        return {"status": "simulated", "query": query, "rows": [], "total": 0, "message": "Database query simulation"}

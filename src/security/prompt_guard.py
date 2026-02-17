import re
from dataclasses import dataclass

@dataclass
class GuardResult:
    allowed: bool
    reason: str | None = None

PATTERNS = [
    (re.compile(r"ignore (all|any|the) previous instructions", re.I), "instruction_override"),
    (re.compile(r"(reveal|show|print).*(secret|api key|password|token)", re.I), "secret_exfiltration"),
    (re.compile(r"(disable|bypass|ignore).*(security|policy|guardrail|permission)", re.I), "policy_bypass"),
    (re.compile(r"(run|execute).*(shell|bash|powershell|cmd)", re.I), "unrestricted_shell"),
    (re.compile(r"system prompt", re.I), "system_prompt_extraction"),
]


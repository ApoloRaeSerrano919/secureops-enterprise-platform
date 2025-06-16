import json
from pathlib import Path
from src.security.prompt_guard import inspect_prompt
from src.tools.policy import evaluate_tool_policy

def main():
    prompt_cases = json.loads(Path("evals/prompt_injection_cases.json").read_text())
    tool_cases = json.loads(Path("evals/tool_policy_cases.json").read_text())

    prompt_correct = 0
    for case in prompt_cases:
        blocked = not inspect_prompt(case["prompt"]).allowed
        if blocked == case["should_block"]:
            prompt_correct += 1

    tool_correct = 0
    unsafe_allowed = 0

    for case in tool_cases:
        result = evaluate_tool_policy(case["role"], case["tool"])
        allowed = bool(result.get("allowed"))
        if allowed == case["allowed"]:
            tool_correct += 1

        if case["allowed"] is False and allowed is True:
            unsafe_allowed += 1

    metrics = {
        "prompt_security_accuracy": prompt_correct / len(prompt_cases),
        "tool_policy_accuracy": tool_correct / len(tool_cases),
        "unsafe_tool_call_rate": unsafe_allowed / len(tool_cases),
    }

    print(json.dumps(metrics, indent=2))

if __name__ == "__main__":
    main()

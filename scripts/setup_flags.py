"""
Creates the wiser-debt project, environments, and feature flags in LaunchDarkly.

Requires LAUNCHDARKLY_ACCESS_TOKEN in .env (or environment).
Run: python scripts/setup_flags.py
"""

import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.environ.get("LAUNCHDARKLY_ACCESS_TOKEN", "")
BASE_URL = "https://app.launchdarkly.com/api/v2"
PROJECT_KEY = "wiser-debt"

HEADERS = {
    "Authorization": ACCESS_TOKEN,
    "Content-Type": "application/json",
}

PATCH_HEADERS = {
    "Authorization": ACCESS_TOKEN,
    "Content-Type": "application/json; domain-model=launchdarkly.semanticpatch",
}

FLAGS = [
    {
        "key": "legacy-debt-summary",
        "name": "Legacy Debt Summary",
        "description": "Gates CreditCardAgent. Launched to 100% in production over 60 days ago — primary cleanup target.",
    },
    {
        "key": "student-loan-details",
        "name": "Student Loan Details",
        "description": "Gates StudentLoanAgent. Currently at 50% rollout in production — still rolling out, not ready to remove.",
    },
    {
        "key": "new-repayment-dashboard",
        "name": "New Repayment Dashboard",
        "description": "Gates MedicalDebtAgent. 10% rollout in production, 100% in staging — active mid-rollout flag.",
    },
    {
        "key": "exp-priority-sort",
        "name": "Experiment: Priority Sort",
        "description": "Controls sort order in /debts endpoint. Targeting OFF in all environments — abandoned experiment.",
    },
    {
        "key": "payment-killswitch",
        "name": "Payment Killswitch",
        "description": "Gates TaxDebtAgent payment processing. Targeting ON in all environments — permanent operational flag.",
    },
]


def create_project():
    print(f"Creating project '{PROJECT_KEY}'...")
    resp = requests.post(
        f"{BASE_URL}/projects",
        headers=HEADERS,
        json={
            "key": PROJECT_KEY,
            "name": "Wiser Debt",
            "environments": [
                {"key": "staging", "name": "Staging", "color": "F5A623"},
                {"key": "production", "name": "Production", "color": "417505"},
            ],
        },
    )
    if resp.status_code == 201:
        print("  Project created.")
    elif resp.status_code == 409:
        print("  Project already exists, continuing.")
    else:
        print(f"  Error creating project: {resp.status_code} {resp.text}")
        sys.exit(1)


def create_flag(flag):
    print(f"Creating flag '{flag['key']}'...")
    resp = requests.post(
        f"{BASE_URL}/flags/{PROJECT_KEY}",
        headers=HEADERS,
        json={
            "key": flag["key"],
            "name": flag["name"],
            "description": flag["description"],
            "kind": "boolean",
            "variations": [
                {"value": True, "name": "On"},
                {"value": False, "name": "Off"},
            ],
        },
    )
    if resp.status_code == 201:
        print(f"  Flag '{flag['key']}' created.")
    elif resp.status_code == 409:
        print(f"  Flag '{flag['key']}' already exists.")
    else:
        print(f"  Error: {resp.status_code} {resp.text}")


def configure_flag_targeting(flag_key, env_key, on, fallthrough_variation=None, rules=None):
    """Configure targeting for a flag in a specific environment."""
    instructions = []

    if on:
        instructions.append({"kind": "turnFlagOn"})
    else:
        instructions.append({"kind": "turnFlagOff"})

    if fallthrough_variation is not None:
        instructions.append({
            "kind": "updateFallthroughVariationOrRollout",
            "variationId": None,
        })

    if rules:
        instructions = [{"kind": "turnFlagOn" if on else "turnFlagOff"}]

    resp = requests.patch(
        f"{BASE_URL}/flags/{PROJECT_KEY}/{flag_key}",
        headers=PATCH_HEADERS,
        json={
            "environmentKey": env_key,
            "instructions": instructions,
        },
    )
    if resp.status_code == 200:
        print(f"  Configured '{flag_key}' in {env_key}.")
    else:
        print(f"  Error configuring '{flag_key}' in {env_key}: {resp.status_code} {resp.text}")


def configure_rollout(flag_key, env_key, percentage):
    """Set a percentage rollout for the true variation."""
    resp = requests.patch(
        f"{BASE_URL}/flags/{PROJECT_KEY}/{flag_key}",
        headers=PATCH_HEADERS,
        json={
            "environmentKey": env_key,
            "instructions": [
                {"kind": "turnFlagOn"},
                {
                    "kind": "updateFallthroughVariationOrRollout",
                    "rolloutWeights": {
                        "on": percentage * 1000,
                        "off": (100 - percentage) * 1000,
                    },
                },
            ],
        },
    )
    if resp.status_code == 200:
        print(f"  Set {percentage}% rollout for '{flag_key}' in {env_key}.")
    else:
        print(f"  Error setting rollout for '{flag_key}' in {env_key}: {resp.status_code} {resp.text}")


def setup_all_flags():
    # legacy-debt-summary: Production 100% on, Staging 100% on
    configure_flag_targeting("legacy-debt-summary", "production", on=True)
    configure_flag_targeting("legacy-debt-summary", "staging", on=True)

    # student-loan-details: Production 50% rollout
    configure_rollout("student-loan-details", "production", 50)
    configure_flag_targeting("student-loan-details", "staging", on=True)

    # new-repayment-dashboard: Production 10%, Staging 100%
    configure_rollout("new-repayment-dashboard", "production", 10)
    configure_flag_targeting("new-repayment-dashboard", "staging", on=True)

    # exp-priority-sort: OFF in all environments
    configure_flag_targeting("exp-priority-sort", "production", on=False)
    configure_flag_targeting("exp-priority-sort", "staging", on=False)

    # payment-killswitch: ON in all environments
    configure_flag_targeting("payment-killswitch", "production", on=True)
    configure_flag_targeting("payment-killswitch", "staging", on=True)


def main():
    if not ACCESS_TOKEN:
        print("Error: LAUNCHDARKLY_ACCESS_TOKEN not set in .env or environment.")
        sys.exit(1)

    create_project()

    for flag in FLAGS:
        create_flag(flag)

    setup_all_flags()
    print("\nDone! All flags configured.")


if __name__ == "__main__":
    main()

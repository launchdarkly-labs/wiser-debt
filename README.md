# wiser-debt

A minimal debt tracking API with a multi-agent architecture, built as a demo for LaunchDarkly Agent Skills. A `CoordinatorAgent` receives requests and delegates to specialized debt agents, each gated by a LaunchDarkly feature flag. All agent responses are mocked — the flags are the point, not the app.

## Architecture

```
POST /summary
    └── CoordinatorAgent
            ├── CreditCardAgent      gated by legacy-debt-summary
            ├── StudentLoanAgent     gated by student-loan-details
            ├── MedicalDebtAgent     gated by new-repayment-dashboard
            └── TaxDebtAgent         always active, uses payment-killswitch

GET /debts
    └── CoordinatorAgent
            └── uses exp-priority-sort to determine sort order of results
```

The `CoordinatorAgent` checks each flag before instantiating the corresponding agent. If a flag is off, that agent is skipped and excluded from the response.

## Setup

1. Clone the repo and install dependencies:

```bash
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and fill in your keys:

```bash
cp .env.example .env
```

3. Run the setup script to create flags in LaunchDarkly:

```bash
python scripts/setup_flags.py
```

4. Install agent skills:

```bash
npx skills add launchdarkly/agent-skills
```

5. Start the server:

```bash
flask --app app run
```

## Part 1: Create and target a flag

Use the LaunchDarkly agent skills to:

- Discover which flags exist in the `wiser-debt` project
- Check the targeting state of `new-repayment-dashboard` in production
- Update the rollout percentage for `new-repayment-dashboard` to 50%

## Part 2: Pay down flag debt

Use the LaunchDarkly agent skills to:

- Run flag discovery to identify stale flags
- Clean up `legacy-debt-summary` — it's been at 100% for over 60 days
- Remove the flag wrappers from code and simplify tests

## Flag reference

| Flag key | Type | State | Agent |
|---|---|---|---|
| `legacy-debt-summary` | boolean | Production: 100% on, stale 60+ days | `CreditCardAgent` |
| `student-loan-details` | boolean | Production: 50% rollout | `StudentLoanAgent` |
| `new-repayment-dashboard` | boolean | Production: 10%, Staging: 100% | `MedicalDebtAgent` |
| `exp-priority-sort` | boolean | OFF everywhere | Sort order in `/debts` |
| `payment-killswitch` | boolean | ON everywhere | `TaxDebtAgent` |

## Running tests

```bash
pytest
```

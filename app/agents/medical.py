class MedicalDebtAgent:
    def summarize(self):
        return {
            "type": "medical",
            "balance": 1800.00,
            "interest_rate": 0.0,
            "minimum_payment": 50.00,
            "projected_payoff_months": 36,
        }

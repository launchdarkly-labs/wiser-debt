class TaxDebtAgent:
    def summarize(self):
        return {
            "type": "tax",
            "balance": 5600.00,
            "interest_rate": 0.07,
            "minimum_payment": 200.00,
            "projected_payoff_months": 30,
        }

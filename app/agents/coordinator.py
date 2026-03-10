from app.agents.credit_card import CreditCardAgent
from app.agents.student_loan import StudentLoanAgent
from app.agents.medical import MedicalDebtAgent
from app.agents.tax import TaxDebtAgent


class CoordinatorAgent:
    def __init__(self, ld_client, context):
        self.ld_client = ld_client
        self.context = context

    def summarize(self):
        results = []

        # legacy-debt-summary: stale, launched to 100% — cleanup target
        if self.ld_client.variation("legacy-debt-summary", self.context, False):
            results.append(CreditCardAgent().summarize())

        # student-loan-details: mid-rollout at 50%
        if self.ld_client.variation("student-loan-details", self.context, False):
            results.append(StudentLoanAgent().summarize())

        # new-repayment-dashboard: mid-rollout at 10%
        if self.ld_client.variation("new-repayment-dashboard", self.context, False):
            results.append(MedicalDebtAgent().summarize())

        # payment-killswitch: permanent — TaxDebtAgent always runs if killswitch is on
        if self.ld_client.variation("payment-killswitch", self.context, True):
            results.append(TaxDebtAgent().summarize())

        return results

    def list_debts(self):
        debts = self.summarize()

        # exp-priority-sort: abandoned experiment — sort by balance descending
        if self.ld_client.variation("exp-priority-sort", self.context, False):
            debts.sort(key=lambda d: d["balance"], reverse=True)
        else:
            debts.sort(key=lambda d: d["type"])

        return debts

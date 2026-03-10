from unittest.mock import MagicMock
import pytest
from app.agents.coordinator import CoordinatorAgent


@pytest.fixture
def mock_context():
    return MagicMock()


@pytest.fixture
def mock_ld_client():
    return MagicMock()


def test_coordinator_includes_credit_card_when_legacy_summary_on(mock_ld_client, mock_context):
    mock_ld_client.variation.side_effect = lambda key, ctx, default: (
        True if key == "legacy-debt-summary" else default
    )
    agent = CoordinatorAgent(mock_ld_client, mock_context)
    result = agent.summarize()
    assert any(r["type"] == "credit_card" for r in result)


def test_coordinator_excludes_credit_card_when_legacy_summary_off(mock_ld_client, mock_context):
    mock_ld_client.variation.side_effect = lambda key, ctx, default: (
        False if key == "legacy-debt-summary" else default
    )
    agent = CoordinatorAgent(mock_ld_client, mock_context)
    result = agent.summarize()
    assert not any(r["type"] == "credit_card" for r in result)


def test_coordinator_includes_student_loan_when_flag_on(mock_ld_client, mock_context):
    mock_ld_client.variation.side_effect = lambda key, ctx, default: (
        True if key == "student-loan-details" else default
    )
    agent = CoordinatorAgent(mock_ld_client, mock_context)
    result = agent.summarize()
    assert any(r["type"] == "student_loan" for r in result)


def test_coordinator_excludes_student_loan_when_flag_off(mock_ld_client, mock_context):
    mock_ld_client.variation.side_effect = lambda key, ctx, default: (
        False if key == "student-loan-details" else default
    )
    agent = CoordinatorAgent(mock_ld_client, mock_context)
    result = agent.summarize()
    assert not any(r["type"] == "student_loan" for r in result)


def test_coordinator_includes_medical_when_repayment_dashboard_on(mock_ld_client, mock_context):
    mock_ld_client.variation.side_effect = lambda key, ctx, default: (
        True if key == "new-repayment-dashboard" else default
    )
    agent = CoordinatorAgent(mock_ld_client, mock_context)
    result = agent.summarize()
    assert any(r["type"] == "medical" for r in result)


def test_coordinator_excludes_medical_when_repayment_dashboard_off(mock_ld_client, mock_context):
    mock_ld_client.variation.side_effect = lambda key, ctx, default: (
        False if key == "new-repayment-dashboard" else default
    )
    agent = CoordinatorAgent(mock_ld_client, mock_context)
    result = agent.summarize()
    assert not any(r["type"] == "medical" for r in result)


def test_coordinator_includes_tax_when_killswitch_on(mock_ld_client, mock_context):
    mock_ld_client.variation.side_effect = lambda key, ctx, default: (
        True if key == "payment-killswitch" else default
    )
    agent = CoordinatorAgent(mock_ld_client, mock_context)
    result = agent.summarize()
    assert any(r["type"] == "tax" for r in result)


def test_coordinator_excludes_tax_when_killswitch_off(mock_ld_client, mock_context):
    mock_ld_client.variation.side_effect = lambda key, ctx, default: (
        False if key == "payment-killswitch" else default
    )
    agent = CoordinatorAgent(mock_ld_client, mock_context)
    result = agent.summarize()
    assert not any(r["type"] == "tax" for r in result)


def test_coordinator_all_flags_on(mock_ld_client, mock_context):
    mock_ld_client.variation.return_value = True
    agent = CoordinatorAgent(mock_ld_client, mock_context)
    result = agent.summarize()
    types = {r["type"] for r in result}
    assert types == {"credit_card", "student_loan", "medical", "tax"}


def test_coordinator_all_flags_off(mock_ld_client, mock_context):
    mock_ld_client.variation.return_value = False
    agent = CoordinatorAgent(mock_ld_client, mock_context)
    result = agent.summarize()
    assert result == []

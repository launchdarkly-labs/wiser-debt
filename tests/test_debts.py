from unittest.mock import MagicMock
import pytest
from app.agents.coordinator import CoordinatorAgent


@pytest.fixture
def mock_context():
    return MagicMock()


@pytest.fixture
def mock_ld_client():
    return MagicMock()


def test_list_debts_sorted_alphabetically_when_exp_sort_off(mock_ld_client, mock_context):
    mock_ld_client.variation.side_effect = lambda key, ctx, default: (
        False if key == "exp-priority-sort" else True
    )
    agent = CoordinatorAgent(mock_ld_client, mock_context)
    debts = agent.list_debts()
    types = [d["type"] for d in debts]
    assert types == sorted(types)


def test_list_debts_sorted_by_balance_when_exp_sort_on(mock_ld_client, mock_context):
    mock_ld_client.variation.side_effect = lambda key, ctx, default: True
    agent = CoordinatorAgent(mock_ld_client, mock_context)
    debts = agent.list_debts()
    balances = [d["balance"] for d in debts]
    assert balances == sorted(balances, reverse=True)


def test_list_debts_returns_empty_when_all_agent_flags_off(mock_ld_client, mock_context):
    mock_ld_client.variation.return_value = False
    agent = CoordinatorAgent(mock_ld_client, mock_context)
    debts = agent.list_debts()
    assert debts == []

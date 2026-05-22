import pytest

from src.simulation.decision import make_decision


def test_make_decision_allows_below_threshold():
    result = make_decision(probability=0.49, threshold=0.5)

    assert result.decision == "allow"
    assert result.probability == 0.49
    assert result.threshold == 0.5


def test_make_decision_blocks_at_threshold():
    result = make_decision(probability=0.5, threshold=0.5)

    assert result.decision == "block"


def test_make_decision_blocks_above_threshold():
    result = make_decision(probability=0.8, threshold=0.5)

    assert result.decision == "block"


def test_make_decision_rejects_invalid_probability():
    with pytest.raises(ValueError):
        make_decision(probability=1.5, threshold=0.5)


def test_make_decision_rejects_invalid_threshold():
    with pytest.raises(ValueError):
        make_decision(probability=0.5, threshold=-0.1)
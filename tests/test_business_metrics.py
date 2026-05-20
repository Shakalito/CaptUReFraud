from src.simulation.metrics import BusinessMetrics, CostConfig, business_metrics_to_dict


def test_cost_config_defaults():
    config = CostConfig()

    assert config.missed_fraud_cost == 1000.0
    assert config.blocked_legit_cost == 50.0


def test_business_metrics_to_dict():
    metrics = BusinessMetrics(
        total_transactions=100,
        total_frauds=10,
        detected_frauds=8,
        missed_frauds=2,
        blocked_legit_transactions=5,
        fraud_recall=0.8,
        estimated_fraud_loss=2000.0,
        estimated_blocking_cost=250.0,
        estimated_total_cost=2250.0,
    )

    result = business_metrics_to_dict(metrics)

    assert result["total_transactions"] == 100
    assert result["total_frauds"] == 10
    assert result["detected_frauds"] == 8
    assert result["missed_frauds"] == 2
    assert result["blocked_legit_transactions"] == 5
    assert result["fraud_recall"] == 0.8
    assert result["estimated_total_cost"] == 2250.0

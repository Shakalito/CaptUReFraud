from src.simulation.engine import SimulationConfig


def test_simulation_config_uses_default_threshold():
    config = SimulationConfig()

    assert config.threshold == 0.8


def test_simulation_config_accepts_custom_threshold():
    config = SimulationConfig(threshold=0.5)

    assert config.threshold == 0.5

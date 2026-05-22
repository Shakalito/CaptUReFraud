from src.simulation.feedback import build_feedback


def main() -> None:
    examples = [
        {"true_label": 1, "predicted_label": 1, "decision": "block"},
        {"true_label": 0, "predicted_label": 1, "decision": "block"},
        {"true_label": 0, "predicted_label": 0, "decision": "allow"},
        {"true_label": 1, "predicted_label": 0, "decision": "allow"},
    ]

    for example in examples:
        result = build_feedback(**example)

        print(
            f"true_label={example['true_label']} "
            f"predicted_label={example['predicted_label']} "
            f"decision={example['decision']} "
            f"outcome={result.prediction_outcome} "
            f"fraud_detected={result.fraud_correctly_detected} "
            f"fraud_missed={result.fraud_missed} "
            f"legit_blocked={result.legit_incorrectly_blocked}"
        )


if __name__ == "__main__":
    main()
from src.simulation.decision import make_decision


def main() -> None:
    probabilities = [0.12, 0.49, 0.5, 0.79, 0.8, 0.95]
    threshold = 0.8

    for probability in probabilities:
        result = make_decision(probability=probability, threshold=threshold)

        print(
            f"probability={result.probability:.2f} "
            f"threshold={result.threshold:.2f} "
            f"decision={result.decision}"
        )


if __name__ == "__main__":
    main()
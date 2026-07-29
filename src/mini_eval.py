import pandas as pd
from predict_mobilenet import predict_image, load_model


CSV_PATH = "data/labels/binary/combined/test.csv"
OUTPUT_PATH = "outputs/reports/full_eval_thresholds.csv"


def evaluate_threshold(df, threshold, model):
    total = 0
    correct = 0

    normal_total = 0
    normal_correct = 0

    risk_total = 0
    risk_correct = 0

    false_positive = 0
    false_negative = 0
    skipped = 0

    for _, row in df.iterrows():
        image_path = row["image_path"]
        actual = row["label"]

        result = predict_image(image_path, model=model)

        if result.get("error") is True or "risk_percent" not in result:
            skipped += 1
            print(f"[SKIPPED] {image_path}")
            print("Reason:", result.get("message", "risk_percent missing"))
            continue

        risk_prob = result["risk_percent"] / 100
        predicted = "risk" if risk_prob >= threshold else "normal"

        total += 1

        if predicted == actual:
            correct += 1

        if actual == "normal":
            normal_total += 1

            if predicted == "normal":
                normal_correct += 1
            else:
                false_positive += 1

        elif actual == "risk":
            risk_total += 1

            if predicted == "risk":
                risk_correct += 1
            else:
                false_negative += 1

    accuracy = correct / total if total else 0
    normal_recall = normal_correct / normal_total if normal_total else 0
    risk_recall = risk_correct / risk_total if risk_total else 0

    return {
        "threshold": threshold,
        "accuracy": round(accuracy * 100, 2),
        "normal_recall": round(normal_recall * 100, 2),
        "risk_recall": round(risk_recall * 100, 2),
        "false_positive": false_positive,
        "false_negative_risk_missed": false_negative,
        "risk_missed": false_negative,
        "skipped_bad_images": skipped,
        "total_evaluated": total
    }


def main():
    df = pd.read_csv(CSV_PATH)

    print("\nAROVA FULL TEST EVALUATION")
    print("=" * 80)
    print("Total test rows:", len(df))
    print(df["label"].value_counts())
    print("=" * 80)

    print("\nLoading model once...")
    model = load_model()
    print("Model loaded successfully.")

    thresholds = [0.30, 0.35, 0.40, 0.45, 0.50]
    results = []

    for threshold in thresholds:
        print(f"\nEvaluating threshold: {threshold}")

        metrics = evaluate_threshold(
            df=df,
            threshold=threshold,
            model=model
        )

        results.append(metrics)

        print("Accuracy:", metrics["accuracy"])
        print("Normal Recall:", metrics["normal_recall"])
        print("Risk Recall:", metrics["risk_recall"])
        print("False Positive:", metrics["false_positive"])
        print("Risk Missed:", metrics["risk_missed"])
        print("Skipped Bad Images:", metrics["skipped_bad_images"])
        print("Total Evaluated:", metrics["total_evaluated"])

    print("\nSUMMARY TABLE")
    print("=" * 80)

    result_df = pd.DataFrame(results)
    print(result_df)

    result_df.to_csv(OUTPUT_PATH, index=False)
    print(f"\nSaved: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
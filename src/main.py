import csv
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from extraction_pipeline import extract_cause

OUTPUT_FIELDS = ["confirmed_cause", "probable_cause", "confidence", "reasoning"]


def load_reports(file_path: Path) -> list[dict]:
    with open(file_path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    data_file = Path(__file__).parent.parent / "data" / "sample_reports.csv"

    if len(sys.argv) > 1:
        data_file = Path(sys.argv[1])

    if not data_file.exists():
        print(f"Error: file not found: {data_file}")
        sys.exit(1)

    reports = load_reports(data_file)
    print(f"Processing {len(reports)} reports...\n")

    results = []
    for i, report in enumerate(reports, 1):
        sys.stdout.write(f"[{i}/{len(reports)}] {report['report_id']}... ")
        sys.stdout.flush()
        extraction = extract_cause(report["report_text"])
        row = {**report, **extraction}
        results.append(row)

        confidence = extraction["confidence"]
        if confidence == "confirmed":
            print(f"confirmed cause: {extraction['confirmed_cause']}")
        elif confidence == "probable":
            print(f"probable cause: {extraction['probable_cause']} (not confirmed)")
        else:
            print("cause not determinable")

    output_file = "results.csv"
    fieldnames = list(reports[0].keys()) + OUTPUT_FIELDS
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nResults saved to: {output_file}")
    confirmed = sum(1 for r in results if r["confidence"] == "confirmed")
    probable = sum(1 for r in results if r["confidence"] == "probable")
    not_det = sum(1 for r in results if r["confidence"] == "not_determinable")
    print(f"Confirmed: {confirmed} | Probable: {probable} | Not determinable: {not_det}")


if __name__ == "__main__":
    main()

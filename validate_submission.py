"""
Validation script for verifying output/ submission folder.
Checks that all 50 JSON files exist, conform 100% to FinalCaseOutput schema,
and satisfy all task constraints.
"""

import os
import json
import sys
from src.contracts import FinalCaseOutput
from src.agents.verifier_agent import VerifierAgent


def validate_submission():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, "output")
    verifier = VerifierAgent()

    if not os.path.exists(output_dir):
        print(f"ERROR: output directory does not exist at {output_dir}")
        sys.exit(1)

    expected_files = [f"EC_{i:03d}.json" for i in range(1, 51)]
    missing_files = []
    invalid_files = []

    print(f"Validating 50 JSON files in {output_dir}...\n")

    for filename in expected_files:
        filepath = os.path.join(output_dir, filename)
        if not os.path.exists(filepath):
            missing_files.append(filename)
            continue

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            output_model = FinalCaseOutput(**data)
            verifier_result = verifier.verify(output_model)

            if not verifier_result.is_valid:
                invalid_files.append((filename, verifier_result.validation_errors))
        except Exception as e:
            invalid_files.append((filename, [str(e)]))

    if missing_files:
        print(f"FAILED: Missing {len(missing_files)} output files:")
        for f in missing_files:
            print(f"  - {f}")
    
    if invalid_files:
        print(f"FAILED: {len(invalid_files)} invalid files:")
        for fname, errs in invalid_files:
            print(f"  - {fname}: {errs}")

    if not missing_files and not invalid_files:
        print("SUCCESS! All 50 output files are present, valid, and fully compliant!")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    validate_submission()

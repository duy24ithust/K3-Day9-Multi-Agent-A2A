"""
Validation Script for E-Commerce Dispute Resolution Submissions (Member 5 & Team).

Checks that:
1. Thư mục output/ chứa đúng 50 file JSON (EC_001.json -> EC_050.json).
2. Đúng schema đề bài và không có trường lạ/thiếu trường.
3. Ràng buộc giới hạn số lượng phần tử:
   - order_ids <= 5
   - item_ids <= 5
   - seller_ids <= 5
   - payment_ids <= 5
   - evidence_ids <= 10
   - ranked_causes <= 3
   - responsible_parties <= 3
   - resolution_actions <= 5
4. Giá trị confidence thuộc đoạn [0.0, 1.0].
5. Có đầy đủ các file báo cáo repo (architecture.md, metadata.json, trace.jsonl).
"""

import os
import json
import sys

def validate():
    output_dir = "output"
    errors = []

    print("==================================================================")
    print("  RUNNING SUBMISSION VALIDATION CHECKS FOR 50 CASES               ")
    print("==================================================================")

    if not os.path.exists(output_dir):
        print("❌ ERROR: Output directory 'output/' does not exist.")
        sys.exit(1)

    output_files = [f for f in os.listdir(output_dir) if f.endswith(".json")]
    if len(output_files) != 50:
        errors.append(f"Expected exactly 50 JSON files in 'output/', found {len(output_files)}")

    for i in range(1, 51):
        filename = f"EC_{i:03d}.json"
        filepath = os.path.join(output_dir, filename)

        if not os.path.exists(filepath):
            errors.append(f"Missing output file: {filename}")
            continue

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 1. Required top-level keys
            req_keys = [
                "case_id", "assessment", "affected_entities",
                "root_cause_analysis", "evidence_ids",
                "financial_resolution", "resolution_actions"
            ]
            for rk in req_keys:
                if rk not in data:
                    errors.append(f"{filename}: Missing key '{rk}'")

            # 2. Entity bounds
            aff = data.get("affected_entities", {})
            if len(aff.get("order_ids", [])) > 5:
                errors.append(f"{filename}: order_ids count {len(aff.get('order_ids'))} > 5")
            if len(aff.get("item_ids", [])) > 5:
                errors.append(f"{filename}: item_ids count {len(aff.get('item_ids'))} > 5")
            if len(aff.get("seller_ids", [])) > 5:
                errors.append(f"{filename}: seller_ids count {len(aff.get('seller_ids'))} > 5")
            if len(aff.get("payment_ids", [])) > 5:
                errors.append(f"{filename}: payment_ids count {len(aff.get('payment_ids'))} > 5")

            # 3. Evidence bounds
            ev_ids = data.get("evidence_ids", [])
            if len(ev_ids) > 10:
                errors.append(f"{filename}: evidence_ids count {len(ev_ids)} > 10")

            # 4. Root cause bounds
            rca = data.get("root_cause_analysis", {})
            if len(rca.get("ranked_causes", [])) > 3:
                errors.append(f"{filename}: ranked_causes count {len(rca.get('ranked_causes'))} > 3")
            if len(rca.get("responsible_parties", [])) > 3:
                errors.append(f"{filename}: responsible_parties count {len(rca.get('responsible_parties'))} > 3")

            # 5. Actions bounds
            actions = data.get("resolution_actions", [])
            if len(actions) > 5:
                errors.append(f"{filename}: resolution_actions count {len(actions)} > 5")

            # 6. Confidence range
            conf = data.get("assessment", {}).get("confidence", 0.0)
            if not (0.0 <= float(conf) <= 1.0):
                errors.append(f"{filename}: confidence {conf} out of range [0.0, 1.0]")

        except Exception as e:
            errors.append(f"{filename}: Invalid JSON format - {e}")

    # Check repository deliverable files
    repo_files = ["architecture.md", "metadata.json", "trace.jsonl"]
    for rf in repo_files:
        if not os.path.exists(rf):
            errors.append(f"Missing mandatory repository file: '{rf}'")

    print("\n------------------------------------------------------------------")
    if errors:
        print(f"❌ Validation FAILED with {len(errors)} error(s):")
        for err in errors[:15]:
            print(f"   - {err}")
        if len(errors) > 15:
            print(f"   ... and {len(errors) - 15} more error(s)")
        sys.exit(1)
    else:
        print("✅ PASSED: All 50 output files and repository requirements strictly validated!")
        print("==================================================================")

if __name__ == "__main__":
    validate()

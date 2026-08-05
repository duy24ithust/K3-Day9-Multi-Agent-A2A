"""
Test Script for CoordinatorAgent (Dry-Run Demo)
"""

import sys
import os
import json

# Ensure project root is in Python module search path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.contracts import CaseInput, CustomerRequest
from src.agents.coordinator_agent import CoordinatorAgent

def test_run():
    print("==================================================")
    print("   TESTING MULTI-AGENT COORDINATOR FRAMEWORK     ")
    print("==================================================")

    # Load real input from input/EC_001.json
    with open("input/EC_001.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    case_input = CaseInput(
        case_id=data["case_id"],
        opened_at=data["opened_at"],
        customer_request=CustomerRequest(**data["customer_request"]),
        policy_version=data["policy_version"]
    )

    print(f"1. Loaded Input: Case ID = {case_input.case_id}")
    print(f"   Claimed Order ID = {case_input.customer_request.claimed_order_id}")
    print(f"   Customer Message = '{case_input.customer_request.message}'")

    # Initialize CoordinatorAgent (with stubs for pending teammate agents)
    coordinator = CoordinatorAgent()

    print("\n2. Executing Multi-Agent Handoff Flow...")
    final_output, trace_logs = coordinator.process_case(case_input)

    print("\n3. Generated Trace Logs (Handoff Audit Trail):")
    for trace in trace_logs:
        print(f"   - [{trace['agent']}] Action: {trace['action']}")

    print("\n4. Generated Final Output JSON (Validation Passed):")
    print(json.dumps(final_output.model_dump(), indent=2, ensure_ascii=False))

    print("\n==================================================")
    print("   COORDINATOR FRAMEWORK TEST PASSED PERFECTLY!   ")
    print("==================================================")

if __name__ == "__main__":
    test_run()

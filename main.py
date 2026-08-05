"""
Main runner for Multi-Agent E-Commerce Dispute Resolution system.
Processes 50 cases from input/ directory, outputs JSON results to output/ directory,
and records execution trace in trace.jsonl.
"""

import os
import json
import glob
from typing import List, Dict, Any

from src.contracts import CaseInput
from src.repositories.order_repository import OrderRepository
from src.repositories.payment_repository import PaymentRepository
from src.agents.order_seller_agent import OrderSellerAgent
from src.agents.payment_agent import PaymentAgent
from src.agents.policy_agent import PolicyAgent
from src.agents.verifier_agent import VerifierAgent
from src.agents.coordinator_agent import CoordinatorAgent


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(base_dir, "input")
    output_dir = os.path.join(base_dir, "output")
    trace_file = os.path.join(base_dir, "trace.jsonl")

    os.makedirs(output_dir, exist_ok=True)

    print("Initializing Data Repositories...")
    order_repo = OrderRepository()
    payment_repo = PaymentRepository()

    print("Initializing Multi-Agent System...")
    order_seller_agent = OrderSellerAgent(repository=order_repo)
    payment_agent = PaymentAgent(repository=payment_repo)
    policy_agent = PolicyAgent()
    verifier_agent = VerifierAgent()

    coordinator = CoordinatorAgent(
        order_seller_agent=order_seller_agent,
        payment_agent=payment_agent,
        policy_agent=policy_agent,
        verifier_agent=verifier_agent
    )

    input_files = sorted(glob.glob(os.path.join(input_dir, "EC_*.json")))
    print(f"Found {len(input_files)} cases in {input_dir}")

    all_trace_logs: List[Dict[str, Any]] = []

    for file_path in input_files:
        filename = os.path.basename(file_path)
        with open(file_path, "r", encoding="utf-8") as f:
            case_data = json.load(f)

        case_input = CaseInput(**case_data)
        final_output, trace_logs = coordinator.process_case(case_input)

        # Output JSON writing
        output_file_path = os.path.join(output_dir, filename)
        with open(output_file_path, "w", encoding="utf-8") as f:
            f.write(final_output.model_dump_json(indent=2))

        all_trace_logs.extend(trace_logs)

    # Write trace.jsonl
    with open(trace_file, "w", encoding="utf-8") as f:
        for log in all_trace_logs:
            f.write(json.dumps(log, ensure_ascii=False) + "\n")

    print(f"Successfully processed {len(input_files)} cases!")
    print(f"Output files saved to: {output_dir}")
    print(f"Trace logs written to: {trace_file}")


if __name__ == "__main__":
    main()

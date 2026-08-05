# Phân công công việc cho 5 thành viên

## 1. Tổng quan

| Thành viên | Vai trò | Công việc chính | Kết quả bàn giao |
| --- | --- | --- | --- |
| Người 1 | Coordinator & Integration | Thiết kế workflow multi-agent, chạy 50 case và tổng hợp output | Coordinator, runner và 50 JSON |
| Người 2 | Order & Seller Agent | Tra cứu order, item, seller và kiểm tra seller bàn giao trễ | Module order/seller |
| Người 3 | Payment Agent | Tính và đối soát item, freight, payment và split payment | Module payment |
| Người 4 | Delivery & Policy Agent | Xác định giao trễ, trách nhiệm, refund, action và root cause | Module delivery/policy |
| Người 5 | Verifier, Testing & Documentation | Validate schema/evidence, kiểm thử, tạo trace, metadata và tài liệu | Validator, tests và tài liệu |

## 2. Người 1 — Coordinator và tích hợp

### Công việc

- Định nghĩa contract trao đổi dữ liệu giữa các agent.
- Đọc các input từ `EC_001.json` đến `EC_050.json`.
- Lấy `claimed_order_id` và giao nhiệm vụ cho các agent.
- Nhận kết quả từ Order/Seller, Payment, Delivery và Policy Agent.
- Tổng hợp kết quả theo output schema của đề bài.
- Ghi kết quả tương ứng vào thư mục `output/`.
- Xử lý lỗi để một case lỗi không làm dừng toàn bộ pipeline.
- Tích hợp code của các thành viên còn lại.
- Chạy và kiểm tra pipeline end-to-end cho 50 case.

### File dự kiến phụ trách

```text
src/coordinator.py
src/main.py
src/contracts.py
```

### Kết quả bàn giao

- Một lệnh chạy được toàn bộ 50 case.
- Đủ 50 output JSON đúng tên.
- Có luồng giao việc và handoff thực sự giữa các agent.

## 3. Người 2 — Order & Seller Agent

### Công việc

- Đọc và tra cứu các file:
  - `olist_orders_dataset.csv`
  - `olist_order_items_dataset.csv`
  - `olist_sellers_dataset.csv`
- Kiểm tra `order_status`.
- Kiểm tra ngày carrier nhận hàng và `shipping_limit_date` của từng item.
- Xác định seller bàn giao hàng trễ.
- Tính `item_total_brl` và `freight_total_brl`.
- Sinh `order_ids`, `item_ids`, `seller_ids` và evidence tương ứng.
- Xử lý trường hợp order không có item row.

### File dự kiến phụ trách

```text
src/agents/order_seller_agent.py
src/repositories/order_repository.py
tests/test_order_seller_agent.py
```

### Contract bàn giao

```json
{
  "order_status": "delivered",
  "item_total_brl": 100.0,
  "freight_total_brl": 15.0,
  "late_seller_ids": [],
  "order_ids": [],
  "item_ids": [],
  "seller_ids": [],
  "evidence_ids": []
}
```

## 4. Người 3 — Payment Agent

### Công việc

- Đọc `olist_order_payments_dataset.csv`.
- Lấy toàn bộ payment row của từng order.
- Tính `payment_total_brl`.
- Tạo `payment_ids` từ `payment_sequential`.
- Kiểm tra số lượng payment row.
- Đối soát `payment_total` với `item_total + freight_total`, sai số tối đa `0.10 BRL`.
- Phát hiện trường hợp `valid_split_payment`.
- Cung cấp payment evidence.
- Kiểm thử trường hợp có nhiều payment row và làm tròn hai chữ số.

### File dự kiến phụ trách

```text
src/agents/payment_agent.py
src/repositories/payment_repository.py
tests/test_payment_agent.py
```

### Contract bàn giao

```json
{
  "payment_total_brl": 115.0,
  "payment_count": 2,
  "payment_matches_order_total": true,
  "is_split_payment": true,
  "payment_ids": [],
  "evidence_ids": []
}
```

## 5. Người 4 — Delivery & Policy Agent

### Công việc

- So sánh các trường:
  - `order_delivered_customer_date`
  - `order_estimated_delivery_date`
  - `order_delivered_carrier_date`
  - `shipping_limit_date`
- Phân biệt seller bàn giao trễ, logistics giao trễ và giao đúng cam kết.
- Áp dụng sáu quy tắc nghiệp vụ theo đúng thứ tự ưu tiên.
- Xác định:
  - `primary_issue`
  - `case_status`
  - root-cause code
  - responsible party
  - số tiền hoàn
  - resolution action
- Tạo policy evidence đúng định dạng.

### File dự kiến phụ trách

```text
src/agents/delivery_agent.py
src/agents/policy_agent.py
src/policy/ec_policy_v1.py
tests/test_policy.py
```

### Contract bàn giao

```json
{
  "primary_issue": "late_delivery_seller",
  "case_status": "action_required",
  "root_cause_code": "SELLER_HANDOFF_AFTER_LIMIT",
  "responsible_parties": [],
  "recommended_refund_brl": 15.0,
  "resolution_actions": ["refund_freight"],
  "policy_evidence_id": "policy:SELLER_HANDOFF_AFTER_LIMIT"
}
```

## 6. Người 5 — Verifier, Testing và Documentation

### Công việc kỹ thuật

- Viết JSON Schema hoặc validator tương đương.
- Kiểm tra đầy đủ trường bắt buộc và enum hợp lệ.
- Kiểm tra `confidence` thuộc đoạn `[0, 1]`.
- Kiểm tra giới hạn số phần tử trong từng danh sách.
- Kiểm tra evidence đúng định dạng và thực sự tồn tại trong CSV.
- Kiểm tra số tiền được làm tròn hai chữ số.
- Kiểm tra refund, action và case status nhất quán.
- Viết test cho toàn bộ pipeline.
- Kiểm tra có đúng 50 output và không có file lạ.
- Tạo `trace.jsonl` và `metadata.json`.
- Viết script kiểm tra bài trước khi nộp.

### Công việc tài liệu

- Hoàn thiện `architecture.md`.
- Vẽ sơ đồ agent và luồng handoff.
- Ghi hướng dẫn chạy, dependency và cấu hình.
- Kiểm tra `.gitignore` để không commit `.env`.
- Tạo file ZIP chỉ chứa đúng 50 output JSON.

### File dự kiến phụ trách

```text
src/agents/verifier_agent.py
src/validation/output_validator.py
tests/test_output_validator.py
scripts/validate_submission.py
architecture.md
metadata.json
trace.jsonl
```

### Kết quả bàn giao

- Báo cáo validation của 50 case.
- Bộ test và lệnh kiểm tra trước khi nộp.
- Tài liệu kiến trúc, metadata và trace hoàn chỉnh.
- File ZIP hợp lệ để nộp.

## 7. Contract chung cần thống nhất

Nhóm cần thống nhất object trung gian trước khi bắt đầu code:

```text
CaseInput
 ├── OrderSellerResult
 ├── PaymentResult
 ├── DeliveryResult
 └── PolicyResult
        ↓
   FinalCaseOutput
        ↓
   VerifierResult
```

Các nguyên tắc chung:

- Agent trả về dữ liệu có cấu trúc, không trả về văn bản tự do.
- Các tổng tiền làm tròn hai chữ số thập phân.
- Timestamp được so sánh theo giá trị trong CSV.
- Evidence phải tồn tại trong dữ liệu và đúng định dạng của đề bài.
- Policy Agent phải áp dụng quy tắc theo đúng thứ tự ưu tiên.

## 8. Thứ tự phối hợp

1. Người 1 định nghĩa contract và tạo skeleton dự án.
2. Người 2 và Người 3 phát triển song song các module dữ liệu.
3. Người 4 dùng contract của Người 2 và Người 3 để triển khai policy.
4. Người 5 viết validator song song dựa trên output schema.
5. Người 1 tích hợp toàn bộ module.
6. Cả nhóm chạy 50 case; Người 5 kiểm tra kết quả cuối cùng.
7. Mỗi thành viên tự hoàn thành báo cáo cá nhân theo đúng phần việc thực tế.

## 9. Checklist hoàn thành chung

- [ ] Pipeline multi-agent chạy được end-to-end.
- [ ] Mỗi agent có vai trò, input và output rõ ràng.
- [ ] Có handoff và trace chạy thực tế.
- [ ] Đủ đúng 50 file từ `EC_001.json` đến `EC_050.json`.
- [ ] Tất cả output đúng schema và quy tắc nghiệp vụ.
- [ ] Evidence tồn tại và đúng định dạng.
- [ ] `architecture.md`, `trace.jsonl` và `metadata.json` đã hoàn thiện.
- [ ] Mỗi thành viên đã hoàn thành báo cáo cá nhân.
- [ ] Không commit `.env`, API key hoặc secret.
- [ ] File ZIP chỉ chứa 50 output JSON.

> Lưu ý: Người 5 có thể chủ trì phần tài liệu chung, nhưng mỗi thành viên phải tự viết báo cáo cá nhân và chỉ nhận ownership cho phần mình thực sự thực hiện.

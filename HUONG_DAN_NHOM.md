# Hướng dẫn Kỹ thuật & Phân công Làm việc Nhóm (Team Development Guide)

Tài liệu này hướng dẫn chi tiết cách triển khai code cho từng thành viên dựa trên hệ thống **Data Contracts** đã chuẩn hóa tại `src/contracts.py`.

---

## 1. Cấu trúc Dự án & Quy định Thư mục

```text
K3-Day9-Multi-Agent-A2A/
├── data/                         # 9 file CSV của Olist (Không sửa)
├── input/                        # 50 file JSON khiếu nại (EC_001.json -> EC_050.json)
├── output/                       # Thư mục chứa 50 file JSON kết quả đầu ra
├── src/
│   ├── contracts.py              # Data Contracts chung (TẤT CẢ THÀNH VIÊN DÙNG CHUNG)
│   ├── agents/
│   │   ├── coordinator_agent.py  # Người 1: Điều phối pipeline & handoff
│   │   ├── order_seller_agent.py # Người 2: Agent xử lý Đơn & Seller
│   │   ├── payment_agent.py      # Người 3: Agent xử lý Thanh toán
│   │   ├── delivery_agent.py     # Người 4: Agent xử lý Vận chuyển & Chính sách
│   │   ├── policy_agent.py       # Người 4: Phân tích chính sách EC_POLICY_V1
│   │   └── verifier_agent.py     # Người 5: Agent kiểm tra chất lượng Output
│   └── repositories/
│       ├── order_repository.py   # Người 2: Đọc CSV orders, items, sellers
│       └── payment_repository.py # Người 3: Đọc CSV payments
├── tests/                        # Chứa các file unit test của từng người
├── main.py                       # Người 1: File chạy chính 50 cases
└── validate_submission.py        # Người 5: Script kiểm tra 50 output JSON
```

---

## 2. Hướng dẫn Chi tiết cho Từng Thành viên

### 👤 Người 1 — Coordinator & Integration (Trưởng nhóm)
* **File phụ trách**: `src/agents/coordinator_agent.py`, `src/contracts.py`, `main.py`
* **Nhiệm vụ**:
  1. Định nghĩa chuẩn hóa Pydantic Contracts.
  2. Điều phối luồng handoff dữ liệu từ `OrderSellerAgent` $\rightarrow$ `PaymentAgent` $\rightarrow$ `PolicyAgent` $\rightarrow$ `VerifierAgent`.
  3. Ghép nối code của 4 thành viên và chạy 50 cases tạo file tại `output/`.

---

### 👤 Người 2 — Order & Seller Agent
* **File phụ trách**: `src/repositories/order_repository.py`, `src/agents/order_seller_agent.py`
* **Input nhận vào**: `order_id` (string)
* **Quy trình xử lý**:
  1. Đọc CSV `olist_orders_dataset.csv`, `olist_order_items_dataset.csv`, `olist_sellers_dataset.csv`.
  2. Lấy trạng thái đơn `order_status`.
  3. So sánh ngày carrier nhận hàng (`order_delivered_carrier_date`) với hạn bàn giao (`shipping_limit_date`) của từng item. Nếu trễ $\rightarrow$ thêm seller_id vào `late_seller_ids`.
  4. Tính `item_total_brl` (tổng giá sản phẩm) và `freight_total_brl` (tổng cước vận chuyển), làm tròn 2 chữ số.
  5. Tạo danh sách ID: `order_ids` (`["order:<id>"]`), `item_ids` (`["<order_id>:<item_id>"]`), `seller_ids`, `evidence_ids`.
* **Output bắt buộc trả về**: `OrderSellerResult` (import từ `src.contracts`).

---

### 👤 Người 3 — Payment Agent
* **File phụ trách**: `src/repositories/payment_repository.py`, `src/agents/payment_agent.py`
* **Input nhận vào**: `order_id`, `item_total_brl`, `freight_total_brl`
* **Quy trình xử lý**:
  1. Đọc CSV `olist_order_payments_dataset.csv`.
  2. Tính `payment_total_brl` (tổng tiền thanh toán), làm tròn 2 chữ số.
  3. Đếm số lượng dòng thanh toán `payment_count`.
  4. Đánh giá `is_split_payment`: `True` nếu `payment_count >= 2`.
  5. Đánh giá đối soát tiền: `payment_matches_order_total = True` nếu `abs(payment_total - (item_total + freight_total)) <= 0.10`.
  6. Tạo danh sách `payment_ids` (`["<order_id>:<payment_sequential>"]`) và `evidence_ids` (`["payment:<order_id>:<seq>"]`).
* **Output bắt buộc trả về**: `PaymentResult` (import từ `src.contracts`).

---

### 👤 Người 4 — Delivery & Policy Agent
* **File phụ trách**: `src/agents/delivery_agent.py`, `src/agents/policy_agent.py`
* **Input nhận vào**: `OrderSellerResult` (của Người 2), `PaymentResult` (của Người 3)
* **Quy trình xử lý**:
  Áp dụng 6 quy tắc chính sách `EC_POLICY_V1` theo đúng thứ tự ưu tiên:
  1. `canceled_order_paid`: `order_status == "canceled"` & `payment_total > 0` $\rightarrow$ Refund 100% tổng payment, trách nhiệm `platform`.
  2. `unavailable_order_paid`: `order_status == "unavailable"` & `payment_total > 0` $\rightarrow$ Refund 100% tổng payment, trách nhiệm `platform`.
  3. `late_delivery_seller`: Đơn giao trễ cho khách & có seller bàn giao trễ cho carrier $\rightarrow$ Refund tổng cước freight, trách nhiệm seller ID vi phạm.
  4. `late_delivery_logistics`: Đơn giao trễ cho khách nhưng seller bàn giao đúng hạn $\rightarrow$ Refund tổng cước freight, trách nhiệm `logistics_provider`.
  5. `valid_split_payment`: Đơn có $\ge 2$ payment rows & tổng tiền khớp $\rightarrow$ Refund 0 BRL, action `explain_valid_split_payment`.
  6. `unsupported_late_claim`: Đơn giao đúng/trước hạn $\rightarrow$ Refund 0 BRL, action `reject_late_refund`.
* **Output bắt buộc trả về**: `PolicyResult` (import từ `src.contracts`).

---

### 👤 Người 5 — Verifier Agent, Testing & Documentation
* **File phụ trách**: `src/agents/verifier_agent.py`, `validate_submission.py`, `architecture.md`, `metadata.json`
* **Nhiệm vụ**:
  1. Viết `VerifierAgent` nhận `FinalCaseOutput` để kiểm tra toàn bộ ràng buộc đề bài (ràng buộc số lượng ID: max 5 entity IDs, max 10 evidence IDs, confidence $\in [0, 1]$).
  2. Viết script `validate_submission.py` tự động kiểm tra 50 file JSON tại `output/`.
  3. Hoàn thiện tài liệu `architecture.md`, `metadata.json`, và sinh `trace.jsonl`.
  4. Đóng gói thư mục `output/` thành file zip nộp bài.

---

## 3. Nguyên tắc Lập trình Bắt buộc

1. **Sử dụng Pydantic Contracts**: Luôn import các Data Class từ `src.contracts` để tạo object đầu ra.
2. **Làm tròn tiền**: Tất cả các phép tính tiền (`item_total_brl`, `freight_total_brl`, `payment_total_brl`, `recommended_refund_brl`) phải dùng `round(value, 2)`.
3. **So sánh Thời gian**: So sánh chuỗi ngày giờ theo chuẩn ISO trong CSV (không chuyển đổi múi giờ).
4. **Git Workflow**: 
   - Trước khi sửa code: `git pull origin main`
   - Đặt tên commit rõ ràng: `git commit -m "feat(payment): implement PaymentAgent reconciliation"`

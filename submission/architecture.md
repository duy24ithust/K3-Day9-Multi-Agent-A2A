# Multi-Agent Architecture for E-commerce Dispute Resolution

Hệ thống Multi-Agent được thiết kế chuyên biệt để tự động hóa quy trình đối soát và xử lý khiếu nại thương mại điện tử trên bộ dữ liệu Olist E-commerce, đạt điểm số tối đa **100/100** trên hệ thống chấm điểm tự động.

---

## 1. Sơ đồ Kiến trúc & Luồng Handoff (Multi-Agent Sequence Diagram)

```mermaid
sequenceDiagram
    autonumber
    participant Input as Case Input (EC_xxx.json)
    participant Coord as Coordinator Agent
    participant OrderAgent as Order & Seller Agent
    participant PayAgent as Payment Agent
    participant PolicyAgent as Delivery & Policy Agent (gpt-4o-mini)
    participant Verifier as Verifier Agent
    participant Output as Final Output (EC_xxx.json)

    Input->>Coord: Nhận khiếu nại (case_id, claimed_order_id, customer_message)
    Coord->>OrderAgent: Trích xuất trạng thái đơn & mốc bàn giao seller (order_id)
    OrderAgent-->>Coord: Trả về OrderSellerResult (status, item_total, freight_total, late_sellers)
    Coord->>PayAgent: Trích xuất lịch sử thanh toán & đối soát tiền (order_id, totals)
    PayAgent-->>Coord: Trả về PaymentResult (payment_total, is_split, matches_total)
    Coord->>PolicyAgent: Đánh giá chính sách EC_POLICY_V1 (OrderSellerResult + PaymentResult + Message)
    PolicyAgent-->>Coord: Trả về PolicyResult (primary_issue, refund, responsible, root_cause)
    Coord->>Verifier: Gửi FinalCaseOutput để kiểm tra ràng buộc Schema & Evidence ID
    Verifier-->>Coord: Trả về VerifierResult (is_valid = True)
    Coord->>Output: Ghi kết quả output/EC_xxx.json & trace.jsonl
```

---

## 2. Vai trò và Phân quyền Các Agent trong Kiến trúc

| Tên Agent | Vai trò & Nhiệm vụ chính | Nguồn dữ liệu truy cập | Output Contract |
| :--- | :--- | :--- | :--- |
| **Coordinator Agent** (Người 1) | Tiếp nhận yêu cầu, phân công nhiệm vụ, quản lý luồng handoff, ghép nối dữ liệu và tạo file JSON đầu ra. | `input/EC_001.json` $\rightarrow$ `EC_050.json` | `FinalCaseOutput` |
| **Order & Seller Agent** (Người 2) | Phân tích trạng thái đơn (`order_status`), mốc thời gian bàn giao seller (`shipping_limit_date`), ngày giao carrier và tính `item_total`, `freight_total`. | `olist_orders_dataset.csv`, `olist_order_items_dataset.csv`, `olist_sellers_dataset.csv` | `OrderSellerResult` |
| **Payment Agent** (Người 3) | Tính tổng tiền thanh toán (`payment_total_brl`), đối soát khớp tiền trong sai số $\le 0.10$ BRL và phát hiện thanh toán chia nhỏ (`is_split_payment`). | `olist_order_payments_dataset.csv` | `PaymentResult` |
| **Delivery & Policy Agent** (Người 4) | Phân tích mốc thời gian giao khách (`order_delivered_customer_date`), áp 6 quy tắc chính sách `EC_POLICY_V1` & gọi LLM `gpt-4o-mini` kiểm tra ngữ cảnh tin nhắn. | `OrderSellerResult`, `PaymentResult`, OpenAI GPT-4o-mini | `PolicyResult` |
| **Verifier Agent** (Người 5) | Thẩm định 100% tính hợp lệ của Output (giới hạn 5 entity IDs, 10 evidence IDs, confidence $[0, 1]$, đúng định dạng bằng chứng). | `FinalCaseOutput` | `VerifierResult` |

---

## 3. Chìa khóa Kỹ thuật Đạt Điểm 100 Tuyệt đối

1. **Chuẩn hóa Hợp đồng Dữ liệu (Contract-Driven Development)**:
   * Tất cả các agent trao đổi thông tin thông qua các Pydantic Models v2 định nghĩa sẵn trong `src/contracts.py`.

2. **Chính xác Tuyệt đối về Bằng chứng (Evidence ID Precision)**:
   * Sắp xếp danh sách `evidence_ids` theo đúng 5 cấp bậc tiêu chuẩn: `order` $\rightarrow$ `item` $\rightarrow$ `payment` $\rightarrow$ `seller` $\rightarrow$ `policy`.
   * **Triệt tiêu False Positive**: Bằng chứng `seller:<seller_id>` chỉ được bao gồm KHI VÀ CHỈ KHI Seller thực sự có lỗi bàn giao muộn (`late_delivery_seller`).

3. **Chính xác về Thực thể Liên quan (Affected Entities)**:
   * Giữ nguyên `seller_ids` của tất cả sản phẩm trong đơn để phản ánh đúng thông tin thực thể liên quan của đơn hàng.

4. **Chỉ số Tin cậy Tuyệt đối (`confidence = 1.0`)**:
   * Phản ánh mức độ tin cậy 100% khi đối soát dữ liệu thực tế từ Olist CSV.

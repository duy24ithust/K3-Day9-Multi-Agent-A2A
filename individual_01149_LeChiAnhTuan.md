# Báo cáo vai trò cá nhân — Day 9: Multi-Agent A2A

## 1. Thông tin cá nhân

| Thông tin | Nội dung |
| --- | --- |
| Họ và tên | Lê Chí Anh Tuấn |
| Mã học viên | 01149 |
| Khóa/Lớp | K3 |
| Vai trò chính | Role 2 — Order & Seller Agent |
| Ngày hoàn thành | 2026-08-05 |

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao | Trạng thái |
| --- | --- | --- | --- | --- |
| Order Repository | `src/repositories/order_repository.py` | Ba CSV orders, order items và sellers | `OrderRecord`, `OrderItemRecord`, `SellerRecord` và các hàm tra cứu | Hoàn thành |
| Order & Seller Agent | `src/agents/order_seller_agent.py` — `OrderSellerAgent.analyze()` | `order_id` | `OrderSellerResult` theo contract chung | Hoàn thành |
| Unit test Role 2 | `tests/test_order_seller_agent.py` | Dữ liệu CSV fixture độc lập | Kết quả kiểm thử repository và agent | Hoàn thành |
| Tài liệu handoff | `ROLE2_HANDOFF.md` | Contract và implementation Role 2 | Hướng dẫn tích hợp cho Role 1 và Role 4 | Hoàn thành |

Order Repository chịu trách nhiệm đọc dữ liệu nguồn và cung cấp các record bất biến cho agent. Order & Seller Agent sử dụng repository để phân tích trạng thái đơn, item, seller, tiền hàng, phí vận chuyển và thời điểm seller bàn giao cho carrier. Kết quả được bàn giao cho Coordinator Agent và Policy Agent thông qua `OrderSellerResult` trong `src/contracts.py`.

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động | Thành viên/module được hỗ trợ | Kết quả |
| --- | --- | --- |
| Rà soát contract tích hợp | Role 1 — Coordinator | Xác nhận `OrderSellerAgent.analyze(order_id)` tương thích lời gọi hiện có trong Coordinator |
| Chuẩn hóa dữ liệu handoff | Role 4 — Policy Agent | Cung cấp `order_status`, timestamp giao hàng, `late_seller_ids`, item total và freight total |
| Rà soát quy ước entity/evidence | Role 5 — Verifier | Phân biệt ID thô trong affected entities và ID có tiền tố trong evidence |

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao | Cách xác minh |
| --- | --- | --- | --- |
| Đọc và lập index dữ liệu Role 2 | `OrderRepository` | Mỗi CSV chỉ được đọc một lần; hỗ trợ tra cứu order, item và seller | Chạy unit test repository và chạy agent trên 50 input |
| Tính tổng tiền hàng và vận chuyển | `OrderSellerAgent.analyze()` | `item_total_brl` và `freight_total_brl` làm tròn hai chữ số | Unit test với order nhiều item |
| Phát hiện seller bàn giao trễ | `OrderSellerAgent._late_items()` | Seller được đánh dấu trễ khi carrier date lớn hơn shipping limit date | Test trường hợp trễ, đúng hạn và hai timestamp bằng nhau |
| Sinh affected entities và evidence | `OrderSellerAgent._build_evidence()` | ID đúng định dạng, có thứ tự ổn định và không vượt giới hạn | Assertions trong unit test và kiểm tra 50 input thật |
| Xử lý dữ liệu biên | Repository và Agent | Hỗ trợ order không item, thiếu timestamp, order không tồn tại và CSV thiếu | Các test tương ứng trong bộ 8 unit test |

Output cụ thể của phần việc là một `OrderSellerResult` có cấu trúc cho từng order. Khi chạy trên 50 input thật, agent tìm thấy đủ 50 order, trong đó có 34 order `delivered`, 8 order `canceled`, 8 order `unavailable`, 8 order không có item và 9 order có seller bàn giao trễ.

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết

Một khiếu nại không thể được đánh giá chỉ từ nội dung khách hàng cung cấp. Phần Role 2 phải truy xuất đúng order trong dữ liệu Olist, lấy toàn bộ item và seller liên quan, tính giá trị hàng hóa và phí vận chuyển, đồng thời xác định seller có giao hàng cho carrier quá `shipping_limit_date` hay không. Kết quả phải có thể kiểm chứng trực tiếp bằng entity ID và evidence ID.

### Cách triển khai

`OrderRepository` đọc ba file CSV bằng thư viện chuẩn `csv`, sau đó tạo:

- Dictionary order theo `order_id`.
- Dictionary danh sách item theo `order_id`.
- Dictionary seller theo `seller_id`.

Các record dùng `dataclass(frozen=True)` để tránh agent vô tình sửa dữ liệu nguồn. Tiền được parse bằng `Decimal`, cộng trước rồi mới chuyển thành số thực và làm tròn hai chữ số. Item được sắp xếp theo `order_item_id` để kết quả ổn định giữa các lần chạy.

`OrderSellerAgent.analyze()` thực hiện các bước:

1. Chuẩn hóa và kiểm tra `order_id`.
2. Truy xuất order cùng toàn bộ item.
3. Tính tổng `price` và `freight_value`.
4. So sánh `order_delivered_carrier_date` với `shipping_limit_date` của từng item.
5. Khử trùng lặp seller nhưng giữ nguyên thứ tự xuất hiện.
6. Tạo affected entities và evidence có thể kiểm chứng.
7. Khởi tạo và trả về `OrderSellerResult` theo Pydantic contract chung.

Điều kiện bàn giao trễ được cài đặt đúng theo đề bài:

```text
order_delivered_carrier_date > shipping_limit_date
```

Nếu hai thời điểm bằng nhau thì seller không bị xem là trễ. Nếu thiếu carrier date hoặc shipping limit date, agent không tự tạo kết luận trễ.

### Input, output và contract

| Thành phần | Mô tả |
| --- | --- |
| Input | Một chuỗi `order_id` hợp lệ từ `customer_request.claimed_order_id` |
| Output | `OrderSellerResult` trong `src/contracts.py` |
| Module phụ thuộc | `src/contracts.py`, ba CSV orders/items/sellers |
| Module sử dụng output | `CoordinatorAgent`, Payment Agent và Policy Agent |
| Điều kiện lỗi cần xử lý | Order ID rỗng, order không tồn tại, CSV thiếu, giá tiền không hợp lệ, order không item và timestamp thiếu |

Các quy ước ID:

```text
order_ids:   <order_id>
item_ids:    <order_id>:<order_item_id>
seller_ids:  <seller_id>
evidence:    order:<order_id>
             item:<order_id>:<order_item_id>
             seller:<seller_id>
```

### Cách xác minh

```bash
python -m pytest tests/test_order_seller_agent.py -q
python -m compileall -q src tests
```

- **Kết quả mong đợi:** Tất cả unit test pass, source compile thành công và agent xử lý được đủ 50 input.
- **Kết quả thực tế:** `8 passed in 0.36s`; compile thành công; 50/50 order được tìm thấy và phân tích.
- **Artifact/log:** `tests/test_order_seller_agent.py`, `ROLE2_HANDOFF.md`; không chứa secret.

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Pipeline cần xử lý 50 case nhưng các CSV Olist có hàng chục đến hàng trăm nghìn dòng. Nếu đọc lại ba CSV trong mỗi lần `analyze()`, toàn bộ dữ liệu sẽ bị quét lặp lại 50 lần.
- **Các phương án đã cân nhắc:** (1) đọc và lọc CSV cho mỗi case; (2) dùng pandas và lọc DataFrame; (3) đọc CSV một lần bằng thư viện chuẩn rồi lập dictionary index.
- **Phương án đã chọn:** Đọc ba CSV một lần trong `OrderRepository`, lưu index theo `order_id` và tái sử dụng cùng repository cho toàn bộ pipeline.
- **Lý do:** Giảm I/O lặp lại, không bổ sung dependency ngoài, tra cứu nhanh, dễ inject thư mục dữ liệu tạm khi unit test và giữ logic truy cập dữ liệu tách biệt khỏi agent.
- **Bằng chứng quyết định phù hợp:** Cùng một instance agent đã xử lý đủ 50 input thật; toàn bộ kiểm tra hoàn thành mà không phải khởi tạo lại repository cho từng case.

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng/lỗi nguyên văn:** Hướng dẫn nhóm mô tả `order_ids` dưới dạng `['order:<id>']`, trong khi output schema chính thức minh họa `order_ids` bằng ID thô và chỉ `evidence_ids` có tiền tố `order:`.
- **Bước tái hiện:** Đối chiếu mục Role 2 trong `HUONG_DAN_NHOM.md` với mục Output schema và Evidence ID trong `README.md`, sau đó kiểm tra cách Coordinator gắn `order_seller_res.order_ids` vào `affected_entities.order_ids`.
- **Nguyên nhân gốc:** Tài liệu hướng dẫn nhóm đã trộn lẫn quy ước affected entity với quy ước evidence.
- **Cách xử lý:** Dùng ID thô cho `order_ids`, dùng `order:<order_id>` cho evidence và ghi rõ quyết định trong code cùng tài liệu handoff.
- **Cách xác minh sau khi sửa:** Unit test kiểm tra `order_ids == ['on_time']` và evidence chứa `order:on_time`; Coordinator có thể chuyển trực tiếp entity IDs sang final output.
- **Điều học được:** Khi tài liệu nội bộ mâu thuẫn, cần ưu tiên schema chấm điểm chính thức và kiểm tra consumer thực tế của contract trước khi triển khai.

## 7. Hiểu biết về luồng end-to-end

1. Coordinator đọc từng file `EC_xxx.json`, lấy `claimed_order_id` và chuyển cho Order & Seller Agent. Agent của tôi tra cứu orders, items và sellers rồi trả `OrderSellerResult`.
2. Payment Agent nhận `order_id`, `item_total_brl` và `freight_total_brl` để đối soát toàn bộ payment row và trả `PaymentResult`.
3. Policy Agent nhận kết quả của Role 2 và Role 3, so sánh các timestamp giao hàng, sau đó áp dụng sáu quy tắc `EC_POLICY_V1` theo đúng thứ tự ưu tiên để xác định issue, trách nhiệm, refund và action.
4. Coordinator kết hợp các kết quả thành `FinalCaseOutput`, bao gồm assessment, affected entities, root cause, evidence, financial resolution và resolution actions.
5. Verifier Agent kiểm tra schema, giới hạn số ID, evidence, số tiền và tính nhất quán trước khi ghi 50 JSON vào `output/`. Trace của các handoff được lưu để chứng minh hệ thống multi-agent đã chạy thật.

Vai trò của `OrderSellerResult` trong luồng là cung cấp dữ liệu có thể kiểm chứng cho cả Payment Agent và Policy Agent. Role 2 không tự quyết định primary issue hoặc hoàn tiền, nhờ đó ranh giới trách nhiệm giữa các agent được giữ rõ ràng.

## 8. Cam kết của thành viên

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Tôi không ghi “đã chạy thành công” cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** Lê Chí Anh Tuấn  
**Ngày xác nhận:** 2026-08-05


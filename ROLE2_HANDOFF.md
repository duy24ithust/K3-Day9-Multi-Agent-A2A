# Role 2 — Order & Seller Agent Handoff

## Phạm vi đã triển khai

Role 2 sở hữu hai module:

```text
src/repositories/order_repository.py
src/agents/order_seller_agent.py
```

Repository đọc một lần ba nguồn dữ liệu `orders`, `order_items` và `sellers`, sau đó lập index theo `order_id`. Agent nhận một `order_id` và trả về đúng `OrderSellerResult` trong `src/contracts.py`.

## Cách sử dụng

```python
from src.agents.order_seller_agent import OrderSellerAgent
from src.repositories.order_repository import OrderRepository

repository = OrderRepository("data")
agent = OrderSellerAgent(repository)
result = agent.analyze("e2a03ccf5ea816036608b2d8c3ab8e60")
```

Coordinator có thể khởi tạo một agent và tái sử dụng cho toàn bộ 50 case. Không nên tạo lại repository ở mỗi case vì sẽ đọc lại toàn bộ CSV.

## Contract đầu ra

Agent trả về các trường:

- Trạng thái và timestamp của order.
- Tổng `price` trong `item_total_brl`.
- Tổng `freight_value` trong `freight_total_brl`.
- Seller bàn giao trễ trong `late_seller_ids`.
- Entity IDs và evidence IDs có thể kiểm chứng trực tiếp từ CSV.

Quy tắc seller bàn giao trễ:

```text
order_delivered_carrier_date > shipping_limit_date
```

Nếu hai timestamp bằng nhau thì seller không trễ. Nếu thiếu một timestamp, agent không tự suy diễn seller trễ.

## Quy ước ID

- `order_ids`: `['<order_id>']`
- `item_ids`: `['<order_id>:<order_item_id>']`
- `seller_ids`: `['<seller_id>']`
- Order evidence: `order:<order_id>`
- Item evidence: `item:<order_id>:<order_item_id>`
- Seller evidence: `seller:<seller_id>`

`order_ids` dùng ID thô theo output schema chính thức. Tiền tố `order:` chỉ được dùng trong evidence.

## Xử lý trường hợp biên

- Order không có item: tổng item và freight bằng `0.0`; danh sách item/seller để rỗng.
- Không tìm thấy order: trả `order_status='unknown'` và không tạo entity/evidence giả.
- `order_id` rỗng: raise `ValueError`.
- Thiếu CSV bắt buộc: fail fast bằng `FileNotFoundError`.
- Monetary cell không hợp lệ: raise `ValueError` kèm order và tên cột.
- Entity IDs được giới hạn tối đa 5.
- Evidence của Role 2 được giới hạn tối đa 7 để chừa chỗ cho Payment và Policy Agent trong giới hạn 10 evidence cuối cùng.

## Kiểm thử

Chạy unit test:

```bash
python -m pytest tests/test_order_seller_agent.py -q
```

Kết quả gần nhất:

```text
8 passed
```

Kết quả kiểm tra trên 50 input thật:

```text
cases_analyzed: 50
orders_found: 50
statuses: delivered=34, canceled=8, unavailable=8
orders_without_items: 8
orders_with_late_seller: 9
max_items_exposed: 3
max_evidence: 5
```

## Handoff cho Role 1 và Role 4

Role 1 truyền instance này vào Coordinator:

```python
coordinator = CoordinatorAgent(order_seller_agent=OrderSellerAgent())
```

Role 4 sử dụng trực tiếp `order_status`, ba timestamp giao hàng, `late_seller_ids`, `item_total_brl` và `freight_total_brl` từ `OrderSellerResult`; Role 2 không tự quyết định primary issue, refund hoặc resolution action.


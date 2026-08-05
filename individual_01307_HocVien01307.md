# BÁO CÁO CÁ NHÂN LAB DAY 09 - MULTI-AGENT E-COMMERCE DISPUTE RESOLUTION

- **Họ và tên**: Học viên 01307
- **Mã số sinh viên (MSSV)**: 01307
- **Lớp**: D303
- **Leaderboard Score**: **100/100** (Tuyệt đối)
- **Repository**: [K3-Day9-Multi-Agent-A2A](https://github.com/duy24ithust/K3-Day9-Multi-Agent-A2A)

---

## 1. Phân công Vai trò trong Nhóm

Trong dự án này, tôi đảm nhận vai trò **Thành viên 1 - Coordinator Agent & System Integrator (Agent Điều phối & Tối ưu hóa)**:

* **Tạo dựng Hợp đồng Dữ liệu (`src/contracts.py`)**: Định nghĩa chuẩn hóa Pydantic Schema v2 cho 5 vai trò.
* **Xây dựng Agent Điều phối (`src/agents/coordinator_agent.py`)**: Tiếp nhận yêu cầu, quản lý chuỗi Handoff giữa 4 Agent chuyên môn (OrderSeller, Payment, DeliveryPolicy, Verifier), và tổng hợp đầu ra `FinalCaseOutput`.
* **Tối ưu hóa Bằng chứng & Độ tin cậy (Evidence & Confidence Optimization)**:
  * Chuẩn hóa 5 cấp bậc bằng chứng (`order` $\rightarrow$ `item` $\rightarrow$ `payment` $\rightarrow$ `seller` $\rightarrow$ `policy`).
  * Loại bỏ lỗi False Positive đối với `seller:<seller_id>` ở các ca Seller không có lỗi.
  * Tối ưu chỉ số `confidence = 1.0` cho toàn bộ 50 ca đối soát.
* **Chạy Batch Pipeline & Đóng gói (`main.py`, `validate_submission.py`)**: Xử lý 50 ca khiếu nại, đóng gói `output.zip` đúng chuẩn cấu trúc `output/` và kiểm tra 100% hợp lệ.

---

## 2. Kết quả Đạt được

* **Điểm thi Competition Leaderboard**: **100 / 100 điểm** (Đạt mốc tuyệt đối cả 6 tiêu chí: Đánh giá case, Entity liên quan, Nguyên nhân gốc, Bằng chứng, Tài chính, Hành động xử lý).
* **Thời gian xử lý**: Hoàn thành tự động 50 cases chỉ trong ~52 giây.
* **Tài liệu & Audit artifacts**: Đã hoàn thiện `architecture.md`, `metadata.json`, `trace.jsonl`, và bộ kiểm thử `tests/test_verifier_agent.py`.

---

## 3. Bài học Rút ra & Kỹ thuật Áp dụng

1. **Handoff Protocol & Contract-Driven Development**: Khi chia nhỏ bài toán thành các Agent chuyên biệt với Hợp đồng dữ liệu rõ ràng, hệ thống chạy ổn định, không bị chồng chéo logic và dễ dàng kiểm thử độc lập.
2. **Triệt tiêu False Positive trong Evidence IDs**: Việc lựa chọn đúng bằng chứng có liên quan trực tiếp đến hành vi vi phạm quyết định lớn đến mốc điểm tuyệt đối.
3. **Kết hợp LLM (`gpt-4o-mini`) và Rule-based Engine**: Sử dụng Rule-based Engine cho các phép toán tài chính và timestamp để đạt độ chính xác 100%, kết hợp LLM nhỏ ($\le 10\text{B}$) để hiểu ngữ cảnh khiếu nại của khách hàng.

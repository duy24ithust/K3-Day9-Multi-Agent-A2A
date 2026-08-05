# Member Role Report — Day 9: Multi Agent A2A

## 1. Thông tin cá nhân

| Thông tin       | Nội dung                                    |
| --------------- | ------------------------------------------- |
| Họ và tên       | Đậu Quốc Duy                                |
| MSSV            | 2A202601445                                 |
| Khóa/Lớp        | K3                                          |
| Vai trò chính   | Người 5 — Verifier, Testing & Documentation |
| Ngày hoàn thành | 2026-08-05                                  |

## 2. Vai trò và phạm vi công việc

Hệ thống của nhóm dùng **Custom Multi-Agent Framework (Python + Pydantic)**: một Coordinator điều phối tuần tự Order&Seller → Payment → Delivery/Policy → Verifier, dữ liệu trao đổi giữa các agent qua các contract Pydantic trong `src/contracts.py`. Vai trò của tôi là **tầng nghiệm thu**: không sinh kết luận nghiệp vụ, mà kiểm output của các agent khác đúng schema/ràng buộc và đóng gói hợp lệ trước khi nộp.

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao | Trạng thái |
| ------------------ | ------------------ | -------------- | --------------- | ---------- |
| Verifier Agent | `src/agents/verifier_agent.py::VerifierAgent.verify` | `FinalCaseOutput` | `VerifierResult(is_valid, validation_errors)` | Hoàn thành |
| Output/Verifier contract | `src/contracts.py::FinalCaseOutput`, `VerifierResult` (Pydantic) | field theo schema đề | model có ràng buộc `max_length`, `ge/le` | Hoàn thành |
| Unit test verifier | `tests/test_verifier_agent.py` | `FinalCaseOutput` mẫu | 2 test (valid pass / vượt evidence fail) | Hoàn thành |
| Pre-submission checker | `validate_submission.py` | `output/` + file repo | exit 0/1 + danh sách lỗi | Hoàn thành |
| Trace & metadata | `trace.jsonl`, `metadata.json` (sinh bởi `main.py`) | event mỗi case | trace thực thi + metadata run | Hoàn thành |
| Tài liệu kiến trúc | `architecture.md` | thiết kế nhóm | sơ đồ agent + bảng rule + luồng handoff | Hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động | Thành viên/module được hỗ trợ | Kết quả |
| --------- | ----------------------------- | ------- |
| Rà cấu hình model & tích hợp OpenAI | `main.py`, `.env.example` (Người 1) | Xác nhận `MODEL_NAME = "gpt-4o-mini"` khớp `metadata.json`; kiểm `.gitignore` chặn `.env` |
| Đóng gói ZIP nộp | cả nhóm | ZIP chỉ chứa 50 output JSON dưới `output/` |

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/artifact liên quan | Kết quả bàn giao | Cách xác minh |
| --------------------- | ----------------------- | ---------------- | ------------- |
| Verifier kiểm ràng buộc schema | `src/agents/verifier_agent.py` | trả `is_valid` + list lỗi cho mỗi output | `python -m unittest tests.test_verifier_agent` |
| Unit test verifier | `tests/test_verifier_agent.py` | 2/2 test **OK** | `Ran 2 tests ... OK` |
| Validate toàn bộ submission | `validate_submission.py` | **PASSED** 50/50 file + repo files | `python validate_submission.py` |

Output cụ thể phần việc tôi tạo/xác minh: kết quả nghiệm thu **50/50 output hợp lệ** (`✅ PASSED: All 50 output files and repository requirements strictly validated!`) và verifier test **2/2 OK**.

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết

Bài chấm dùng **hard gate**: chỉ cần một output sai schema, vượt giới hạn số phần tử (≤5 entity, ≤10 evidence, ≤3 root cause…), hoặc `confidence` ngoài `[0,1]` là mất điểm cả case. Vai trò của tôi là dựng lớp kiểm chứng để không output nào lọt qua với các lỗi đó, và đảm bảo gói nộp đúng chuẩn (đúng 50 file + đủ file repo bắt buộc).

### Cách triển khai

- **`VerifierAgent.verify(output: FinalCaseOutput)`**: nhận một output đã dựng, kiểm từng ràng buộc và gom lỗi vào `errors` — bound của `order_ids/item_ids/seller_ids/payment_ids` ≤ 5, `evidence_ids` ≤ 10, `ranked_causes`/`responsible_parties` ≤ 3, `resolution_actions` ≤ 5, và `confidence ∈ [0.0, 1.0]`. Trả `VerifierResult(is_valid=len(errors)==0, validation_errors=errors)`.
- **Ràng buộc ở tầng contract** (`src/contracts.py`): các model Pydantic đã đặt `max_length` (ví dụ `evidence_ids: max_length=10`, các entity list `max_length=5`) và `confidence: Field(..., ge=0.0, le=1.0)`. Nhờ đó những vi phạm nặng bị chặn ngay khi khởi tạo `FinalCaseOutput` (raise `ValidationError`), verifier là lớp kiểm bổ sung và tường minh hóa lỗi.
- **`validate_submission.py`**: chốt cuối, soi artifact đã sinh (không chạy lại pipeline) — đúng 50 file `EC_001..EC_050`, đủ 7 key top-level, mọi bound, `confidence` trong khoảng, và tồn tại các file repo bắt buộc `architecture.md`, `metadata.json`, `trace.jsonl`.

### Input, output và contract

| Thành phần | Mô tả |
| ---------- | ----- |
| Input | `FinalCaseOutput` (verifier) / thư mục `output/` + file repo (checker) |
| Output | `VerifierResult(is_valid, validation_errors)`; exit code 0/1 + danh sách lỗi |
| Module phụ thuộc | `src/contracts.py` (định nghĩa `FinalCaseOutput`, `VerifierResult`) |
| Module sử dụng output | `main.py` (Coordinator gọi verifier trong pipeline), người nộp bài |
| Điều kiện lỗi cần xử lý | thiếu/thừa file, thiếu key, vượt bound entity/evidence/cause/action, confidence ngoài `[0,1]`, JSON hỏng |

### Cách xác minh

```bash
python -m unittest tests.test_verifier_agent   # unit test verifier
python validate_submission.py                  # nghiệm thu 50 output + file repo
```

- **Kết quả mong đợi:** verifier test OK, checker in `✅ PASSED`.
- **Kết quả thực tế:** `Ran 2 tests ... OK`; `✅ PASSED: All 50 output files and repository requirements strictly validated!`.
- **Artifact/log:** `output/EC_*.json`, `trace.jsonl`, `metadata.json` (không chứa secret).

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** đặt ràng buộc schema ở đâu để chống hard gate — chỉ ở agent kiểm, hay cả ở contract.
- **Các phương án đã cân nhắc:** (1) Chỉ kiểm bằng `VerifierAgent` sau khi output đã dựng xong; (2) Đặt luôn ràng buộc `max_length`/`ge/le` vào model Pydantic `FinalCaseOutput` **và** giữ verifier như lớp kiểm tường minh.
- **Phương án đã chọn:** (2).
- **Lý do:** ràng buộc ở contract chặn vi phạm nặng ngay lúc khởi tạo (fail-fast, raise `ValidationError`), còn `VerifierAgent` gom lỗi thành danh sách đọc được để log/nghiệm thu — hai lớp bổ trợ, không phụ thuộc mỗi một điểm.
- **Bằng chứng quyết định phù hợp:** test `test_exceeding_evidence_limit_fails` chứng minh 12 evidence bị chặn ngay ở tầng Pydantic; `test_valid_output_passes` chứng minh output hợp lệ đi qua verifier sạch; và `validate_submission.py` PASSED trên cả 50 case.

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng:** Sau khi pull nhánh `main` về, script `scripts/validate_submission.py` (bản tôi viết ở nhánh riêng trước đó) crash: `ModuleNotFoundError: No module named 'src.schema'`.
- **Bước tái hiện:** `python scripts/validate_submission.py`.
- **Nguyên nhân gốc:** nhánh riêng của tôi trước đây dùng kiến trúc khác (`src/schema.py`, LangGraph). Nhánh `main` của nhóm dùng **Pydantic contracts** (`src/contracts.py`) và có sẵn `validate_submission.py` ở thư mục gốc — module `src.schema` không còn tồn tại nên import gãy.
- **Cách xử lý:** dừng dùng script cũ; chuyển sang dùng `validate_submission.py` (bản chuẩn của nhóm ở root) và `VerifierAgent` trong `src/contracts.py`; viết lại báo cáo này cho khớp codebase `main`.
- **Cách xác minh sau khi sửa:** `python validate_submission.py` → `✅ PASSED`; `python -m unittest tests.test_verifier_agent` → `OK`.
- **Điều học được:** báo cáo và công cụ phải bám **codebase đang trên `main`**, không bám nhánh riêng; sau mỗi lần pull phải kiểm lại import/đường dẫn trước khi kết luận "đã chạy được".

## 7. Hiểu biết về luồng end-to-end

**Câu trả lời (theo đúng bài lab Multi-Agent A2A này):**

1. **Dữ liệu đi từ input đến kết luận:** `main.py` đọc `input/EC_NNN.json`, lấy `claimed_order_id`, Coordinator điều phối các agent (Order&Seller, Payment, Delivery/Policy) tra dữ liệu Olist qua các repository/tool, trao đổi bằng contract Pydantic, rồi dựng `FinalCaseOutput` và ghi `output/EC_NNN.json`.
2. **Đo chất lượng dựa trên gì:** ground-truth là dữ liệu Olist có thể kiểm chứng (status đơn, `shipping_limit_date`, ngày giao, `payment_value`). Policy áp `EC_POLICY_V1` cho ra `primary_issue`, responsible party, refund; verifier + `validate_submission.py` đối chiếu ràng buộc schema.
3. **Kiểm chất lượng khác giám sát vận hành ở đâu:** verifier/validate chặn hard gate về **schema & bound**; còn `trace.jsonl` là log vận hành ghi lại quá trình xử lý từng case để truy vết, không dùng để chấm đúng/sai nghiệp vụ.
4. **Vì sao cùng một tập test cho mọi lần chạy:** 50 case cố định là chuẩn so sánh — đổi model (`gpt-4o-mini`) hay tinh chỉnh agent đều chạy lại đúng 50 input đó, nên chênh lệch kết quả phản ánh thay đổi hệ thống chứ không phải do đổi dữ liệu đầu vào.
5. **Xem là thành công dựa trên artifact/metric nào:** `validate_submission.py` in `✅ PASSED` cho 50/50 output + đủ file repo, unit test verifier `OK`, và `metadata.json` ghi `processed_cases: 50`.

## 8. Cam kết của thành viên

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Tôi không ghi "đã chạy thành công" cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** Đậu Quốc Duy
**Ngày xác nhận:** 2026-08-05

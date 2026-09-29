# Báo cáo cá nhân — K4-L3A Day 13 Monitoring & LLMOps

> Mỗi học viên hoàn thiện một file duy nhất này. Khi dẫn evidence, dùng đường dẫn tương đối, ví dụ `evidence/07-trace-waterfall.png`.

## 1. Thông tin học viên

- **Họ và tên:** THIỀU QUANG VINH
- **MSSV:** 2A202602877
- **Lớp:** K4-L3A
- **Repository URL:** https://github.com/zinhcandoit/K4-L3-DAY13-ThieuQuangVinh-2A202602877-Monitoring-LLMOps.git
- **Commit SHA cuối:** 
- **Challenge ID:**
- **Tên project Langfuse cá nhân:** `day13-k4-l3a-2A202602877`

## 2. Evidence index

Điền đúng đường dẫn tới evidence thực tế. Có thể đổi tên hoặc dùng nhiều ảnh nếu cần.

| Evidence | Đường dẫn |
|---|---|
| Pytest cuối | `evidence/01-pytest.png` |
| Log validator | `evidence/02-log-validator.png` |
| Dashboard validator | `evidence/03-dashboard-validator.png` |
| Structured log | `evidence/04-structured-log.png` |
| PII redaction | `evidence/05-pii-redaction.png` |
| Trace list | `evidence/06-trace-list.png` |
| Trace waterfall | `evidence/07-trace-waterfall.png` |
| Trace metadata | `evidence/08-trace-metadata.png` |
| Prompt versions | `evidence/09-prompt-versions.png` |
| Prompt rollback | `evidence/10-prompt-rollback.png` |
| Dashboard runtime | `evidence/11-dashboard-overview.png` |
| Incident metric | `evidence/12-incident-metric.png` |
| Incident log | `evidence/13-incident-log.png` |
| Incident trace | `evidence/14-incident-trace.png` |

## 3. Kết quả kỹ thuật

| Nội dung | Baseline | Kết quả cuối | Nhận xét |
|---|---|---|---|
| `validate_logs.py` | 30/100 (40/41 records thiếu required fields/enrichment) | | Chưa triển khai CP1: thiếu correlation_id và log enrichment |
| `validate_dashboard.py` | 6/6 panel hợp lệ | | Đạt cấu hình schema contract ban đầu |
| `pytest` | 22/22 passed | | Toàn bộ unit tests khởi đầu đã pass |
| Số traces hợp lệ | 20 traces (`lab-agent-run`) | | Traces gửi thành công lên project Langfuse cá nhân `day13-k4-l3a-2A202602877` |
| Số PII leak | 0 leak | | `validate_logs.py` chưa phát hiện PII leak trong sample ban đầu |
| Latency P95 / TTFT P95 | Latency P95: 693ms / TTFT P95: 50ms | | Đo được từ 20 requests baseline (P50 latency: 268ms) |
| Retrieval success rate | 100% (20/20) | | Chưa có incident nào được kích hoạt |

## 4. Logging và PII

- **Cách tạo/nhận và truyền correlation ID:** Tại middleware `CorrelationIdMiddleware`, trước mỗi request gọi `clear_contextvars()` để dọn sạch context cũ tránh rò rỉ context giữa các request. Kiểm tra header `x-request-id` từ client, nếu có thì tái sử dụng, nếu không có thì sinh mới theo format `req-<8-char-hex>` (`f"req-{uuid.uuid4().hex[:8]}"`). Gán ID vào `request.state.correlation_id` và gọi `bind_contextvars(correlation_id=correlation_id)`. Sau khi xử lý request, middleware ghi `x-request-id` và `x-response-time-ms` vào response headers.
- **Các metadata được ghi vào structured log:** Các trường chuẩn gồm `ts` (ISO UTC), `level`, `service`, `event`, `correlation_id`, `env`, cùng context enrichment gồm `user_id_hash` (băm SHA-256 rút gọn 12 ký tự), `session_id`, `feature`, `model` được bind qua `structlog.contextvars.bind_contextvars` ngay đầu route `/chat` trong `app/main.py`. Ngoài ra các log sau xử lý còn ghi nhận `latency_ms`, `ttft_ms`, `tokens_in`, `tokens_out`, `cost_usd`, `quality_score`, `tool_name`, `tool_success` và `payload`.
- **Cách bảo đảm PII được scrub trước khi ghi:** Xây dựng processor `scrub_event` trong `app/logging_config.py` và đặt nó trong chuỗi structlog processors trước `JsonlFileProcessor` và `JSONRenderer`. Hàm `scrub_event` duyệt đệ quy toàn bộ cấu trúc event dictionary (string, dict, list) và áp dụng hàm `scrub_text()` từ `app/pii.py`. Các regex pattern trong `PII_PATTERNS` bao gồm email, số điện thoại Việt Nam (`+84` / `0`), CCCD (12 chữ số) và thẻ thanh toán (16 chữ số), thay thế các phần tử nhạy cảm thành `[REDACTED_EMAIL]`, `[REDACTED_PHONE_VN]`, `[REDACTED_CCCD]`, `[REDACTED_CREDIT_CARD]` trước khi serialize ra JSON hoặc ghi vào `data/logs.jsonl`.
- **Cách kiểm chứng kết quả:** Chạy bộ test unit `pytest` (25/25 passed bao gồm các test cases mới cho CCCD, Credit Card, header correlation ID và log enrichment). Chạy script chuẩn `python scripts/validate_logs.py` đạt điểm tuyệt đối 100/100, xác nhận 0 record thiếu required fields/enrichment, nhận diện đầy đủ correlation IDs và 0 PII leak.


## 5. Tracing và prompt versioning

- **Cách xác nhận traces do chính tôi tạo trong project cá nhân:**
- **Cấu trúc root/retrieval/generation observations:**
- **Cách nối trace với log:**
- **Prompt name:**
- **Version/label baseline:**
- **Version/label candidate:**
- **Trace ID của mỗi version:**
- **Cách promote và rollback `production`:**

## 6. Dashboard, SLO và alerts

- **Dashboard và sáu panel:**
- **SLO và lý do chọn:**
- **Cách tính error budget:**
- **Ba alert và runbook tương ứng:**

## 7. Điều tra challenge

- **Challenge ID:**
- **Khoảng thời gian điều tra:**
- **Triệu chứng từ metrics:**
- **Log line và correlation ID liên quan:**
- **Trace ID và span gây ảnh hưởng:**
- **Root cause:**
- **Fix action:**
- **Preventive measure:**

## 8. Giải thích và tự đánh giá

- **Một quyết định kỹ thuật quan trọng và lý do:**
- **Một lỗi/blocker đã gặp:**
- **Cách tìm nguyên nhân và xử lý:**
- **Cách hiểu luồng Metrics → Logs → Traces:**
- **Vai trò của prompt version, token/cost, SLO hoặc rollback trong vận hành LLM:**
- **Điều quan trọng nhất đã học:**
- **Hạn chế hoặc phần chưa hoàn thành, nếu có:**

## 9. Checklist trước khi nộp

- [ ] Kết quả và evidence thuộc commit SHA cuối.
- [ ] Tất cả ảnh/output mở được bằng đường dẫn tương đối.
- [ ] Incident evidence nối đúng metric → log → trace.
- [ ] Trace/prompt evidence thuộc project Langfuse cá nhân và ảnh không lộ key/secret.
- [ ] Repository chạy lại được theo README.
- [ ] Không có secret, API key, PII thô hoặc evidence của người khác/lớp khác.
- [ ] URL repo và commit SHA cuối đã được nộp trên LMS/Codelabs.

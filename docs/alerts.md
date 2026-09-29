# Template Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert 1

- Tên: api_latency_p95_breach
- Severity: warning
- Duration: 3m
- Kênh thông báo: Slack (#alerts-llmops)
- SLI/SLO liên quan: `fast_successful_requests` (SLO 99.5%, latency <= 3000ms trong 28 ngày)
- Điều kiện và thời gian duy trì: Latency P95 > 3000ms duy trì liên tục trong 3 phút
- Ảnh hưởng tới người dùng: Trải nghiệm chatbot phản hồi chậm rõ rệt (lag, chờ lâu hoặc timeout ở phía frontend)
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard panel `Latency percentiles and TTFT` để xác nhận hiện tượng P95 tăng vọt và kiểm tra xem TTFT có tăng tương ứng hay không.
  2. Lọc file `data/logs.jsonl` tìm các event `response_sent` có `latency_ms > 3000`, trích xuất `correlation_id` của request bất thường.
  3. Mở trace tương ứng trên Langfuse Cloud, so sánh span `retrieval` và span `generation` để phân lập bước gây trễ (do retrieval chậm như `rag_slow` hay LLM sinh token chậm).
- Mitigation tạm thời: Bật cache phản hồi RAG, giảm tạm thời số tài liệu truy vấn (top_k), hoặc chuyển hướng sang cụm replica / fallback nhanh.
- Owner: oncall-llmops

## Alert 2

- Tên: retrieval_error_rate_high
- Severity: critical
- Duration: 2m
- Kênh thông báo: Slack (#alerts-critical)
- SLI/SLO liên quan: Guardrail `error_rate_pct_max <= 2%` và `retrieval_success_rate_pct_min >= 90%`
- Điều kiện và thời gian duy trì: Tỷ lệ lỗi API > 2% hoặc tỷ lệ truy xuất thành công < 90% duy trì liên tục trong 2 phút
- Ảnh hưởng tới người dùng: Request thất bại trả mã lỗi 500, người dùng nhận thông báo lỗi hệ thống không thể trả lời
- Ba bước kiểm tra đầu tiên:
  1. Kiểm tra dashboard panel `Error rate and retrieval success`, phân loại error_type đang tăng đột biến.
  2. Lọc log `request_failed` trong `data/logs.jsonl` xem chi tiết exception trong `payload.detail` (ví dụ `Vector store timeout`).
  3. Tra cứu trace ID trên Langfuse để xem thông tin lỗi tại child observation `retrieval`.
- Mitigation tạm thời: Khởi động lại service vector store hoặc kích hoạt chế độ degraded fallback (sử dụng LLM sinh câu trả lời dự phòng không qua retrieval).
- Owner: oncall-rag-platform

## Alert 3

- Tên: cost_token_burn_spike
- Severity: warning
- Duration: 5m
- Kênh thông báo: Slack (#alerts-finance-ops)
- SLI/SLO liên quan: Guardrail `daily_cost_usd_max <= $2.5`
- Điều kiện và thời gian duy trì: Chi phí ước tính ngày vượt $2.5 hoặc tốc độ output tokens vượt 10,000 tokens/phút duy trì trong 5 phút
- Ảnh hưởng tới người dùng: Người dùng có thể nhận phản hồi quá dài, lặp lại; nguy cơ cạn kiệt hạn mức quota API của tổ chức
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard panel `Cost over time` và `Input and output tokens` để xác định thời điểm bắt đầu spike và mức độ tiêu hao token.
  2. Lọc log `response_sent` tìm các bản ghi có `tokens_out` hoặc `cost_usd` cao đột biến, xác định `user_id_hash`, `session_id`, `feature`.
  3. Mở trace tương ứng trên Langfuse kiểm tra prompt và output text của LLM để phát hiện loop hoặc tấn công prompt injection/token consumption.
- Mitigation tạm thời: Áp dụng trần giới hạn `max_tokens` chặt chẽ hơn (ví dụ 150-200 tokens) cho model, áp dụng rate limiting cho session/user liên quan.
- Owner: oncall-finance-ops


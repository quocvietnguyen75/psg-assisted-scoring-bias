# Báo cáo M1 — respiratory

Thời gian UTC: 2026-10-27T16:03:22.539412+00:00. Nguồn: PSG-IPA 1.0.0; 125 annotation đã khớp SHA-256.
Protocol 001, S1 PDF trang 3–4. Mỗi bản ghi lấy trung bình 12 hiệu F1(assisted,auto) − F1(manual,auto).

| Bản ghi | M1 trung bình |
|---|---:|
| SN1 | 0.098 |
| SN2 | 0.109 |
| SN3 | 0.038 |
| SN4 | 0.194 |
| SN5 | 0.208 |

Trung bình tác vụ: **0.129296**. Có 5/5 bản ghi có M1 dương.
Giá trị trung bình dương: assisted gần auto hơn manual.
Đây là mô tả mức đồng thuận, không xác định độ chính xác hay quan hệ nhân quả.
Không áp dụng kết luận thống kê toàn bài từ riêng tác vụ này; chưa tính M2, bootstrap hoặc kiểm định chung.

Ghép theo giao dương lớn nhất, một–một; chạm biên không là giao. Không gộp sự kiện hoặc lọc thời lượng tối thiểu.
Tie được xử lý theo thứ tự onset/end rồi chỉ số; protocol không quy định tie.
Số xung đột tie phát hiện trong các phép so sánh: **14**. Nếu khác kết quả gốc, cần kiểm tra tie trước khi kết luận lỗi.

**Đối chiếu:** chưa đối chiếu bảng M1 từng bản ghi của phân tích gốc; chưa tuyên bố verified trong 0.001.
Ngưỡng 0.001 được dùng lại từ quy trình D2 staging như tiêu chí đối chiếu cho phần mở rộng này.

**Khai báo:** có AI hỗ trợ; trợ lý đã xem kết quả bản thảo. Không phải kiểm chứng mù độc lập do con người.
Không đọc/import code phân tích gốc. Code staging kiểm chứng được dùng lại cho đọc CSV, cửa sổ và tải dữ liệu.
Chi tiết từng người nằm trong scorer_summary.csv; hash và kiểm tra đầu vào nằm trong provenance.json.

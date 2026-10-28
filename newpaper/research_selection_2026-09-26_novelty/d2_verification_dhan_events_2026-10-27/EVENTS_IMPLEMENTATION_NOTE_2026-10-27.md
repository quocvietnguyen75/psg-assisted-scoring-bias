# Ghi chú triển khai bổ sung M1 sự kiện — 27/10/2026

## Phạm vi được giao

Mở rộng bộ kiểm chứng staging sang ba tác vụ arousals, respiratory và limb, chỉ tính M1.
Không thay đổi protocol 001 hay bản thảo. Không tính lại M2, M3–M5, consensus, bootstrap hoặc kết luận thống kê toàn bài.

## Cơ sở triển khai

Đọc trực tiếp protocol 001 và operational clarifications trong S1 PDF trang 3–4.
Dùng lại tiện ích I/O của bộ kiểm chứng staging (`d2.py`), không đọc/import code phân tích gốc.
Đã xem một số kết quả trong bản thảo trước công việc này; không được gọi là kiểm chứng mù độc lập do con người.
Có AI hỗ trợ; không dùng số gốc để chọn hoặc chỉnh thuật toán cho khớp.

Quy tắc ghép là greedy theo giao dương dài nhất, không phải maximum-cardinality matching hoặc tối ưu tổng overlap.
Tie chưa có quy định trong protocol: sắp event theo onset/end rồi chỉ số cặp; ghi số xung đột tie trong từng phép so sánh.
Người chấm là đối số trái và auto là đối số phải, giữ nhất quán trong hai điều kiện.
Sự kiện sau clipping vẫn là từng event riêng, không gộp event cùng/khác kênh hoặc subtype hô hấp.
Những quy ước này được ghi trước lần phân tích event thật đầu tiên.

## Kiểm thử trước dữ liệu thật

Mỗi tác vụ có sáu kiểm thử: nhãn/clipping, danh sách rỗng/chạm biên, greedy matching với ví dụ phân biệt maximum cardinality,
tie, M1 có đáp án tính tay (dương/âm/0), và đầu vào không hợp lệ.
Kiểm thử tích hợp tạo 125 annotation giả cho từng tác vụ, xác minh bảng 5 bản ghi và 60 ô người–bản ghi,
hash, chống ghi đè và từ chối dữ liệu bị sửa. Các kiểm thử này đã qua trước lần phân tích thật đầu tiên.
Năm kiểm thử staging hiện có cũng đã qua.

## Thực thi và đối chiếu

Mỗi lần chạy xuất một thư mục UTC riêng. Không ghi đè kết quả cũ.
Kiểm tra đủ 125 checksum của mỗi tác vụ trước phân tích; không tuyên bố đã kiểm tra toàn bộ 1.025 file của nghiên cứu gốc.
`download_events.py` là tiện ích tải tiếp cả ba tác vụ khi mạng không ổn định:

```powershell
python -X utf8 d2_verification/download_events.py
```

Đối chiếu từng bản ghi với bảng gốc là bước sau bàn giao; chưa thực hiện thì trạng thái là chưa đối chiếu.
Tiêu chí sai khác tuyệt đối ≤ 0,001 được dùng lại từ D2 staging cho phần mở rộng này.
Nếu cần sửa lỗi sau phân tích thật: thêm ghi chú có ngày, mô tả nguyên nhân và giữ cả đầu ra trước/sau.

## Thực thi đã hoàn thành

Đường tải trực tiếp PhysioNet timeout nhiều lần. Trước phân tích thật đã chuyển tải annotation và manifest
sang kho public S3 `https://physionet-open.s3.amazonaws.com/psg-ipa/1.0.0/`, kiểm tra đủ 375 checksum.
Đây là thay đổi đường truyền, không thay đổi bộ dữ liệu hoặc phương pháp tính.
Ba lần phân tích thật đầu tiên nằm trong `arousals/runs/20261027T160320146973Z`,
`respiratory/runs/20261027T160320180578Z`, `limb/runs/20261027T160320217046Z`.
Không có sửa thuật toán sau các lần chạy này. Báo cáo bàn giao: [EVENTS_REPORT_VI.md](EVENTS_REPORT_VI.md).

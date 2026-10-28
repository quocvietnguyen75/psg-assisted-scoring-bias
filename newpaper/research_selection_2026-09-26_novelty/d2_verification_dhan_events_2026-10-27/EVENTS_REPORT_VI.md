# Bàn giao bổ sung M1 cho ba tác vụ sự kiện

Ngày thực hiện: 27/10/2026 (UTC+07:00). Code có AI hỗ trợ, được triển khai từ protocol 001 trong S1 PDF trang 3–4.
Đây là phần mở rộng theo yêu cầu mới, không thay đổi D2 staging hoặc bản thảo.

## Kết quả

Mỗi ô là trung bình 12 người chấm của F1(assisted,auto) − F1(manual,auto).
Không làm tròn trung gian. Bảng dưới làm tròn ba chữ số; bản đầy đủ ở thư mục lần chạy từng tác vụ.

| Bản ghi | Vi thức giấc | Hô hấp | Cử động chi |
|---|---:|---:|---:|
| SN1 | -0.002 | 0.098 | 0.149 |
| SN2 | 0.162 | 0.109 | 0.118 |
| SN3 | 0.073 | 0.038 | 0.063 |
| SN4 | 0.022 | 0.194 | 0.055 |
| SN5 | 0.075 | 0.208 | 0.132 |
| Trung bình | **0.066** | **0.129** | **0.103** |

Trung bình dương ở cả ba tác vụ: assisted giống auto hơn manual theo event-level F1.
Vi thức giấc SN1 hơi âm; báo cáo giữ nguyên kết quả này.
Không suy ra độ chính xác hoặc quan hệ nhân quả, không áp dụng quy tắc kết luận chính toàn bài khi chưa có M2 và kiểm định đủ 20 đơn vị.

## Tài liệu và file bàn giao

- **Vi thức giấc:** [README](arousals/README_VI.md), [báo cáo](arousals/REPORT_VI.md), [kết quả](arousals/runs/20261027T160320146973Z/results_3dp.csv).
- **Hô hấp:** [README](respiratory/README_VI.md), [báo cáo](respiratory/REPORT_VI.md), [kết quả](respiratory/runs/20261027T160320180578Z/results_3dp.csv).
- **Cử động chi:** [README](limb/README_VI.md), [báo cáo](limb/REPORT_VI.md), [kết quả](limb/runs/20261027T160320217046Z/results_3dp.csv).
- [Bảng chung 15 dòng](event_m1_results_3dp.csv), [ghi chú triển khai](EVENTS_IMPLEMENTATION_NOTE_2026-10-27.md), [code F1/M1 dùng chung](event_m1.py).

Mỗi thư mục tác vụ có lệnh chạy, kiểm thử và thư mục `runs/` chứa bảng M1, hai F1 của 60 ô người–bản ghi,
số event/cặp ghép, thống kê tie và provenance (hash code/protocol/manifest/dữ liệu).
Các wrapper dùng code chung để tránh ba bản triển khai F1 khác nhau; cần giữ `event_m1.py` và `d2.py` khi bàn giao.

## Kiểm tra đã hoàn thành

- 375 annotation sự kiện, mỗi tác vụ 125 TXT, đã khớp SHA-256 theo manifest PSG-IPA 1.0.0.
- Đường tải trực tiếp PhysioNet timeout; tải tiếp từ kho public `physionet-open` S3, giữ kiểm tra hash.
- 24 kiểm thử đã qua: 18 kiểm thử sự kiện, 5 staging và 1 tích hợp chạy đủ ba tác vụ trên dữ liệu giả.
- Đầu ra thật có đủ 5 bản ghi và 60 ô người–bản ghi cho từng tác vụ; đã kiểm tra trung bình từ chi tiết khớp bảng chính.
- Giữ nguyên phần staging và những file người dùng đang làm.

## Giới hạn và bước còn lại

**Chưa đối chiếu với bảng M1 từng bản ghi của phân tích gốc; chưa tuyên bố verified trong 0,001.**
Sau bàn giao, đối chiếu từng đơn vị và điều tra nếu sai khác lớn hơn 0,001 (tiêu chí dùng lại từ D2 staging).
Chưa thực hiện clean re-run toàn pipeline; công việc này chỉ kiểm chứng M1 của sự kiện.

Protocol không quy định tie khi giao dài bằng nhau. Code dùng thứ tự onset/end rồi chỉ số cặp, cố định người chấm là đối số trái.
Số xung đột tie phát hiện là 2 ở arousals, 14 ở respiratory và 749 ở limb; đây là số xung đột cặp ứng viên,
không phải số sai khác F1 hoặc số người chấm. Nếu có sai khác với gốc cần kiểm tra quy tắc này.

**Khai báo:** có AI hỗ trợ và trợ lý đã xem kết quả bản thảo trước khi viết code; không phải kiểm chứng mù độc lập do con người.
Không đọc/import code phân tích gốc `src/careport/`; chỉ tái sử dụng tiện ích của bộ kiểm chứng staging.
Người thực hiện cần khai báo trung thực về việc đã xem code/kết quả khi gửi tác giả liên hệ.

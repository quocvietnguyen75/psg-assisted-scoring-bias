# Báo cáo triển khai D2

Ngày hoàn tất phần tính toán: 22/10/2026, múi giờ Asia/Saigon.

## Trạng thái

Đã viết code từ định nghĩa protocol 001 và chạy trên 5 bản ghi staging SN1–SN5.
Không đọc/import code phân tích gốc. Chưa đối chiếu với kết quả gốc để kết luận
đạt ngưỡng sai khác 0.001. Chưa thực hiện clean re-run toàn bộ nghiên cứu vì chưa
có repository phân tích đầy đủ.

## Kết quả

| Recording | Mean M1 | Δauto | Δhuman | DiD |
|---|---:|---:|---:|---:|
| SN1 | 0.095 | 0.062 | -0.012 | 0.074 |
| SN2 | 0.112 | 0.102 | -0.014 | 0.117 |
| SN3 | 0.065 | 0.056 | -0.022 | 0.078 |
| SN4 | 0.055 | 0.064 | -0.011 | 0.074 |
| SN5 | 0.078 | 0.090 | -0.020 | 0.110 |

Mỗi đại lượng được làm tròn độc lập sau khi tính đủ độ chính xác. Vì vậy phép trừ
các cột đã làm tròn có thể chênh 0.001 so với DiD được xuất.

Đầu ra gốc nằm trong `runs/20261022T003025897739Z/`: kết quả đầy đủ, kết quả 3 chữ
số, tóm tắt theo chuyên gia và provenance. Không xuất nhãn theo epoch.

## Kiểm tra

- 125 annotation khớp SHA-256 trong manifest do PhysioNet công bố.
- Năm kiểm thử trên dữ liệu giả đều đạt trước lượt phân tích thật, gồm 50 cặp
  kappa ngẫu nhiên so với scikit-learn và fixture M1/M2 tính tay.
- 5,103 epoch nằm trong cửa sổ phân tích: SN1 896, SN2 725, SN3 1,635,
  SN4 961, SN5 886.
- Không có epoch thiếu nhãn trong cửa sổ ở 25 chuỗi của mỗi bản ghi.
  Một số epoch không đủ phiếu tạo consensus; được loại riêng trong từng so sánh.
- Không có midpoint trùng Lights off hoặc Lights on, nên quy ước biên không ảnh
  hưởng kết quả của bộ dữ liệu này.
- Không chỉnh công thức hoặc dữ liệu dựa trên việc so khớp kết quả paper.

## Khai báo để gửi tác giả liên hệ

> Tôi triển khai D2 với sự hỗ trợ của Codex từ protocol và annotation PSG-IPA.
> Code triển khai không đọc hoặc sử dụng code phân tích gốc của nghiên cứu.
> Tuy nhiên, trong hội thoại trước khi triển khai, trợ lý AI đã xem một số bảng
> kết quả của bản thảo. Vì vậy tôi khai báo việc hỗ trợ AI và sự tiếp xúc đó,
> không xác nhận đây là kiểm chứng mù hoàn toàn do con người tự thực hiện.
> Xin tác giả liên hệ đánh giá điều kiện độc lập của D2 và đối chiếu bảng đính kèm
> với kết quả gốc theo ngưỡng 0.001.

Đây là bản nháp nội dung bàn giao; người phụ trách phải kiểm tra, chỉnh lại theo
những tài liệu chính mình đã xem và chỉ xác nhận các thông tin đúng thực tế.

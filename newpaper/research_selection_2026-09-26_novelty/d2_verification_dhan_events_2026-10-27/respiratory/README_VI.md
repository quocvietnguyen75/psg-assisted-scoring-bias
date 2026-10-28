Nguồn `Resp_events/Annotations/` gồm 5 bản ghi SN1–SN5; mỗi bản ghi có 1 auto, 12 manual và 12 semiauto (assisted): **125 TXT**.
Ghép manual/semiauto theo cùng scorer1–scorer12 trong tác vụ.

- `auto/SN<r>_Respiration_auto.txt`
- `manual/SN<r>_Respiration_manual_scorer<s>.txt`
- `semiauto/SN<r>_Respiration_semiauto_scorer<s>.txt`

Chỉ giữ nhãn **`Obstructive apnea`, `Central apnea`, `Mixed apnea`, `Hypopnea`, `Central hypopnea` (gộp chung, loại RERA)**; bỏ annotation ngữ cảnh khác.
Các cột CSV là `Recording onset` (giây từ đầu bản ghi), `Duration` (giây), `Annotation`.

## Cách xử lý và đo

1. Lấy Lights off/on từ **auto của chính tác vụ và bản ghi**.
2. Cắt sự kiện theo cửa sổ `[off,on)`; bỏ ngoài cửa sổ hoặc phần không còn thời lượng dương.
3. Không gộp event, không lọc thêm thời lượng tối thiểu. Không dùng epoch 30 giây hoặc lưới consensus 0,1 giây cho M1.
4. Ghép event người chấm với auto một–một theo độ dài giao dương giảm dần; chạm biên không tính là giao. Không áp dụng ngưỡng IoU.
5. **F1 = 2 × số cặp ghép / tổng số event hai danh sách.** Cả hai rỗng: F1 = 1; chỉ một rỗng: F1 = 0.
6. **M1(s,r) = F1(assisted(s,r),auto(r)) − F1(manual(s,r),auto(r)).** Trung bình 12 người cho mỗi bản ghi; trung bình 5 bản ghi cho tác vụ.

Không làm tròn trung gian. M1 không cần consensus.
Protocol chưa quy định phá tie: code sắp event theo onset/end, sau đó theo chỉ số cặp khi giao bằng nhau;
đếm xung đột tie trong kết quả để điều tra nếu khác phân tích gốc. Không chọn cách phá tie để ép khớp số gốc.

## Chạy

Python 3.10+, chỉ thư viện chuẩn. Từ thư mục gốc dự án:

```powershell
python -X utf8 -m unittest discover -s d2_verification/respiratory -v
python -X utf8 d2_verification/respiratory/run.py download
python -X utf8 d2_verification/respiratory/run.py analyze
```

Download lấy 125 TXT và SHA256SUMS.txt từ kho public S3 `physionet-open` của PhysioNet, kiểm tra hash từng file; không cần EDF.
Kho tải: https://physionet-open.s3.amazonaws.com/psg-ipa/1.0.0/. Hash khớp manifest cùng phiên bản trên PhysioNet.
Cache dùng chung `d2_verification/data/psg-ipa/1.0.0/` được Git bỏ qua.
Có dữ liệu sẵn: dùng `analyze --data-root "E:\duong_dan\psg-ipa\1.0.0"`.
Có thể chọn `--output` tới thư mục mới; chương trình từ chối ghi đè output cũ.
Thiếu file, sai checksum, marker hoặc duration không hợp lệ sẽ gây lỗi.
Hash ở đây kiểm tra 125 đầu vào của tác vụ, không xác minh toàn bộ 1.025 file của pipeline gốc.

## Các file và đầu ra

- `run.py`: lệnh riêng; dùng [event_m1.py](../event_m1.py) và I/O trong [d2.py](../d2.py).
- `test_respiratory.py`: kiểm thử đúng nhãn, clipping, F1 rỗng/chạm biên, greedy matching, tie và M1 tính tay.
- `REPORT_VI.md`: báo cáo lần chạy bàn giao.
- `runs/<UTC>/results_full.csv`, `results_3dp.csv`: 5 giá trị M1 theo bản ghi.
- `runs/<UTC>/scorer_summary.csv`: 60 ô người–bản ghi, hai F1, M1, số event, số cặp ghép và tie.
- `runs/<UTC>/task_summary.csv`: trung bình tác vụ và số bản ghi M1 dương.
- `runs/<UTC>/provenance.json`: hash code, protocol, manifest, 125 đầu vào; cửa sổ, vocabulary và khai báo AI.
- `runs/<UTC>/REPORT_VI.md`: báo cáo tự sinh cho mỗi lần chạy. Chỉ lưu thống kê, không xuất event cá nhân.

## Kết luận và đối chiếu

M1 dương: assisted gần auto hơn manual; âm: ít giống hơn; bằng 0: không đổi theo phép đo này.
Không suy ra chính xác hơn, thuật toán đúng hơn hoặc quan hệ nhân quả.
Không dùng riêng tác vụ này để tuyên bố kết luận chính toàn bài, vốn cần cả M1, M2 và 20 đơn vị.

Sau bàn giao mới đối chiếu bảng gốc từng bản ghi. Dùng lại tiêu chí D2 staging:
sai khác tuyệt đối ≤ 0,001 là khớp; lớn hơn cần điều tra nhãn, cửa sổ, clipping, matching/tie và ghi nguyên nhân.
Chưa đối chiếu không gọi là verified. Sửa lỗi sau chạy thật cần ghi chú có ngày và giữ cả output cũ/mới.


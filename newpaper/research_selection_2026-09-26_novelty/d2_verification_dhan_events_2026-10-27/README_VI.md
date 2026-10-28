# D2: triển khai kiểm chứng phân giai đoạn ngủ

## Phần mở rộng M1 cho sự kiện (27/10/2026)

Ba tác vụ có thư mục riêng, gồm hướng dẫn, lệnh chạy, kiểm thử và báo cáo:

- [Vi thức giấc EEG](arousals/README_VI.md)
- [Sự kiện hô hấp](respiratory/README_VI.md)
- [Cử động chi](limb/README_VI.md)

Phần mở rộng chỉ tính **M1 bằng event-level F1** theo protocol 001; không tính M2 của sự kiện.
Code F1 dùng chung trong `event_m1.py`, dữ liệu annotation dùng chung trong `data/`.
Xem [báo cáo bàn giao ba tác vụ](EVENTS_REPORT_VI.md) và [bảng chung 15 dòng](event_m1_results_3dp.csv).
Kiểm thử tích hợp ba tác vụ: `python -X utf8 -m unittest discover -s d2_verification -p test_event_m1.py -v`.
Các giới hạn về tính độc lập và khai báo AI ở dưới vẫn áp dụng.

## Phạm vi và tính độc lập

Code `d2.py` được viết từ protocol 001 trong Supplementary File S1, trang 3–5,
và hướng dẫn `team_tasks/D2_REIMPLEMENTATION_TASK.md`. Không đọc/import code gốc
`src/careport/`; không dùng giá trị của bài làm điều kiện để chỉnh code.

**Khai báo bắt buộc khi bàn giao:** đây là triển khai có AI hỗ trợ. Trong hội thoại
trước khi triển khai, trợ lý đã đọc một số bảng kết quả trong bản thảo. Do đó không
được gọi sản phẩm này là kiểm chứng mù do con người tự thực hiện, hoặc ký xác nhận
chưa xem kết quả thay cho người làm. Tác giả liên hệ cần quyết định liệu cách kiểm
chứng này đáp ứng D2 hay cần thêm người đủ điều kiện thực hiện độc lập.

## Chạy trên PowerShell, từ thư mục gốc dự án

Chương trình chính chỉ dùng thư viện chuẩn Python 3.10 trở lên. Kiểm thử đối chiếu
kappa cần scikit-learn (đã có trong môi trường triển khai).

```powershell
python -X utf8 -m unittest discover -s d2_verification -v
python -X utf8 d2_verification/d2.py download
python -X utf8 d2_verification/d2.py analyze
```

Lệnh download chỉ tải 125 file annotation cùng SHA256SUMS từ PSG-IPA 1.0.0:
https://physionet.org/content/psg-ipa/1.0.0/
Mỗi file bắt buộc khớp SHA-256 do nguồn công bố. Không cần EDF hay huấn luyện model.

Nếu đã có dữ liệu, dùng:

```powershell
python -X utf8 d2_verification/d2.py analyze --data-root "E:\duong_dan\psg-ipa\1.0.0"
```

Thư mục dữ liệu phải chứa SHA256SUMS.txt và Sleep_stages/Annotations/.

## Quy tắc tính

- Epoch 30 giây, căn từ thời điểm bắt đầu bản ghi; lấy nhãn ở midpoint.
- Cửa sổ: lights_off <= midpoint < lights_on, lấy marker từ pre-fill.
  Quy ước biên này được ghi lại; metadata kiểm tra có midpoint trùng biên không.
- Annotation theo khoảng [onset, onset + duration); bỏ annotation ngữ cảnh khác tác vụ.
- Chỉ W, N1, N2, N3, R là hợp lệ. Thiếu nhãn/nhãn khác là unscored.
- Loại unscored riêng trong từng phép tính kappa, không ép mọi phép tính dùng cùng tập epoch.
- Consensus 7/12; leave-one-out 6/11. Không hạ ngưỡng khi có người thiếu nhãn.
- M1: trung bình 12 người của kappa(assisted,auto) - kappa(manual,auto).
- delta_auto: kappa(auto,assisted consensus) - kappa(auto,manual consensus).
- delta_human: trung bình 12 người của kappa(manual người đó,assisted consensus
  của 11 người khác) - kappa(manual người đó,manual consensus của 11 người khác).
- DiD = delta_auto - delta_human.
- Không làm tròn trung gian. Dừng nếu không có cặp hợp lệ hoặc kappa không xác định.

## Đầu ra

Mỗi lần chạy tạo thư mục thời gian riêng trong `runs/`, giữ nguyên lần chạy trước:

- `results_3dp.csv`: bảng SN1–SN5, bốn chỉ số làm tròn ba chữ số để bàn giao.
- `results_full.csv`: kết quả đủ độ chính xác.
- `scorer_summary.csv`: các đại lượng tóm tắt theo chuyên gia, phục vụ kiểm tra.
- `provenance.json`: thời gian UTC, phiên bản Python, hash code/protocol/dữ liệu,
  thông tin cửa sổ, số epoch thiếu nhãn và số epoch có consensus.

Không xuất nhãn theo epoch. Dữ liệu tải về và cache Python nằm trong .gitignore.

## Kiểm thử trước dữ liệu thật

Kiểm thử bao gồm kappa tính tay; 50 cặp dữ liệu giả so với scikit-learn;
ngưỡng consensus/leave-one-out và nhãn thiếu; căn epoch/cửa sổ/annotation
ngữ cảnh; bộ dữ liệu giả có M1, delta_auto, delta_human và DiD biết trước.

## Bàn giao và phần còn lại

Gửi bảng kết quả, code, tài liệu này và khai báo AI cho tác giả liên hệ; không
tự gửi thông điệp xác nhận độc lập không đúng thực tế. Chưa đối chiếu số liệu với
báo cáo gốc. Việc đối chiếu sau bàn giao dùng ngưỡng 0.001 trong task; mọi sai khác
lớn hơn phải điều tra, ghi nguyên nhân và giữ đầu ra trước/sau sửa.

Phần clean re-run chưa thể thực hiện từ gói Overleaf này: cần repository phân tích
đầy đủ và hướng dẫn chạy protocol/amendment/build. Sau khi có repository, dùng
bản checkout mới và dữ liệu tải mới, chạy toàn bộ rồi so sánh byte-for-byte
`generated/values.tex`. 125 annotation ở đây chỉ đủ cho phần triển khai staging,
không đủ cho toàn bộ pipeline.

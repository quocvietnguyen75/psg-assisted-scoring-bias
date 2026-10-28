"""Protocol 001 event M1; shared implementation, standard library only."""
from __future__ import annotations
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import platform
from d2 import BASE, fetch_bytes, lights_window, read_annotations

HERE = Path(__file__).resolve().parent
DOWNLOAD_BASE = 'https://physionet-open.s3.amazonaws.com/psg-ipa/1.0.0/'
TASKS = {
    'arousals': ('EEG_arousals', 'EEGarousals', {'EEG arousal'}),
    'respiratory': ('Resp_events', 'Respiration', {
        'Obstructive apnea', 'Central apnea', 'Mixed apnea', 'Hypopnea', 'Central hypopnea'}),
    'limb': ('Limb_movements', 'LimbMovements', {'Limb movement'}),
}
DISCLOSURE = ('AI-assisted implementation from protocol text; assistant has seen manuscript results. '
              'Not blind independent human verification. Original study analysis code not imported or read.')


def names(task):
    folder, stem, _ = TASKS[task]
    for r in range(1, 6):
        yield f'{folder}/Annotations/auto/SN{r}_{stem}_auto.txt'
        for condition in ('manual', 'semiauto'):
            for s in range(1, 13):
                yield f'{folder}/Annotations/{condition}/SN{r}_{stem}_{condition}_scorer{s}.txt'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest_entries(content):
    return {name.lstrip('*').removeprefix('./'): digest
            for digest, name in (line.split(maxsplit=1) for line in content.splitlines() if line.strip())}


def download(task, root):
    content = fetch_bytes(DOWNLOAD_BASE + 'SHA256SUMS.txt')
    expected = manifest_entries(content.decode())
    def one(name):
        path = root / name
        if path.exists() and sha(path) == expected[name]:
            return
        data = fetch_bytes(DOWNLOAD_BASE + name)
        if hashlib.sha256(data).hexdigest() != expected[name]:
            raise ValueError(f'Checksum mismatch: {name}')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    with ThreadPoolExecutor(max_workers=6) as pool:
        list(pool.map(one, names(task)))
    (root / 'SHA256SUMS.txt').write_bytes(content)
    print(f'{task}: 125 annotations SHA-256 verified.')


def events(rows, labels, window):
    off, on = window
    result = []
    for onset, duration, label in rows:
        if label not in labels:
            continue
        if not math.isfinite(onset) or not math.isfinite(duration) or duration <= 0:
            raise ValueError('Event onset must be finite and duration positive and finite.')
        start, end = max(off, onset), min(on, onset + duration)
        if start < end:
            result.append((start, end))
    # Do not merge adjacent/overlapping annotations: each row is an event.
    return sorted(result)


def match_events(left, right):
    """Greedy largest positive intersection; ties use sorted event indices.

    Protocol does not specify a tie rule. Record ambiguity whenever equal-overlap
    candidates share an endpoint; this can make the resulting match depend on ties.
    """
    candidates = []
    for i, (a, b) in enumerate(left):
        for j, (c, d) in enumerate(right):
            overlap = min(b, d) - max(a, c)
            if overlap > 0:
                candidates.append((-overlap, i, j))
    candidates.sort()
    used_l, used_r = set(), set()
    matches, tie_conflicts = [], 0
    for k, (negative, i, j) in enumerate(candidates):
        if i in used_l or j in used_r:
            continue
        for other, x, y in candidates[k + 1:]:
            if other != negative:
                break
            if x not in used_l and y not in used_r and (x == i or y == j):
                tie_conflicts += 1
        used_l.add(i)
        used_r.add(j)
        matches.append((i, j))
    n = len(left) + len(right)
    return {'F1': 2 * len(matches) / n if n else 1.0,
            'matched': len(matches), 'tie_conflicts': tie_conflicts}


def m1(auto, manual, assisted):
    if len(manual) != 12 or len(assisted) != 12:
        raise ValueError('Exactly 12 matched scorers required.')
    details = []
    for s, (m, a) in enumerate(zip(manual, assisted), 1):
        fm, fa = match_events(m, auto), match_events(a, auto)
        details.append({'scorer': s, 'manual_events': len(m), 'assisted_events': len(a),
                        'auto_events': len(auto), 'F1_manual_auto': fm['F1'],
                        'F1_assisted_auto': fa['F1'], 'M1': fa['F1'] - fm['F1'],
                        'manual_matches': fm['matched'], 'assisted_matches': fa['matched'],
                        'manual_tie_conflicts': fm['tie_conflicts'],
                        'assisted_tie_conflicts': fa['tie_conflicts']})
    return sum(x['M1'] for x in details) / 12, details


def write_csv(path, rows, rounded=False):
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        for row in rows:
            writer.writerow({k: f'{v:.3f}' if rounded and isinstance(v, float) else v
                             for k, v in row.items()})


def analyze(task, root, output):
    if output.exists():
        raise FileExistsError(f'Refusing to overwrite previous run: {output}')
    expected = manifest_entries((root / 'SHA256SUMS.txt').read_text())
    hashes = {name: sha(root / name) for name in names(task)}
    for name, digest in hashes.items():
        if digest != expected[name]:
            raise ValueError(f'Input checksum mismatch: {name}')
    folder, stem, labels = TASKS[task]
    results, details, quality = [], [], []
    for r in range(1, 6):
        record = f'SN{r}'
        base = root / folder / 'Annotations'
        auto_rows = read_annotations(base / 'auto' / f'{record}_{stem}_auto.txt')
        window = lights_window(auto_rows)
        if not all(math.isfinite(v) for v in window):
            raise ValueError('Non-finite lights window.')
        vocabulary = Counter(label for _, _, label in auto_rows)
        auto = events(auto_rows, labels, window)
        conditions = {}
        for setting in ('manual', 'semiauto'):
            conditions[setting] = []
            for s in range(1, 13):
                rows = read_annotations(base / setting / f'{record}_{stem}_{setting}_scorer{s}.txt')
                vocabulary.update(label for _, _, label in rows)
                conditions[setting].append(events(rows, labels, window))
        value, cells = m1(auto, conditions['manual'], conditions['semiauto'])
        results.append({'recording': record, 'M1': value})
        details.extend({'recording': record, **cell} for cell in cells)
        quality.append({'recording': record, 'lights_off': window[0], 'lights_on': window[1],
                        'label_counts_before_filtering': dict(sorted(vocabulary.items()))})
    mean = sum(row['M1'] for row in results) / 5
    output.mkdir(parents=True)
    write_csv(output / 'results_full.csv', results)
    write_csv(output / 'results_3dp.csv', results, True)
    write_csv(output / 'scorer_summary.csv', details)
    write_csv(output / 'task_summary.csv', [{'task': task, 'mean_M1': mean,
              'positive_recordings': sum(row['M1'] > 0 for row in results),
              'recordings': 5, 'scorers': 12}])
    protocol = HERE.parent / 'submission/supplementary_file_S1_analysis_plans.pdf'
    sources = [Path(__file__), HERE / 'd2.py', HERE / task / 'run.py']
    metadata = {'created_utc': datetime.now(timezone.utc).isoformat(),
                'python': platform.python_version(), 'dataset': 'PSG-IPA 1.0.0', 'source': BASE,
                'download_mirror': DOWNLOAD_BASE,
                'task': task, 'labels': sorted(labels), 'input_sha256': hashes,
                'manifest_sha256': sha(root / 'SHA256SUMS.txt'), 'protocol_pdf_sha256': sha(protocol),
                'code_sha256': {p.name: sha(p) for p in sources}, 'quality': quality,
                'matching': 'greedy descending positive intersection, tie by sorted left/right indices',
                'left_argument': 'human scoring', 'window': '[lights_off, lights_on), clipped events',
                'disclosure': DISCLOSURE, 'comparison_status': 'Not compared with original per-recording results.'}
    (output / 'provenance.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
    ties = sum(x['manual_tie_conflicts'] + x['assisted_tie_conflicts'] for x in details)
    table = '\n'.join(f"| {x['recording']} | {x['M1']:.3f} |" for x in results)
    report = f'''# Báo cáo M1 — {task}

Thời gian UTC: {metadata['created_utc']}. Nguồn: PSG-IPA 1.0.0; 125 annotation đã khớp SHA-256.
Protocol 001, S1 PDF trang 3–4. Mỗi bản ghi lấy trung bình 12 hiệu F1(assisted,auto) − F1(manual,auto).

| Bản ghi | M1 trung bình |
|---|---:|
{table}

Trung bình tác vụ: **{mean:.6f}**. Có {sum(x['M1'] > 0 for x in results)}/5 bản ghi có M1 dương.
Giá trị trung bình {'dương: assisted gần auto hơn manual' if mean > 0 else 'không dương: không thấy dịch chuyển trung bình về auto'}.
Đây là mô tả mức đồng thuận, không xác định độ chính xác hay quan hệ nhân quả.
Không áp dụng kết luận thống kê toàn bài từ riêng tác vụ này; chưa tính M2, bootstrap hoặc kiểm định chung.

Ghép theo giao dương lớn nhất, một–một; chạm biên không là giao. Không gộp sự kiện hoặc lọc thời lượng tối thiểu.
Tie được xử lý theo thứ tự onset/end rồi chỉ số; protocol không quy định tie.
Số xung đột tie phát hiện trong các phép so sánh: **{ties}**. Nếu khác kết quả gốc, cần kiểm tra tie trước khi kết luận lỗi.

**Đối chiếu:** chưa đối chiếu bảng M1 từng bản ghi của phân tích gốc; chưa tuyên bố verified trong 0.001.
Ngưỡng 0.001 được dùng lại từ quy trình D2 staging như tiêu chí đối chiếu cho phần mở rộng này.

**Khai báo:** có AI hỗ trợ; trợ lý đã xem kết quả bản thảo. Không phải kiểm chứng mù độc lập do con người.
Không đọc/import code phân tích gốc. Code staging kiểm chứng được dùng lại cho đọc CSV, cửa sổ và tải dữ liệu.
Chi tiết từng người nằm trong scorer_summary.csv; hash và kiểm tra đầu vào nằm trong provenance.json.
'''
    (output / 'REPORT_VI.md').write_text(report, encoding='utf-8')
    print(f'{task}: {output}, mean M1={mean:.6f}, tie conflicts={ties}')


def main(task):
    parser = argparse.ArgumentParser(description=f'M1 event verification: {task}')
    parser.add_argument('command', choices=['download', 'analyze'])
    parser.add_argument('--data-root', type=Path, default=HERE / 'data/psg-ipa/1.0.0')
    parser.add_argument('--output', type=Path, default=HERE / task / 'runs' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
    args = parser.parse_args()
    if args.command == 'download':
        download(task, args.data_root)
    else:
        analyze(task, args.data_root, args.output)

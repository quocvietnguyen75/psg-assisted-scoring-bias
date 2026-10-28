"""Resume all event annotation downloads; verify every file, report failures."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
from event_m1 import DOWNLOAD_BASE, HERE, TASKS, fetch_bytes, manifest_entries, names, sha


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=6)
    args = parser.parse_args()
    root = HERE / 'data/psg-ipa/1.0.0'
    root.mkdir(parents=True, exist_ok=True)
    manifest = fetch_bytes(DOWNLOAD_BASE + 'SHA256SUMS.txt')
    expected = manifest_entries(manifest.decode())
    (root / 'SHA256SUMS.txt').write_bytes(manifest)
    pending = [name for task in TASKS for name in names(task)
               if not (root / name).exists() or sha(root / name) != expected[name]]
    print(f'Remaining files: {len(pending)}', flush=True)

    def one(name):
        try:
            data = fetch_bytes(DOWNLOAD_BASE + name)
            if hashlib.sha256(data).hexdigest() != expected[name]:
                raise ValueError('Checksum mismatch')
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            return None
        except Exception as error:
            return f'{name}: {error}'

    failures = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(one, name) for name in pending]
        for i, future in enumerate(as_completed(futures), 1):
            error = future.result()
            if error:
                failures.append(error)
            if i % 20 == 0 or i == len(pending):
                print(f'Finished {i}/{len(pending)}, failures {len(failures)}', flush=True)
    if failures:
        raise SystemExit('\n'.join(failures))
    print('All 375 event annotation files verified.', flush=True)


if __name__ == '__main__':
    main()

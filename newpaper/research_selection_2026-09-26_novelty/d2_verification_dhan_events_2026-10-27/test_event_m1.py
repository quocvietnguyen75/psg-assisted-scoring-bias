"""End-to-end synthetic checks, before real event analysis."""
import contextlib
import csv
import hashlib
import io
import json
from pathlib import Path
import shutil
import unittest
import uuid
from event_m1 import analyze, names, TASKS


class EventIntegration(unittest.TestCase):
    @contextlib.contextmanager
    def fixture_directory(self):
        # Regular mkdir inherits workspace ACLs; Windows tempfile's private ACL
        # may be inaccessible to the sandbox token.
        base = Path(__file__).resolve().parent / 'data'
        directory = base / ('event-fixture-' + uuid.uuid4().hex)
        directory.mkdir(parents=True)
        try:
            yield directory
        finally:
            if directory.resolve().parent != base.resolve():
                raise ValueError('Fixture cleanup outside expected directory.')
            shutil.rmtree(directory)

    def test_all_tasks_end_to_end_and_corruption(self):
        for task, (_, _, labels) in TASKS.items():
            with self.subTest(task=task), self.fixture_directory() as directory:
                root = Path(directory) / 'data'
                manifest = []
                for name in names(task):
                    path = root / name
                    path.parent.mkdir(parents=True, exist_ok=True)
                    # manual has no event, assisted exactly adopts the auto event.
                    text = 'Recording onset,Duration,Annotation\n0,0,Lights off\n20,0,Lights on\n'
                    if '/manual/' not in name:
                        text += f'2,3,{sorted(labels)[0]}\n'
                    path.write_text(text, encoding='utf-8')
                    manifest.append(hashlib.sha256(path.read_bytes()).hexdigest() + ' ' + name)
                (root / 'SHA256SUMS.txt').write_text('\n'.join(manifest), encoding='utf-8')
                output = Path(directory) / 'run'
                with contextlib.redirect_stdout(io.StringIO()):
                    analyze(task, root, output)
                with (output / 'results_full.csv').open() as stream:
                    rows = list(csv.DictReader(stream))
                self.assertEqual(len(rows), 5)
                self.assertTrue(all(float(row['M1']) == 1 for row in rows))
                with (output / 'scorer_summary.csv').open() as stream:
                    self.assertEqual(len(list(csv.DictReader(stream))), 60)
                meta = json.loads((output / 'provenance.json').read_text(encoding='utf-8'))
                self.assertEqual(len(meta['input_sha256']), 125)
                self.assertIn('mean', (output / 'task_summary.csv').read_text())
                with self.assertRaises(FileExistsError):
                    analyze(task, root, output)
                (root / next(names(task))).write_text('corrupted', encoding='utf-8')
                with self.assertRaisesRegex(ValueError, 'checksum'):
                    analyze(task, root, Path(directory) / 'new-run')
                self.assertFalse((Path(directory) / 'new-run').exists())


if __name__ == '__main__':
    unittest.main()

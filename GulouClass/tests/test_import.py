import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import URLError

from assets.func.SeatableGet import validate_inputs, fetch_courses
from assets.func.schedule_store import atomic_json, build_snapshot, import_schedule, load_snapshot, load_preferences

URL = 'https://cloud.seatable.cn/external-apps/example/?page_id=abc'
PREFS = dict(url=URL, university='测试大学', grade='2024临床医学')


def row(date='2026-09-07', day='一', period='1-2'):
    return ['测试大学', '2024临床医学', '诊断学', date, day, period,
            '08:00-09:50', '问诊', '老师', 'None', '教学楼', 'None', 'None', 'None', 'None', 'None']


class ImportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.old = build_snapshot([row()], PREFS)
        atomic_json(self.root / 'schedule.json', self.old)
        self.before = (self.root / 'schedule.json').read_bytes()
        (self.root / 'internetData1.txt').write_text('legacy backup', encoding='utf-8')

    def check_unchanged(self):
        self.assertEqual((self.root / 'schedule.json').read_bytes(), self.before)
        self.assertEqual((self.root / 'internetData1.txt').read_text(), 'legacy backup')

    def test_success_replaces_whole_snapshot_and_remembers_inputs(self):
        with patch('assets.func.SeatableGet.fetch_courses', return_value=[row(), row('2026-09-21')]):
            result = import_schedule(**PREFS, conf_dir=self.root)
        self.assertEqual(set(result['weeks']), {'1', '3'})
        self.assertEqual(result['course_count'], 2)
        self.assertEqual(load_preferences(self.root), PREFS)
        self.assertEqual(load_snapshot(self.root), result)
        self.assertEqual((self.root / 'internetData1.txt').read_text(), 'legacy backup')

    def test_network_failure_keeps_old_snapshot(self):
        with patch('assets.func.SeatableGet.fetch_courses', side_effect=URLError('offline')):
            with self.assertRaises(URLError):
                import_schedule(**PREFS, conf_dir=self.root)
        self.check_unchanged()

    def test_bad_later_row_does_not_publish_partial_data(self):
        for invalid in [row(period='13-14'), row(date='invalid'), row(day='二'), row(period='n/a'), row()[:6]]:
            with self.subTest(invalid=invalid):
                with patch('assets.func.SeatableGet.fetch_courses', return_value=[row(), invalid]):
                    with self.assertRaises(ValueError):
                        import_schedule(**PREFS, conf_dir=self.root)
                self.check_unchanged()

    def test_empty_result_keeps_old_snapshot(self):
        with patch('assets.func.SeatableGet.fetch_courses', return_value=[]):
            with self.assertRaises(ValueError):
                import_schedule(**PREFS, conf_dir=self.root)
        self.check_unchanged()

    def test_replace_failure_keeps_old_snapshot_and_removes_temp(self):
        import os
        replace = os.replace
        def fail_snapshot(source, target):
            if Path(target).name == 'schedule.json':
                raise OSError('disk full')
            return replace(source, target)
        with patch('assets.func.SeatableGet.fetch_courses', return_value=[row('2026-09-14')]), patch('assets.func.schedule_store.os.replace', side_effect=fail_snapshot):
            with self.assertRaises(OSError):
                import_schedule(**PREFS, conf_dir=self.root)
        self.check_unchanged()
        self.assertFalse(list(self.root.glob('*.tmp')))

    def test_invalid_inputs_fail_before_network(self):
        for changes in [dict(url=''), dict(url='https://other.example/external-apps/a/?page_id=b'), dict(url=URL.split('?')[0]), dict(university=' '), dict(grade='')]:
            with self.subTest(changes=changes), patch('assets.func.SeatableGet._query_rows') as query:
                with self.assertRaises(ValueError):
                    fetch_courses(**dict(PREFS, **changes))
                query.assert_not_called()
        self.assertEqual(validate_inputs(' ' + URL, ' 测试大学 ', '2024临床医学 '), PREFS)

    def test_query_limit_does_not_silently_publish_partial_results(self):
        with patch('assets.func.SeatableGet._query_rows', return_value=([{}] * 500, {})):
            with self.assertRaises(ValueError):
                fetch_courses(**PREFS)

    def test_first_import_with_no_existing_files(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertIsNone(load_snapshot(folder))
            with patch('assets.func.SeatableGet.fetch_courses', return_value=[row()]):
                result = import_schedule(**PREFS, conf_dir=folder)
            self.assertEqual(load_snapshot(folder), result)

    def test_actual_legacy_data_validates(self):
        import csv
        conf = Path(__file__).resolve().parents[1] / 'assets' / 'conf'
        for path in conf.glob('internetData[0-9]*.txt'):
            with path.open(encoding='utf-8') as stream:
                rows = list(csv.reader(stream))
            if rows:
                self.assertEqual(build_snapshot(rows, PREFS)['course_count'], len(rows))


if __name__ == '__main__':
    unittest.main()

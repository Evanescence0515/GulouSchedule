"""Validate a complete timetable before atomically publishing one snapshot.

Legacy text files remain read-only fallbacks until the first successful import.
"""
import json
import os
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from .schedule_model import parse_row

CONF_DIR = Path(__file__).resolve().parents[1] / 'conf'


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent,
                                         prefix='.' + path.name, suffix='.tmp', delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(value, stream, ensure_ascii=False)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def load_preferences(conf_dir=CONF_DIR):
    try:
        value = json.loads((Path(conf_dir) / 'import_preferences.json').read_text(encoding='utf-8'))
        return {k: v for k, v in value.items() if k in ('url', 'university', 'grade') and isinstance(v, str)}
    except (OSError, ValueError, AttributeError):
        return {}


def build_snapshot(rows, preferences):
    if not rows:
        raise ValueError('没有找到匹配的课程，请检查学校和班级名称。')
    dates = []
    for index, row in enumerate(rows, 1):
        try:
            if len(row) != 16 or not all(isinstance(cell, str) for cell in row):
                raise ValueError('课程字段不完整')
            if not row[2].strip() or row[2] == 'None':
                raise ValueError('缺少课程名称')
            date = datetime.strptime(row[3][:10], '%Y-%m-%d')
            if row[4] != '一二三四五六日'[date.weekday()]:
                raise ValueError('日期与星期不一致')
            if not parse_row(row):
                raise ValueError('缺少有效节次')
            dates.append(date)
        except (ValueError, IndexError, TypeError) as error:
            raise ValueError('第 {} 条课程数据有误：{}'.format(index, error)) from error
    start = min(dates)
    monday = start - timedelta(days=start.weekday())
    weeks = {}
    for date, row in zip(dates, rows):
        week = (date - monday).days // 7 + 1
        weeks.setdefault(str(week), []).append(row)
    return dict(version=1, start_date=start.strftime('%Y-%m-%d'), weeks=weeks,
                course_count=len(rows), preferences=dict(preferences),
                updated_at=datetime.now().strftime('%Y-%m-%d %H:%M'))


def load_snapshot(conf_dir=CONF_DIR):
    path = Path(conf_dir) / 'schedule.json'
    if not path.exists():
        return None
    value = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(value, dict) or value.get('version') != 1 or not isinstance(value.get('weeks'), dict):
        raise ValueError('课表缓存格式不正确')
    datetime.strptime(value['start_date'], '%Y-%m-%d')
    if any(not key.isdigit() or int(key) < 1 or not isinstance(rows, list)
           for key, rows in value['weeks'].items()):
        raise ValueError('课表周次格式不正确')
    return value


def import_schedule(url, university, grade, conf_dir=CONF_DIR, progress=lambda text: None):
    from .SeatableGet import fetch_courses, validate_inputs
    preferences = validate_inputs(url, university, grade)
    # Preferences are separate from the timetable; failed queries cannot alter courses.
    atomic_json(Path(conf_dir) / 'import_preferences.json', preferences)
    progress('正在连接课程网站…')
    rows = fetch_courses(**preferences)
    progress('正在校验课程和日期…')
    snapshot = build_snapshot(rows, preferences)
    progress('正在保存课表…')
    atomic_json(Path(conf_dir) / 'schedule.json', snapshot)
    return snapshot

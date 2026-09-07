"""Pure course parsing shared by validation and rendering."""
import re

DAYS = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']


def parse_row(row):
    day = '一二三四五六日'.index(row[4].strip())
    result = []
    for practice, column in ((False, 5), (True, 11)):
        value = row[column].strip()
        if value in ('', 'None'):
            continue
        if practice:
            spans = [(1, 12)] if value == '全天' else [(n + 1, n + 2) for n, _ in practice_time_justice(value)]
        else:
            spans = []
            for part in re.split('[、,，]', value):
                match = re.fullmatch(r'\s*(\d+)(?:\s*[-~～—]\s*(\d+))?\s*', part)
                if not match:
                    raise ValueError('Invalid period')
                spans.append((int(match[1]), int(match[2] or match[1])))
        teacher, place, content = (13, 15, 12) if practice else (8, 10, 7)
        clean = lambda i: row[i].strip() if row[i].strip() not in ('', 'None') else '未填写'
        for start, end in spans:
            if not 1 <= start <= end <= 12:
                raise ValueError('Period out of range')
            result.append(dict(day=day, start=start, end=end, title=clean(2), place=clean(place), detail='{} · 第 {}–{} 节\n\n授课老师：{}\n\n授课地点：{}\n\n授课内容：{}{}'.format(DAYS[day], start, end, clean(teacher), clean(place), clean(content), '\n\n实践课' if practice else '')))
    return result


def practice_time_justice(value):
    if value.strip() == '全天':
        return ['全天', '']
    result = []
    for part in value.split('、'):
        match = re.match(r'\s*(\d{1,2})[:：](\d{2})(.*)', part)
        if not match:
            raise ValueError('Invalid practice time')
        hour = int(match[1])
        period = hour - 8 if hour < 13 else hour - 14 + 4 if hour < 18 else 8
        result.append((period, match[3]))
    return result


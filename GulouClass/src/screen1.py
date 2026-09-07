"""Responsive weekly timetable; existing import entry points are retained."""
import csv
from datetime import datetime, timedelta
from pathlib import Path
from assets.func.schedule_model import parse_row, practice_time_justice
from assets.func.schedule_store import load_snapshot
from .theme import theme
from .ui_widgets import RoundedButton, ThemeBox, label, toolbar
from kivy.clock import Clock
from kivy.graphics import Color, Line, Rectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.uix.scrollview import ScrollView
from kivy.utils import escape_markup

CONF_DIR = Path(__file__).resolve().parents[1] / 'assets' / 'conf'
DAYS = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']


class FirstScreen(Screen):
    gutter, row_height = dp(36), dp(76)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.refresh()
        self.entries, self.period_labels = [], []
        root = ThemeBox(orientation='vertical', padding=dp(16), spacing=dp(8))
        top, self.toolbar_button = toolbar('鼓楼课表', '工具', self.switch_to_second_screen)
        root.add_widget(top)
        nav = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(6))
        self.previous = RoundedButton(text='<', size_hint_x=None, width=dp(36))
        self.previous.bind(on_release=lambda *_: self.updata_button_text_according2week(self.week_number - 1))
        self.week_button = RoundedButton(fill_role='soft', text_role='accent')
        self.week_button.bind(on_release=self.show_dropdown)
        next_button = RoundedButton(text='>', size_hint_x=None, width=dp(36))
        next_button.bind(on_release=lambda *_: self.updata_button_text_according2week(self.week_number + 1))
        home = RoundedButton(text='回到本周', size_hint_x=None, width=dp(92), fill_role='surface')
        home.bind(on_release=lambda *_: self.updata_button_text_according2week(self.current_week()))
        for item in (self.previous, self.week_button, next_button, home):
            nav.add_widget(item)
        root.add_widget(nav)
        self.summary = label(size_hint_y=None, height=dp(28), halign='left')
        self.summary.color_role = 'muted'
        self.summary.bind(size=lambda w, v: setattr(w, 'text_size', v))
        root.add_widget(self.summary)
        self.header_scroll = ScrollView(size_hint_y=None, height=dp(56), do_scroll_y=False, do_scroll_x=False, bar_width=0)
        self.header = BoxLayout(size_hint_x=None)
        self.header.add_widget(label('节次', size_hint_x=None, width=self.gutter))
        self.weekday_buttons = []
        for _ in DAYS:
            item = RoundedButton(font_size='13sp', disabled=True, halign='center', disabled_text_alpha=1)
            self.weekday_buttons.append(item)
            self.header.add_widget(item)
        self.header_scroll.add_widget(self.header)
        root.add_widget(self.header_scroll)
        self.scroll = ScrollView(bar_width=dp(3), scroll_type=['bars', 'content'])
        self.table = FloatLayout(size_hint=(None, None), height=self.row_height * 12)
        self.scroll.add_widget(self.table)
        self.scroll.bind(width=self.resize_table, scroll_x=lambda w, v: setattr(self.header_scroll, 'scroll_x', v))
        self.table.bind(pos=self.arrange, size=self.arrange)
        root.add_widget(self.scroll)
        self.add_widget(root)
        theme.bind(name=self._apply_theme)
        self.updata_button_text_according2week(self.week_number)

    def _apply_theme(self, *args):
        self.arrange()

    def resize_table(self, *args):
        self.table.width = self.header.width = max(self.scroll.width, dp(568))
        self.header_scroll.scroll_x = self.scroll.scroll_x

    def arrange(self, *args):
        table = self.table
        column = (table.width - self.gutter) / 7
        table.canvas.before.clear()
        with table.canvas.before:
            Color(*theme.color('surface'))
            Rectangle(pos=table.pos, size=table.size)
            if getattr(self, 'today_column', -1) >= 0:
                Color(*theme.color('today'))
                Rectangle(pos=(table.x + self.gutter + column * self.today_column, table.y), size=(column, table.height))
            Color(*theme.color('line'))
            for row in range(13):
                y = table.top - row * self.row_height
                Line(points=[table.x, y, table.right, y], width=1)
            for col in range(8):
                x = table.x + self.gutter + column * col
                Line(points=[x, table.y, x, table.top], width=1)
        for widget, day, start, end in self.entries:
            widget.pos = (table.x + self.gutter + day * column + dp(3), table.top - end * self.row_height + dp(3))
            widget.size = (column - dp(6), (end - start + 1) * self.row_height - dp(6))
            widget.text_size = (widget.width - dp(12), widget.height - dp(14))
        for period, widget in enumerate(self.period_labels, 1):
            widget.pos = (table.x, table.top - period * self.row_height)
            widget.size = (self.gutter, self.row_height)

    def refresh(self):
        self.has_calendar = True
        self.snapshot = None
        self.cache_error = False
        try:
            self.snapshot = load_snapshot(CONF_DIR)
        except (OSError, ValueError, KeyError, TypeError):
            self.cache_error = True
        try:
            start = self.snapshot['start_date'] if self.snapshot else (CONF_DIR / 'cache_data.txt').read_text(encoding='utf-8').strip()
            self.start_date = datetime.strptime(start, '%Y-%m-%d')
        except (OSError, ValueError):
            self.start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            self.has_calendar = False
        self.week_number = self.current_week()

    def current_week(self):
        monday = self.start_date - timedelta(days=self.start_date.weekday())
        return max(1, (datetime.now().date() - monday.date()).days // 7 + 1)

    def show_dropdown(self, button):
        dropdown = DropDown(max_height=dp(300))
        weeks = [int(p.stem[12:]) for p in CONF_DIR.glob('internetData[0-9]*.txt') if p.stem[12:].isdigit()]
        if self.snapshot:
            weeks = [int(week) for week in self.snapshot['weeks']]
        for week in range(1, max([25, self.week_number, self.current_week()] + weeks) + 1):
            item = RoundedButton(text='第 {} 周{}'.format(week, ' · 本周' if week == self.current_week() else ''), size_hint_y=None, height=dp(44), fill_role='surface')
            item.bind(on_release=lambda _, n=week: dropdown.select(n))
            dropdown.add_widget(item)
        dropdown.bind(on_select=lambda _, n: self.updata_button_text_according2week(n))
        dropdown.open(button)

    def updata_button_text_according2week(self, week=1):
        self.week_number = max(1, int(week))
        self.previous.disabled = self.week_number == 1
        self.week_button.text = '第 {} 周'.format(self.week_number)
        monday = self.start_date - timedelta(days=self.start_date.weekday()) + timedelta(weeks=self.week_number - 1)
        self.today_column = -1
        for index, item in enumerate(self.weekday_buttons):
            date = monday + timedelta(days=index)
            today = date.date() == datetime.now().date()
            item.text = '{}\n{}'.format('今天' if today else DAYS[index], date.strftime('%m/%d'))
            item.fill_role = 'accent' if today else 'background'
            item.text_role = 'on_accent' if today else 'muted'
            item.apply_theme()
            if today:
                self.today_column = index
        self.date_range = '{} — {}'.format(monday.strftime('%m.%d'), (monday + timedelta(days=6)).strftime('%m.%d'))
        courses, invalid = [], 0
        try:
            if self.snapshot is not None:
                rows = self.snapshot['weeks'].get(str(self.week_number), [])
            else:
                with (CONF_DIR / 'internetData{}.txt'.format(self.week_number)).open(encoding='utf-8', newline='') as stream:
                    rows = list(csv.reader(stream))
            for row in rows:
                try:
                    courses.extend(self.parse_row(row))
                except (ValueError, IndexError, KeyError, TypeError, AttributeError):
                    invalid += 1
        except OSError:
            pass
        self.render_courses(courses)
        if invalid:
            self.summary.text += ' · {} 条数据待检查'.format(invalid)
        if self.cache_error:
            self.summary.text += ' · 新课表缓存异常，请重新导入'

    parse_row = staticmethod(parse_row)

    def render_courses(self, courses):
        self.table.clear_widgets()
        self.entries, self.period_labels, self.buttons = [], [], []
        for period in range(1, 13):
            item = label('{:02d}'.format(period), size_hint=(None, None))
            item.color_role = 'muted'
            self.period_labels.append(item)
            self.table.add_widget(item)
        groups = []
        for course in sorted(courses, key=lambda c: (c['day'], c['start'], c['end'])):
            if groups and groups[-1]['day'] == course['day'] and course['start'] <= groups[-1]['end']:
                groups[-1]['end'] = max(groups[-1]['end'], course['end'])
                groups[-1]['courses'].append(course)
            else:
                groups.append(dict(day=course['day'], start=course['start'], end=course['end'], courses=[course]))
        for group in groups:
            course = group['courses'][0]
            extra = '\n另有 {} 门重叠课程'.format(len(group['courses']) - 1) if len(group['courses']) > 1 else ''
            text = '[b]{}[/b]\n\n[color=536071]{}[/color]{}'.format(escape_markup(course['title']), escape_markup(course['place']), extra)
            if group['start'] == group['end']:
                hint = '{} 门重叠课程'.format(len(group['courses'])) if extra else '点击详情'
                text = '[b]{}[/b]\n[color=536071]{}[/color]'.format(escape_markup(course['title']), hint)
            card = RoundedButton(course_key=course['title'], size_hint=(None, None), font_size='13sp', halign='left', valign='top', markup=True, text=text)
            card.additional_info = [course['title'] if not extra else '重叠课程', '\n\n────────────\n\n'.join(c['title'] + '\n\n' + c['detail'] for c in group['courses'])]
            card.bind(on_release=self.on_button_press)
            self.table.add_widget(card)
            self.entries.append((card, group['day'], group['start'], group['end']))
            self.buttons.append(card)
        self.summary.text = '{} · {} 门课程'.format(self.date_range, len(courses))
        if not courses:
            self.summary.text = self.date_range + (' · 本周暂无课程' if self.has_calendar else ' · 尚未导入课表，请前往工具导入')
        self.resize_table()
        self.arrange()

    practice_time_justice = staticmethod(practice_time_justice)

    def update_buttons_text(self, data):
        courses = []
        for row in data.get(self.week_number, []):
            for slot in row['时间（见习课）']:
                start = int(slot[0]) + 1
                courses.append(dict(day='一二三四五六日'.index(row['星期']), start=start, end=start + 1, title=row['科目'], place=row['地点（见习课）'], detail='\n\n'.join('{}：{}'.format(k, v) for k, v in row.items())))
        self.render_courses(courses)

    def on_button_press(self, instance):
        title, details = instance.additional_info
        content = BoxLayout(orientation='vertical', spacing=dp(16), padding=dp(12))
        scroll = ScrollView()
        body = label(details, size_hint_y=None, halign='left', valign='top')
        body.bind(width=lambda w, v: setattr(w, 'text_size', (v, None)), texture_size=lambda w, v: setattr(w, 'height', v[1] + dp(20)))
        scroll.add_widget(body)
        content.add_widget(scroll)
        close = RoundedButton(text='关闭', fill_role='accent', text_role='on_accent', size_hint_y=None, height=dp(44))
        content.add_widget(close)
        popup = Popup(title=title, title_font='chinese_font', title_color=theme.color('text'), title_size='19sp', content=content, size_hint=(.9, .75), background='', background_color=(1, 1, 1, 1), separator_color=theme.color('line'))
        close.bind(on_release=popup.dismiss)
        popup.open()

    def switch_to_second_screen(self, *args):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'second'

    def on_enter(self, *args):
        if hasattr(self, '_last_date') and self._last_date != datetime.now().date():
            self._check_day()
        self._last_date = datetime.now().date()
        self._day_event = Clock.schedule_interval(self._check_day, 60)

    def on_leave(self, *args):
        if hasattr(self, '_day_event'):
            self._day_event.cancel()

    def _check_day(self, *args):
        if datetime.now().date() != self._last_date:
            monday = self.start_date - timedelta(days=self.start_date.weekday())
            old_current = max(1, (self._last_date - monday.date()).days // 7 + 1)
            follow_current = self.week_number == old_current
            self._last_date = datetime.now().date()
            self.updata_button_text_according2week(self.current_week() if follow_current else self.week_number)

    def get_week_dates(self, target_date):
        monday = target_date - timedelta(days=target_date.weekday())
        return [(monday + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]

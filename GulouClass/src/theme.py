"""Light palettes adapted for timetable readability.

Inspiration: https://www.nordtheme.com/docs/colors-and-palettes/
             https://catppuccin.com/palette/ (Latte)
Card tints and contrast adjustments are specific to this application.
"""
import hashlib
import json
from pathlib import Path
from kivy.event import EventDispatcher
from kivy.properties import StringProperty
from kivy.utils import get_color_from_hex
from assets.func.schedule_store import atomic_json

THEMES = {
    'gulou': dict(name='鼓楼绯红', description='暖白与绯红，经典校园配色',
                  accent='#8B2635', background='#F8F5F4', soft='#F1E3E5', today='#FBEEF0',
                  text='#30282B', muted='#716269', line='#EEE5E6',
                  cards=['#DEEAF6', '#DFEEE5', '#EAE1F3', '#F8E8D7', '#F3DDE3', '#DCF0ED']),
    'nord': dict(name='北欧雾蓝', description='参考 Nord，清爽的蓝灰与冰青',
                 accent='#45688D', background='#ECEFF4', soft='#DCE5F0', today='#EAF2F9',
                 text='#2E3440', muted='#596579', line='#E1E7EF',
                 cards=['#D9E8F3', '#DCECEA', '#E5E1ED', '#F3E8D1', '#EFDBDF', '#DEE9D7']),
    'latte': dict(name='拿铁薰衣草', description='参考 Catppuccin Latte，柔和紫与奶白',
                  accent='#7053A8', background='#EFF1F5', soft='#E6DDF5', today='#F0EAF9',
                  text='#4C4F69', muted='#62667F', line='#E3E4EC',
                  cards=['#DDE7FB', '#E0ECD9', '#EBDDFA', '#F8E3D4', '#F3DEEE', '#D7EDF0']),
    'sage': dict(name='青松米白', description='自选自然色系，鼠尾草绿与暖沙色',
                 accent='#3D6B59', background='#F5F6EF', soft='#DFEADC', today='#EAF2E5',
                 text='#283C33', muted='#5E7064', line='#E5EADD',
                 cards=['#DDECDC', '#F1E6CC', '#DCE9EF', '#E8E0EF', '#F2DFD7', '#D7EBE5']),
}


class ThemeManager(EventDispatcher):
    name = StringProperty('gulou')

    def __init__(self, path=None, **kwargs):
        super().__init__(**kwargs)
        self.path = Path(path) if path else Path(__file__).resolve().parents[1] / 'assets' / 'conf' / 'appearance.json'
        try:
            saved = json.loads(self.path.read_text(encoding='utf-8')).get('theme')
            if saved in THEMES:
                self.name = saved
        except (OSError, ValueError, AttributeError, TypeError):
            pass

    def select(self, name):
        if name not in THEMES:
            raise ValueError('未知主题')
        atomic_json(self.path, {'theme': name})
        self.name = name

    def color(self, role):
        fixed = {'surface': '#FFFFFF', 'on_accent': '#FFFFFF', 'error': '#A32E42'}
        return get_color_from_hex(fixed[role] if role in fixed else THEMES[self.name][role])

    def course_color(self, title):
        colors = THEMES[self.name]['cards']
        return get_color_from_hex(colors[int(hashlib.sha256(title.encode()).hexdigest(), 16) % len(colors)])


theme = ThemeManager()

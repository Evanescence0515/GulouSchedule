"""Available tools and current timetable information."""
from kivy.metrics import dp
from kivy.graphics import Color, Line, RoundedRectangle
from kivy.uix.gridlayout import GridLayout
from kivy.utils import get_color_from_hex
from kivy.uix.screenmanager import Screen, SlideTransition
from .page_widgets import page, paragraph
from .ui_widgets import RoundedButton
from .theme import THEMES, theme


class ThemeOption(RoundedButton):
    def __init__(self, key, **kwargs):
        self.theme_key = key
        super().__init__(fill_role='surface', font_size='14sp', halign='left', valign='top',
                         padding=(dp(12), dp(10)), **kwargs)
        self.bind(pos=self.draw_preview, size=self.draw_preview)
        theme.bind(name=self.draw_preview)
        self.draw_preview()

    def draw_preview(self, *args):
        palette = THEMES[self.theme_key]
        selected = theme.name == self.theme_key
        self.text = palette['name'] + (' · 已选' if selected else '')
        self.text_size = (max(1, self.width - dp(24)), self.height - dp(20))
        self.canvas.after.clear()
        with self.canvas.after:
            Color(*get_color_from_hex(palette['accent']) if selected else theme.color('line'))
            Line(rounded_rectangle=(self.x + 1, self.y + 1, self.width - 2, self.height - 2, dp(10)), width=1.2)
            colors = [palette['accent']] + palette['cards'][:4]
            width = max(dp(4), (self.width - dp(40)) / 5)
            for index, color in enumerate(colors):
                Color(*get_color_from_hex(color))
                RoundedRectangle(pos=(self.x + dp(12) + index * (width + dp(4)), self.y + dp(14)),
                                 size=(width, dp(18)), radius=[dp(5)])


class SecondScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root, body, self.toolbar_button, _ = page('工具', self.switch_to_first_screen)
        body.add_widget(paragraph('课程管理', '18sp', 'text'))
        body.add_widget(paragraph('从课程网站获取最新安排，导入后可离线查看。'))
        action = RoundedButton(text='从网络导入课表  >', fill_role='accent', text_role='on_accent', size_hint_y=None, height=dp(56), font_size='16sp')
        action.bind(on_release=self.switch_to_third_screen)
        body.add_widget(action)
        body.add_widget(paragraph('外观配色', '18sp', 'text'))
        options = GridLayout(cols=2, spacing=dp(8), size_hint_y=None, height=dp(184))
        self.theme_options = {}
        for key in THEMES:
            option = ThemeOption(key)
            option.bind(on_release=lambda _, selected=key: self.select_theme(selected))
            options.add_widget(option)
            self.theme_options[key] = option
        body.add_widget(options)
        self.theme_description = paragraph(THEMES[theme.name]['description'], '12sp')
        body.add_widget(self.theme_description)
        body.add_widget(paragraph('当前课表', '18sp', 'text'))
        self.status = paragraph('正在读取课表…')
        body.add_widget(self.status)
        body.add_widget(paragraph('字体声明', '18sp', 'text'))
        body.add_widget(paragraph('本应用使用 MiSans 字体。\n字体版权归小米所有，按 MiSans 字体许可协议使用。', '12sp'))
        self.add_widget(root)

    def select_theme(self, key):
        try:
            theme.select(key)
        except OSError:
            self.theme_description.color_role = 'error'
            self.theme_description.text = '配色保存失败，请检查目录写入权限。'
            return
        self.theme_description.color_role = 'muted'
        self.theme_description.text = THEMES[key]['description']

    def on_pre_enter(self, *args):
        home = self.manager.get_screen('first')
        snapshot = home.snapshot
        if snapshot:
            info = snapshot.get('preferences', {})
            self.status.text = '{} · {}\n\n{} 条课程安排 · {} 个教学周\n\n最近导入：{}'.format(
                info.get('university', ''), info.get('grade', ''), snapshot.get('course_count', 0),
                len(snapshot['weeks']), snapshot.get('updated_at', '未知'))
        elif home.has_calendar:
            self.status.text = '已有本地课表，可离线查看。\n\n课程起始日期：{}\n\n选择“从网络导入课表”更新安排。'.format(home.start_date.strftime('%Y-%m-%d'))
        else:
            self.status.text = '尚未导入课表。\n\n准备好课程分享链接、学校和班级，即可开始导入。'
        if home.cache_error:
            self.status.text += '\n\n新课表缓存异常，请重新导入。'

    def switch_to_third_screen(self, *args):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'third'

    def switch_to_first_screen(self, *args):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'first'

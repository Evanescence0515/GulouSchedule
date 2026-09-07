"""Import form with background work and main-thread UI updates."""
from functools import partial
from threading import Thread
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.uix.textinput import TextInput
from assets.func.SeatableGet import validate_inputs, describe_error
from assets.func.schedule_store import import_schedule, load_preferences
from .page_widgets import page, paragraph
from .screen1 import CONF_DIR
from .ui_widgets import RoundedButton
from .theme import theme

DEFAULT_URL = 'https://cloud.seatable.cn/external-apps/aa731c40-006f-439c-99b8-cae69fa483eb/?page_id=8n27'


class ThirdScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.busy = False
        self._status_event = None
        self._stage = ''
        self._dots = 0
        root, body, self.back_button, self.form_scroll = page('导入课表', self.switch_to_second_screen)
        body.add_widget(paragraph('连接你的课程', '20sp', 'text'))
        body.add_widget(paragraph('填写课程分享链接、学校和班级，获取对应的课程安排。'))
        saved = load_preferences(CONF_DIR)
        self.text_input1 = self.add_field(body, '课程分享链接', saved.get('url', DEFAULT_URL),
                                          '复制 SeaTable 具体课程页面的完整链接。')
        self.text_input2 = self.add_field(body, '大学名称', saved.get('university', '南京大学'),
                                          '例如：南京大学、南京医科大学')
        self.text_input3 = self.add_field(body, '年级与班级', saved.get('grade', ''),
                                          '与来源表格一致，例如“2024临床医学”。')
        self.inputs = [self.text_input1, self.text_input2, self.text_input3]
        self.form_scroll.bind(size=self._keep_focused_field_visible)
        self.text_input3.hint_text = '请输入年级与班级'
        self.status = paragraph('准备就绪', color='muted')
        body.add_widget(self.status)
        self.enter_button = RoundedButton(text='导入课表', fill_role='accent', text_role='on_accent', size_hint_y=None, height=dp(48), font_size='16sp')
        self.enter_button.disabled_color = (1, 1, 1, .7)
        self.enter_button.bind(on_release=self.enter_and_updata)
        body.add_widget(self.enter_button)
        self.view_button = RoundedButton(text='查看课表', size_hint_y=None, height=0, opacity=0, disabled=True, fill_role='surface')
        self.view_button.bind(on_release=self.switch_to_first_screen)
        body.add_widget(self.view_button)
        self.add_widget(root)
        theme.bind(name=self._apply_theme)
        self._apply_theme()

    def _apply_theme(self, *args):
        for field in self.inputs:
            field.foreground_color = theme.color('text')
            field.cursor_color = theme.color('accent')
            field.background_color = theme.color('surface')
            field.hint_text_color = theme.color('muted')
            field.selection_color = theme.color('soft')

    def add_field(self, body, title, value, hint):
        body.add_widget(paragraph(title, '15sp', 'text'))
        field = TextInput(text=value, multiline=False, font_name='chinese_font', font_size='15sp',
                          size_hint_y=None, height=dp(48), padding=(dp(12), dp(13)),
                          background_normal='', background_active='', background_color=(1, 1, 1, 1),
                          foreground_color=theme.color('text'), cursor_color=theme.color('accent'), write_tab=False)
        field.bind(focus=self._on_field_focus)
        body.add_widget(field)
        body.add_widget(paragraph(hint, '12sp'))
        return field

    def _on_field_focus(self, field, focused):
        if focused:
            Clock.schedule_once(partial(self._reveal_field, field), .15)

    def _reveal_field(self, field, dt):
        # Ignore delayed events after focus moves or the page is left.
        if field.focus and self.manager and self.manager.current == self.name:
            self.form_scroll.scroll_to(field, padding=18, animate=False)

    def _keep_focused_field_visible(self, *args):
        # A keyboard/window resize can reduce the viewport after focus changes.
        for field in self.inputs:
            if field.focus:
                Clock.schedule_once(partial(self._reveal_field, field))
                break

    def enter_and_updata(self, *args):
        if self.busy:
            return
        try:
            values = validate_inputs(*(field.text for field in self.inputs))
        except ValueError as error:
            self.status.text, self.status.color_role = str(error), 'error'
            self.form_scroll.scroll_to(self.status)
            return
        for field, key in zip(self.inputs, ('url', 'university', 'grade')):
            field.text = values[key]
            field.focus = False
        self.busy = True
        self._set_controls(True)
        self.view_button.height, self.view_button.opacity, self.view_button.disabled = 0, 0, True
        self.status.color_role = 'muted'
        self._stage, self._dots = '正在连接课程网站', 0
        self._animate_status(0)
        self._status_event = Clock.schedule_interval(self._animate_status, .4)
        self.form_scroll.scroll_to(self.status)
        # The worker receives plain values; all widget changes return through Clock.
        self._worker_thread = Thread(target=self._import_worker, args=(values,), daemon=True)
        try:
            self._worker_thread.start()
        except Exception as error:
            self._finish(None, describe_error(error), 0)

    def _set_controls(self, busy):
        self.enter_button.disabled = busy
        self.enter_button.text = '正在导入…' if busy else '导入课表'
        for field in self.inputs:
            field.disabled = busy

    def _animate_status(self, dt):
        self._dots = self._dots % 3 + 1
        self.status.text = self._stage + '·' * self._dots

    def _progress(self, text):
        Clock.schedule_once(partial(self._set_stage, text))

    def _set_stage(self, text, dt):
        if self.busy:
            self._stage = text.rstrip('…')
            self._animate_status(0)

    def _import_worker(self, values):
        try:
            result = import_schedule(**values, conf_dir=CONF_DIR, progress=self._progress)
        except Exception as error:
            Clock.schedule_once(partial(self._finish, None, describe_error(error)))
        else:
            Clock.schedule_once(partial(self._finish, result, None))

    def _finish(self, result, error, dt):
        if self._status_event is not None:
            self._status_event.cancel()
            self._status_event = None
        self.busy = False
        self._set_controls(False)
        if error:
            self.status.text = '导入失败：{}\n\n原有课表未更改。'.format(error)
            self.status.color_role = 'error'
            self.enter_button.text = '重新导入'
        else:
            # Commit already succeeded; distinguish a display failure from an import failure.
            try:
                home = self.manager.get_screen('first')
                home.refresh()
                home.updata_button_text_according2week(home.week_number)
                self.status.text = '导入成功：{} 条课程安排，覆盖 {} 个教学周。'.format(result['course_count'], len(result['weeks']))
                self.status.color_role = 'text'
            except Exception:
                self.status.text = '课表已保存，请重新打开应用查看。'
                self.status.color_role = 'error'
            self.enter_button.text = '再次导入'
            self.view_button.height, self.view_button.opacity, self.view_button.disabled = dp(48), 1, False
        Clock.schedule_once(lambda _: self.form_scroll.scroll_to(self.status), .1)

    def switch_to_first_screen(self, *args):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'first'

    def switch_to_second_screen(self, *args):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'second'

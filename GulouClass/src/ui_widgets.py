"""Theme-aware primitives and one shared toolbar for every page."""
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from .theme import theme


class ThemeLabel(Label):
    color_role = StringProperty('text')

    def __init__(self, **kwargs):
        super().__init__(font_name='chinese_font', font_size='14sp', **kwargs)
        theme.bind(name=self.apply_theme)
        self.bind(color_role=self.apply_theme)
        self.apply_theme()

    def apply_theme(self, *args):
        self.color = theme.color(self.color_role)


def label(text='', **kwargs):
    return ThemeLabel(text=text, **kwargs)


class RoundedButton(Button):
    fill_role = StringProperty('background')
    text_role = StringProperty('text')
    disabled_text_alpha = NumericProperty(.65)

    def __init__(self, fill=None, course_key=None, **kwargs):
        self.custom_fill, self.course_key = fill, course_key
        super().__init__(font_name='chinese_font', background_normal='', background_down='',
                         background_color=(0, 0, 0, 0), **kwargs)
        with self.canvas.before:
            self.tint = Color(1, 1, 1, 1)
            self.shape = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])
        self.bind(pos=self.paint, size=self.paint, state=self.paint,
                  fill_role=self.apply_theme, text_role=self.apply_theme)
        theme.bind(name=self.apply_theme)
        self.apply_theme()

    def apply_theme(self, *args):
        self.fill = (theme.course_color(self.course_key) if self.course_key else
                     self.custom_fill if self.custom_fill is not None else theme.color(self.fill_role))
        self.color = theme.color(self.text_role)
        self.disabled_color = self.color[:3] + [self.disabled_text_alpha]
        self.paint()

    def paint(self, *args):
        self.shape.pos, self.shape.size = self.pos, self.size
        self.tint.rgba = tuple(c * .93 for c in self.fill[:3]) + (1,) if self.state == 'down' else self.fill


class ThemeBox(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            self.tint = Color(*theme.color('background'))
            self.background = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.paint, size=self.paint)
        theme.bind(name=self.paint)

    def paint(self, *args):
        self.tint.rgba = theme.color('background')
        self.background.pos, self.background.size = self.pos, self.size


def toolbar(title, action_text, callback):
    # All screens use the same left title and right action positions.
    bar = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(12))
    heading = label(title, bold=True, halign='left', valign='middle')
    heading.font_size = '22sp'
    heading.bind(size=lambda w, v: setattr(w, 'text_size', v))
    bar.add_widget(heading)
    action = RoundedButton(text=action_text, size_hint=(None, None), width=dp(64), height=dp(40),
                           pos_hint={'center_y': .5}, fill_role='surface', text_role='accent', font_size='14sp')
    action.bind(on_release=callback)
    bar.add_widget(action)
    return bar, action

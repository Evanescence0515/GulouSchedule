"""Shared spacing and typography for tools and import pages."""
from kivy.animation import Animation
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from .ui_widgets import ThemeBox, label, toolbar


class FormScrollView(ScrollView):
    """Keep short forms at the top, including during focus/status scrolling."""
    def __init__(self, **kwargs):
        super().__init__(always_overscroll=False, **kwargs)

    def scroll_to(self, widget, padding=10, animate=True):
        if self.children and self.children[0].height <= self.height:
            Animation.cancel_all(self, 'scroll_y')
            self.scroll_y = 1
            return
        super().scroll_to(widget, padding=padding, animate=animate)


def paragraph(text, font_size='14sp', color='muted'):
    item = label(text, size_hint_y=None, halign='left', valign='top')
    item.font_size, item.color_role = font_size, color
    item.bind(width=lambda w, v: setattr(w, 'text_size', (v, None)),
              texture_size=lambda w, v: setattr(w, 'height', v[1] + dp(8)))
    return item


def page(title, back):
    root = ThemeBox(orientation='vertical', padding=dp(16), spacing=dp(14))
    header, button = toolbar(title, '返回', back)
    root.add_widget(header)
    scroll = FormScrollView(do_scroll_x=False, bar_width=dp(3))
    body = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(12), padding=(0, dp(8), 0, dp(16)))
    body.bind(minimum_height=body.setter('height'))
    scroll.add_widget(body)
    root.add_widget(scroll)
    return root, body, button, scroll

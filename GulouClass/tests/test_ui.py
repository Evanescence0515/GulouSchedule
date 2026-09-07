"""Kivy integration checks; uses isolated storage and mocked network requests."""
import csv
import os
import tempfile
import threading
import time
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch
from urllib.error import URLError

from kivy.base import EventLoop
from kivy.core.window import Window
from main import MyApp
import src.screen1 as home_module
import src.screen3 as import_module
from assets.func.schedule_store import load_snapshot
from src.theme import theme, THEMES, ThemeManager


def settle(frames=15):
    for _ in range(frames):
        EventLoop.idle()


class UiTests(unittest.TestCase):
    def test_import_flow_and_home_regressions(self):
        with tempfile.TemporaryDirectory() as folder:
            with (home_module.CONF_DIR / 'internetData1.txt').open(encoding='utf-8') as stream:
                rows = list(csv.reader(stream))
            with patch.object(home_module, 'CONF_DIR', Path(folder)), patch.object(import_module, 'CONF_DIR', Path(folder)):
                app = MyApp()
                app._run_prepare()
                self.addCleanup(app.stop)
                home = app.root.get_screen('first')
                form = app.root.get_screen('third')
                tools = app.root.get_screen('second')
                settle()
                self.assertFalse(home.has_calendar)
                self.assertFalse(home.buttons)
                self.assertFalse(hasattr(home, 'footer'))
                app.root.current = 'third'
                # Focusing any field on a short form must not create a top gap.
                for size in [(1000, 800), (390, 844)]:
                    Window.size = size
                    settle(25)
                    scroll = form.form_scroll
                    body = scroll.children[0]
                    self.assertLess(body.height, scroll.height)
                    for field in form.inputs:
                        field.focus = True
                        settle(20)
                        self.assertAlmostEqual(body.to_window(0, body.height)[1], scroll.top, delta=1)
                        field.focus = False
                    scroll.scroll_to(form.status)
                    settle()
                    self.assertAlmostEqual(body.to_window(0, body.height)[1], scroll.top, delta=1)
                # With a smaller viewport, a focused field must still be revealed.
                form.text_input3.focus = True
                Window.size = (390, 440)
                settle(25)
                field = form.text_input3
                self.assertGreater(form.form_scroll.children[0].height, form.form_scroll.height)
                self.assertGreaterEqual(field.to_window(*field.pos)[1], form.form_scroll.y - 1)
                self.assertLessEqual(field.to_window(field.right, field.top)[1], form.form_scroll.top + 1)
                field.focus = False
                Window.size = (390, 844)
                settle(25)
                form.export_to_png(str(Path(os.environ['TEMP']) / 'gulou-focus-fixed.png'))
                form.text_input3.text = ''
                form.enter_and_updata()
                self.assertFalse(form.busy)
                self.assertIn('班级', form.status.text)
                form.text_input2.text, form.text_input3.text = rows[0][:2]
                app.root.current = 'third'
                settle()
                entered, release = threading.Event(), threading.Event()
                main_thread = threading.get_ident()
                def fetch(**kwargs):
                    self.assertNotEqual(threading.get_ident(), main_thread)
                    entered.set()
                    if not release.wait(5):
                        raise TimeoutError()
                    return rows
                with patch('assets.func.SeatableGet.fetch_courses', side_effect=fetch) as query:
                    form.enter_and_updata()
                    self.assertTrue(entered.wait(2))
                    form.enter_and_updata()
                    self.assertTrue(form.enter_button.disabled)
                    self.assertTrue(all(item.disabled for item in form.inputs))
                    settle(30)
                    self.assertTrue(form.busy)
                    query.assert_called_once()
                    # Navigation remains usable while the worker waits.
                    form.switch_to_second_screen()
                    settle()
                    self.assertEqual(app.root.current, 'second')
                    release.set()
                    deadline = time.monotonic() + 5
                    while form.busy and time.monotonic() < deadline:
                        EventLoop.idle()
                    self.assertFalse(form.busy)
                self.assertIn('导入成功', form.status.text)
                self.assertFalse(form.view_button.disabled)
                self.assertEqual(load_snapshot(folder)['course_count'], len(rows))
                home.updata_button_text_according2week(1)
                self.assertTrue(home.buttons)
                self.assertFalse(home.cache_error)
                # Error after an earlier successful import keeps the same snapshot.
                before = (Path(folder) / 'schedule.json').read_bytes()
                with patch('assets.func.SeatableGet.fetch_courses', side_effect=URLError('offline')):
                    form.enter_and_updata()
                    deadline = time.monotonic() + 5
                    while form.busy and time.monotonic() < deadline:
                        EventLoop.idle()
                self.assertFalse(form.busy)
                self.assertFalse(form.enter_button.disabled)
                self.assertIn('原有课表未更改', form.status.text)
                self.assertEqual((Path(folder) / 'schedule.json').read_bytes(), before)
                self.assertEqual(import_module.ThirdScreen().text_input3.text, rows[0][1])
                # Single-period conflicts must remain visible and accessible.
                course = home.parse_row(rows[0])[0]
                course['end'] = course['start']
                home.render_courses([course, dict(course, title='另一门课程')])
                self.assertEqual(len(home.buttons), 1)
                self.assertIn('重叠课程', home.buttons[0].text)
                self.assertIn('另一门课程', home.buttons[0].additional_info[1])
                # Follow the current week across Monday, but preserve a manually selected week.
                home.start_date = datetime(2026, 8, 24)
                home._last_date = datetime(2026, 9, 6).date()
                home.week_number = 2
                class Monday(datetime):
                    @classmethod
                    def now(cls):
                        return cls(2026, 9, 7, 0, 1)
                with patch.object(home_module, 'datetime', Monday):
                    home._check_day()
                    self.assertEqual(home.week_number, 3)
                    self.assertEqual(home.today_column, 0)
                    home.week_number = 1
                    home._last_date = datetime(2026, 9, 6).date()
                    home._check_day()
                    self.assertEqual(home.week_number, 1)
                # Export real rendered views for visual inspection at both sizes.
                for size, suffix in [((1000, 800), 'desktop'), ((390, 844), 'mobile')]:
                    Window.size = size
                    for name, screen in [('tools', tools), ('import', form)]:
                        app.root.current = screen.name
                        settle(25)
                        screen.export_to_png(str(Path(os.environ['TEMP']) / ('gulou-{}-{}.png'.format(name, suffix))))
                self.assertFalse(any('??' in line for line in form.status.text.splitlines()))
                # Theme selection applies in place and persists without touching course/form data.
                saved_theme = theme.name
                with patch.object(theme, 'path', Path(folder) / 'appearance.json'):
                    home.updata_button_text_according2week(1)
                    original_input = [field.text for field in form.inputs]
                    original_cards = list(home.buttons)
                    original_week = home.week_number
                    for name in THEMES:
                        tools.theme_options[name].dispatch('on_release')
                        settle()
                        self.assertEqual(theme.name, name)
                        self.assertEqual(ThemeManager(theme.path).name, name)
                        self.assertEqual(home.week_number, original_week)
                        self.assertEqual(home.buttons, original_cards)
                        self.assertEqual([field.text for field in form.inputs], original_input)
                        self.assertEqual(list(home.week_button.color), theme.color('accent'))
                        self.assertEqual(list(form.text_input2.cursor_color), theme.color('accent'))
                        for card in home.buttons:
                            self.assertEqual(card.fill, theme.course_color(card.course_key))
                        self.assertNotIn('v', home.week_button.text)
                        app.root.current = 'first'
                        settle(25)
                        home.export_to_png(str(Path(os.environ['TEMP']) / ('gulou-theme-' + name + '.png')))
                    # Header action position, dimensions and title alignment match across all pages.
                    for size in [(1000, 800), (390, 844)]:
                        Window.size = size
                        geometries = []
                        for screen, button in [(home, home.toolbar_button), (tools, tools.toolbar_button), (form, form.back_button)]:
                            app.root.current = screen.name
                            settle(25)
                            geometries.append((tuple(button.pos), tuple(button.size)))
                            self.assertAlmostEqual(button.center_y, button.parent.center_y, delta=1)
                        self.assertEqual(geometries[0], geometries[1])
                        self.assertEqual(geometries[1], geometries[2])
                    theme.select(saved_theme)


if __name__ == '__main__':
    unittest.main()

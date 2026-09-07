import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from src.theme import ThemeManager, THEMES


class ThemeTests(unittest.TestCase):
    def test_missing_corrupt_and_unknown_preferences_use_default(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'appearance.json'
            self.assertEqual(ThemeManager(path).name, 'gulou')
            for text in ['broken json', '{"theme":"unknown"}', '[]', '{"theme":{}}']:
                path.write_text(text)
                self.assertEqual(ThemeManager(path).name, 'gulou')

    def test_failed_save_does_not_apply_a_different_theme(self):
        with tempfile.TemporaryDirectory() as folder:
            manager = ThemeManager(Path(folder) / 'appearance.json')
            with patch('src.theme.atomic_json', side_effect=OSError('read only')):
                with self.assertRaises(OSError):
                    manager.select('nord')
            self.assertEqual(manager.name, 'gulou')

    def test_text_remains_readable_across_palettes(self):
        def luminance(color):
            channels = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in color[:3]]
            return sum(c * weight for c, weight in zip(channels, [.2126, .7152, .0722]))
        def contrast(a, b):
            x, y = sorted([luminance(a), luminance(b)])
            return (y + .05) / (x + .05)
        with tempfile.TemporaryDirectory() as folder:
            manager = ThemeManager(Path(folder) / 'appearance.json')
            for name in THEMES:
                manager.name = name
                with self.subTest(name=name):
                    self.assertGreaterEqual(contrast(manager.color('accent'), manager.color('on_accent')), 4.5)
                    self.assertGreaterEqual(contrast(manager.color('muted'), manager.color('background')), 4.5)


if __name__ == '__main__':
    unittest.main()

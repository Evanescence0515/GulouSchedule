from src.screen1 import FirstScreen
from src.screen2 import SecondScreen
from src.screen3 import ThirdScreen
from src import App, ScreenManager


class MyApp(App):
    def build(self):
        # 创建屏幕管理器
        screen_manager = ScreenManager()
        # 创建第一个屏幕和第二个屏幕
        first_screen = FirstScreen(name='first')
        second_screen = SecondScreen(name='second')
        third_screen = ThirdScreen(name='third')
        # 添加屏幕到屏幕管理器
        screen_manager.add_widget(first_screen)
        screen_manager.add_widget(second_screen)
        screen_manager.add_widget(third_screen)
        return screen_manager

if __name__ == '__main__':
    MyApp().run()


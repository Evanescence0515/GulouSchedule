from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.gridlayout import GridLayout
from kivy.core.text import LabelBase
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.dropdown import DropDown
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.uix.textinput import TextInput
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from datetime import datetime, timedelta
from assets.func.excel2dict import excel2dict
from assets.func.SeatableGet import SeatableGet
from kivy.graphics import Color, Rectangle


import os

# 获取当前脚本文件的绝对路径
current_file_path = os.path.abspath(__file__)
data_file_path = os.path.join(os.path.dirname(current_file_path),"..","assets", "conf", "data.txt")
chinese_font_path = os.path.join(os.path.dirname(current_file_path),"..","assets", "font", "SIMHEI.TTF")
col_file_path = os.path.join(os.path.dirname(current_file_path),"..","assets", "conf", "color.txt")


LabelBase.register(name='chinese_font', fn_regular=chinese_font_path)

# 外观
Label_color=(236/255, 239/255, 241/255, 1)
Popup_color_background=(191/255, 54/255, 12/255,0.4)
Popup_color_title = (236/255, 239/255, 41/255,1)
BoxLayout_color=(255/255, 255/255, 255/255,0.9)
Button_color=(255/255, 235/255, 238/255,1)
header_color=(108/255, 0, 0,1)

# 获取窗口的宽度和高度
window_width = Window.width
window_height = Window.height

#获取日期

current_date = datetime.now()
# 覆写标签
class Label(Label):
    def __init__(self, **kwargs):
        super(Label, self).__init__(**kwargs)
        self.background_color = Label_color
        # 绘制带有背景颜色的矩形
        with self.canvas.before:
            Color(*self.background_color)  # 设置背景颜色为红色
            self.rect = Rectangle(size=self.size, pos=self.pos)

        # 每当 Label 的大小发生变化时，更新矩形的大小
        self.bind(size=self._update_rect, pos=self._update_rect)

    def set_color(self, color):
        # 更新 Label 的背景色
        self.background_color = color

        # 更新绘制矩形的颜色
        self.canvas.before.remove(self.rect)
        with self.canvas.before:
            self.rect_color = Color(*self.background_color)
            self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bold="True"

    def _update_rect(self, instance, value):
        self.rect.size = instance.size
        self.rect.pos = instance.pos

# 覆写BoxLayout
class BoxLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(BoxLayout, self).__init__(**kwargs)
        self.background_color=BoxLayout_color
        # 设置布局的默认背景颜色为其他颜色
        with self.canvas.before:
            Color(*self.background_color)  # 设置背景色
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

    def set_color(self, color):
        # 更新 Label 的背景色
        self.background_color = color

        # 更新绘制矩形的颜色
        self.canvas.before.remove(self.rect)
        with self.canvas.before:
            self.rect_color = Color(*self.background_color)
            self.rect = Rectangle(size=self.size, pos=self.pos)

    def _update_rect(self, instance, value):
        # 更新矩形的位置和大小以匹配布局
        self.rect.pos = instance.pos
        self.rect.size = instance.size

# 覆写button
class Button(Button):
    def __init__(self, **kwargs):
        super(Button, self).__init__(**kwargs)
        # 设置按钮的默认背景颜色为其他颜色
        self.color=(0,0,0,1)
        self.background_color = Button_color
        self.background_normal = ''
        self.background_down=''


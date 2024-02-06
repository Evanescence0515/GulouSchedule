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
from datetime import datetime, timedelta
from assets.func.excel2dict import excel2dict
from assets.func.SeatableGet import SeatableGet
import os

# 获取当前脚本文件的绝对路径
current_file_path = os.path.abspath(__file__)
data_file_path = os.path.join(os.path.dirname(current_file_path),"..","assets", "conf", "data.txt")
chinese_font_path = os.path.join(os.path.dirname(current_file_path),"..","assets", "font", "SIMHEI.TTF")
col_file_path = os.path.join(os.path.dirname(current_file_path),"..","assets", "conf", "color.txt")


LabelBase.register(name='chinese_font', fn_regular=chinese_font_path)

# 获取窗口的宽度和高度
window_width = Window.width
window_height = Window.height

#获取日期
current_date = datetime.now()
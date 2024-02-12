from . import ScreenManager, Screen, SlideTransition, App, Screen, datetime,\
    Button, GridLayout, LabelBase, BoxLayout, Label, DropDown,\
    FileChooserListView, Popup, Window, os, excel2dict

from . import current_file_path, data_file_path, col_file_path,\
    chinese_font_path, window_width, window_height, header_color

class SecondScreen(Screen):
    def __init__(self, **kwargs):
        super(SecondScreen, self).__init__(**kwargs)

        root_layout = BoxLayout(orientation='vertical')
        # 一级分屏
        layPart1 = BoxLayout(orientation='horizontal', size_hint=(1, 0.08),pos_hint={'x':0,'y':0.9})
        layPart2 = BoxLayout(orientation='horizontal', size_hint=(1, 0.1),pos_hint={'x':0,'y':0.8})
        layPart3 = BoxLayout(orientation='horizontal', size_hint=(1,0.1), pos_hint={'x':0,'y':0.7})
        layPartn = BoxLayout(orientation='horizontal', size_hint=(1, 0.7),pos_hint={'x':0,'y':0})# 空白layout
        # 二级分屏1.0
        layPart1_0=BoxLayout(orientation='vertical', size_hint=(0.1,1),pos_hint={'x':0,'y':0})
        layPart1_0.set_color(header_color)
        btn = Button(text="Back",size_hint=(0.15, 1))
        btn.background_color=header_color
        btn.color=(1,1,1,1)
        btn.bind(on_press=self.switch_to_first_screen)
        layPart1_0.add_widget(btn)
        layPart1.add_widget(layPart1_0)
        # 二级分屏2.0
        import_button = Button(text="以Excel文件格式导入(已停用)", size_hint=(1, 1),font_name='chinese_font')
        import_button.bind(on_press=self.show_file_chooser)
        layPart2.add_widget(import_button)
        # 二级分屏3.0
        import_from_internet_button=Button(text="从网络导入", size_hint=(1, 1),font_name='chinese_font')
        import_from_internet_button.bind(on_press=self.switch_to_third_screen)
        layPart3.add_widget(import_from_internet_button)
        root_layout.add_widget(layPart1)
        root_layout.add_widget(layPart2)
        root_layout.add_widget(layPart3)
        root_layout.add_widget(layPartn)




        self.add_widget(root_layout)


    def show_file_chooser(self, instance):#文件选择器(已荒废)
        # 弹出文件选择器
        file_chooser = FileChooserListView()
        file_chooser.bind(on_submit=self.import_excel_file)

        self.popup = Popup(title="Choose Excel File",content=file_chooser, size_hint=(0.9, 0.9))
        self.popup.content.font_name = 'chinese_font' 
        self.popup.open()
        

    def import_excel_file(self, instance, value, *args):#导入excel文件(目前已被荒废)
        # 在这里调用excel2dict函数，并传递文件路径
        file_path = value[0]
        self.result_dict = excel2dict(file_path)

        # 更新屏幕信息
        self.update_screen(self.result_dict)

        #消除popup后在转换位第一屏幕
        self.popup.dismiss()
        App.get_running_app().root.current = 'first'


    def update_screen(self, data_dict):
        # 根据返回的字典更新屏幕信息
        # 获取 Screen1 并调用更新按钮文本的方法
        screen1 = self.manager.get_screen('first')
        screen1.update_buttons_text(data_dict)

    def switch_to_third_screen(self, instance):
        # 获取屏幕管理器
        screen_manager = App.get_running_app().root
        self.manager.transition = SlideTransition(direction="left")
        # 切换到第一个屏幕
        screen_manager.current = 'third'


    def switch_to_first_screen(self, instance):
        # 获取屏幕管理器
        screen_manager = App.get_running_app().root
        self.manager.transition = SlideTransition(direction="right")
        # 切换到第一个屏幕
        screen_manager.current = 'first'
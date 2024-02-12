from . import Screen, App, SlideTransition, BoxLayout, Button, TextInput, Label, SeatableGet, os, datetime,\
            Popup

from . import window_height, window_width, current_file_path, current_date, header_color


class ThirdScreen(Screen):
    def __init__(self, **kwargs):
        super(ThirdScreen, self).__init__(**kwargs)
        #初始化数据
        self.week_number=3

        #抬头部分
        layoutPart1=BoxLayout(orientation='horizontal', size_hint=(1, 0.08),pos_hint={'x':0,'y':0.92})
        layoutPart1_1=BoxLayout(size_hint=(0.85, 1),pos_hint={'x':0.15,'y':0})
        layoutPart1_1.set_color(header_color)
        backButton = Button(text="Back", size_hint=(0.15, 1),font_name='chinese_font')
        backButton.background_color=header_color
        backButton.color=(1,1,1,1)
        backButton.bind(on_press=self.switch_to_second_screen)
        layoutPart1.add_widget(backButton)
        layoutPart1.add_widget(layoutPart1_1)
        

        layoutPart2=BoxLayout(orientation='vertical', size_hint=(1, 0.82),pos_hint={'x':0,'y':0.1})
        layoutPart2_0=BoxLayout(size_hint=(1,0.1),pos_hint={"x":0,"y":0.95})
        label_website=Label(text="鼓楼医院课程网站(Seatable)", font_size="15sp", font_name='chinese_font',halign="left",text_size=(window_width,None))
        label_website.color=(0,0,0,1)
        layoutPart2_0.add_widget(label_website)
        self.text_input1 = TextInput(text='https://cloud.seatable.cn/external-apps/42a2a20c-53ee-4817-8caa-2024044c770f/', multiline=True, font_size="15sp",size_hint=(1,0.1), font_name='chinese_font')

        layoutPart2_1=BoxLayout(size_hint=(1,0.1),pos_hint={"x":0,"y":0.75})
        label_university=Label(text="大学名称\n(南京大学, 徐州医科大学, 南京医科大学...)",font_size="15sp", halign="left" , font_name='chinese_font',text_size=(window_width,None))
        label_university.color=(0,0,0,1)
        layoutPart2_1.add_widget(label_university)
        self.text_input2 = TextInput(text='南京大学', multiline=True, font_size="15sp",size_hint=(1,0.1), font_name='chinese_font')

        layoutPart2_2=BoxLayout(size_hint=(1,0.1),pos_hint={"x":0,"y":0.55})
        label_university=Label(text="年级与班级\n(取决于表格内容, 注意区分\"2021临床医学\"与\"2021级临床医学\")",halign="left",font_size="15sp", font_name='chinese_font',text_size=(window_width,None))
        label_university.color=(0,0,0,1)
        layoutPart2_2.add_widget(label_university)
        self.text_input3 = TextInput(text='2021临床医学', multiline=True, font_size="15sp",size_hint=(1,0.1), font_name='chinese_font')

        layoutPart2_n=BoxLayout(size_hint=(1,0.3),pos_hint={"x":0,"y":0})

        layoutPart2.add_widget(layoutPart2_0)
        layoutPart2.add_widget(self.text_input1)
        layoutPart2.add_widget(layoutPart2_1)
        layoutPart2.add_widget(self.text_input2)
        layoutPart2.add_widget(layoutPart2_2)
        layoutPart2.add_widget(self.text_input3)
        layoutPart2.add_widget(layoutPart2_n)

        layoutPart3=BoxLayout(orientation='horizontal', size_hint=(1, 0.1),pos_hint={'x':0,'y':0})
        enterButton = Button(text="确认",size_hint=(1,1),font_name="chinese_font")
        enterButton.bind(on_press=self.enter_and_updata)
        layoutPart3.add_widget(enterButton)

        self.add_widget(layoutPart1)
        self.add_widget(layoutPart2)
        self.add_widget(layoutPart3)

    def enter_and_updata(self,instance):
        try:
            test=SeatableGet(self.text_input1.text,self.text_input2.text,self.text_input3.text)
            print(test)
            with open(os.path.join(os.path.dirname(current_file_path),"..","assets", "conf", "internetData.txt"),"r",encoding='utf-8') as f:
                a_cache=f.readlines()
                list_date=[]
                for i in a_cache:
                    list_cache=i.split(',')
                    list_date.append(list_cache[3][0:10])
                # 将日期字符串转换为 datetime 对象
                date_objects = [datetime.strptime(date_str, "%Y-%m-%d") for date_str in list_date]
                # 找到最早的日期
                self.start_date = min(date_objects)
                with open(os.path.join(os.path.dirname(current_file_path),"..","assets", "conf", "cache_data.txt"),"w",encoding='utf-8') as c:
                        c.writelines(datetime.strftime(self.start_date, "%Y-%m-%d"))
                # 计算每个日期距离最早日期的天数
                days_since_start = [(date - self.start_date).days for date in date_objects]
                # 计算每个日期所在的周数
                list_week = [int((days + self.start_date.weekday()) / 7) + 1 for days in days_since_start]
                # 计算今天所在的周数
                self.week_number = int(((current_date-self.start_date).days+self.start_date.weekday())/7)+1

            week_dic={}
            coun=0
            for i in list_week:
                if i in week_dic.keys():
                    week_dic[i].append([a_cache[coun]])
                else:
                    week_dic[i]=[[a_cache[coun]]]
                coun+=1
            for i in set(list_week):
                # 清空已有的部分
                with open(os.path.join(os.path.dirname(current_file_path),"..","assets", "conf", "internetData"+str(i)+".txt"),"w",encoding='utf-8'):
                    pass

                with open(os.path.join(os.path.dirname(current_file_path),"..","assets", "conf", "internetData"+str(i)+".txt"),"w+",encoding='utf-8') as f:
                    for j in week_dic[i]:
                        f.write(",".join(j))
            del a_cache
            del week_dic
            del list_week
            del coun

            #updata the screen1
            screen1 = self.manager.get_screen('first')
            screen1.updata_button_text_according2week(self.week_number)
            screen_manager = App.get_running_app().root
            self.manager.transition = SlideTransition(direction="right")
            # 切换到第一个屏幕
            screen_manager.current = 'first'
        except:
            print("网络异常或输入错误")
        if str(test)=="200":
            pass
        else:
            content_layout = BoxLayout(orientation='vertical')
            info_popup = Popup(title="导入失败"+str(test),
                            title_size="20sp",
                            title_font="chinese_font",
                            content=content_layout,
                            size_hint=(0.8, 0.6))
            info_popup.open()
    
    def choose_your_favorite_colour(self,instance):
        pass


    def switch_to_first_screen(self,instance):
        # 获取屏幕管理器
        screen_manager = App.get_running_app().root
        self.manager.transition = SlideTransition(direction="right")
        # 切换到第一个屏幕
        screen_manager.current = 'first'

    def switch_to_second_screen(self, instance):
        # 获取屏幕管理器
        screen_manager = App.get_running_app().root
        self.manager.transition = SlideTransition(direction="right")
        # 切换到第一个屏幕
        screen_manager.current = 'second'
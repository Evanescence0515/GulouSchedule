from . import ScreenManager, Screen, SlideTransition, App, Screen, datetime,\
    Button, GridLayout, LabelBase, BoxLayout, Label, DropDown,\
    FileChooserListView, Popup, Window, os, excel2dict, timedelta

from . import current_file_path, data_file_path, col_file_path,\
    chinese_font_path, window_width, window_height, current_date,\
    Button_color, Popup_color_background, header_color

from . import MyWidget

class FirstScreen(Screen):
    def __init__(self, **kwargs):
        super(FirstScreen, self).__init__(**kwargs)
        # 读取已有的数据1，如果没有，则放弃读取，设置当前周数为1
        try:
            with open(os.path.join(os.path.dirname(current_file_path),"..","assets", "conf", "cache_data.txt"),"r",encoding='utf-8') as f:
                self.start_date=datetime.strptime(f.readlines()[0],"%Y-%m-%d")
                self.week_number = int(((current_date-self.start_date).days+self.start_date.weekday())/7)+1
        except IOError:
            self.week_number=1
        except:
            print("初始化失败")
            self.week_number=1
        #初始化数据
        self.buttons = []
        self.weekday_number = current_date.weekday()
        # 获取当前所在周数的日期
        result_dates = self.get_week_dates(current_date)

        # 分屏
        root_layout = BoxLayout(orientation='vertical')
        # 一级分屏1
        layPart1 = BoxLayout(orientation='horizontal', size_hint=(1, 0.08),pos_hint={"x":0,"y":0.9})
        layPart1.set_color(Button_color)
        # 二级分屏1.0
        layPart1_0=BoxLayout(orientation='vertical', size_hint=(0.15, 1))
        # 周数的选择
        weekButton = Button(text='Weeks', size_hint=(1, 1))
        weekButton.color=(1,1,1,1)
        weekButton.background_color=header_color
        weekButton.bind(on_release=self.show_dropdown)

        layPart1_0.add_widget(weekButton)


        # 二级分屏1.1
        layPart1_1=BoxLayout(orientation='vertical', size_hint=(0.85, 1),pos_hint={"x":0.1,"y":0})
        header_label = Label(text="鼓楼课表", font_size='25sp', font_name='chinese_font')
        header_label.color=(1,1,1,1)
        header_label.set_color(header_color)

        layPart1_1.add_widget(header_label)


        # 二级分屏1.2
        layPart1_2=BoxLayout(orientation='vertical', size_hint=(0.15, 1),pos_hint={"x":0.9,"y":0})
        # 数据导入的标签
        btn = Button(text="工具",size_hint=(1, 1), size=(1,1),font_name='chinese_font')
        btn.color=(1,1,1,1)
        btn.background_color=header_color
        btn.bind(on_press=self.switch_to_second_screen)

        layPart1_2.add_widget(btn)
        layPart1.add_widget(layPart1_0)# end 二级分屏1.0
        layPart1.add_widget(layPart1_1)# end 二级分屏1.1
        layPart1.add_widget(layPart1_2)# end 二级分屏1.2
        
        # 一级分屏2
        #layPart2 = BoxLayout(orientation='horizontal', size_hint=(1, 0.2),pos_hint={"x":0.6,""})
        #header_label = Label(text="Your date data", font_size=20, font_name='chinese_font')
        #layPart2.add_widget(header_label)
        
        # 一级分屏3
        layPart3 = BoxLayout(orientation='horizontal', size_hint=(1, 0.9))

        grid_layout = MyWidget.Background_GridLayout(cols=8, rows=13, spacing=(2, 0), padding=0)

        # 从文件中读取数据
        data = self.read_data_from_file(data_file_path)
        self.config_row=["周一","周二","周三","周四","周五","周六","周日"]
        config_col=range(1,13)

        # 向 GridLayout 中添加按钮，每个按钮表示一个方格
        self.weekday_buttons=[]
        for row in range(0,13):
            for col in range(0,8):
                if row==0 and col==0:
                    button = Button(text=current_date.strftime('%m-%d'), halign='center', valign='center',text_size=(window_width/8,window_height*0.9/13),font_size="15sp",font_name='chinese_font') 
                    button.color=(0,0,0,1)
                    button.border=(10,10,10,10)
                    grid_layout.add_widget(button)
                elif row==0:
                    if col-1==self.weekday_number:
                        button = Button(text=self.config_row[col-1]+"\n"+result_dates[col-1][-5:], halign='center', valign='center',text_size=(window_width/8,window_height*0.9/13),font_size="15sp",font_name='chinese_font')  # 初始文本为空，设置字体大小
                        grid_layout.add_widget(button)
                        button.border=(0,10,10,0)
                        button.color=(0,0,0,1)
                        self.weekday_buttons.append(button)
                    else:
                        button = Button(text=self.config_row[col-1]+"\n"+result_dates[col-1][-5:], halign='center', valign='center',text_size=(window_width/8,window_height*0.9/13), font_size="15sp",font_name='chinese_font')  # 初始文本为空，设置字体大小
                        grid_layout.add_widget(button)
                        button.border=(0,10,10,0)
                        button.color=(0,0,0,1)
                        self.weekday_buttons.append(button)
                elif col==0:
                    button = Button(text=str(config_col[row-1]), halign='center', valign='center',text_size=(window_width/8,window_height*0.9/13),font_size="20sp",font_name='chinese_font')  # 初始文本为空，设置字体大小
                    button.border=(0,0,0,0)
                    button.color=(0,0,0,1)
                    grid_layout.add_widget(button)
                else:
                    button = Button(text=data[row-1][col-1],halign='center',  valign='center',text_size=(window_width/8,window_height*0.9/13), font_size="10sp",font_name='chinese_font',background_normal="")  # 初始文本为空，设置字体大小
                    button.color=(0,0,0,0.8)
                    button.additional_info = ["课程信息",'无信息']
    
                    button.bind(on_press=self.on_button_press)  # 绑定按钮点击事件
                    grid_layout.add_widget(button)
                    self.buttons.append(button)

        self.updata_button_text_according2week(self.week_number)

        layPart3.add_widget(grid_layout)

        root_layout.add_widget(layPart1)
        #root_layout.add_widget(layPart2)
        root_layout.add_widget(layPart3)

        self.add_widget(root_layout)


        

    week="1"
    # 周数的下拉菜单
    def show_dropdown(self, button):
        dropdown = DropDown()
        options = ["第{}周".format(week) for week in range(1, 26)]

        for option_text in options:
            btn_week = Button(text=option_text, size_hint_y=None, height="30sp",font_name='chinese_font')
            btn_week.bind(on_release=lambda btn, option=option_text: self.on_option_select(self.week,option[1:-1]))
            dropdown.add_widget(btn_week)

        # Attach the dropdown to the button and open it
        dropdown.open(button)


    def on_option_select(self, label, option):#label是要修改的部分, 后续这个将会被改成我grid里面的所有数值, option是选择的周数
        # This method is called when an option is selected from the dropdown
        self.week_number=int(option)
        self.updata_button_text_according2week(self.week_number)

    def read_data_from_file(self, filename):
        data = []
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                for line in file:
                    row_data = line.strip().split(',')
                    data.append(row_data)
        except Exception as e:
            print(f"Error reading data from file: {e}")

        return data

    def update_buttons_text(self, data):
        with open(col_file_path) as f:
            color_list=f.readlines()

        for i in range(len(self.buttons)):
            self.buttons[i].text= ''  # 初始文本为空，设置字体大小
            self.buttons[i].background_color = (1, 1, 1, 1)
            self.buttons[i].additional_info = ["课程信息",'无信息']

        if self.week_number in data.keys():
            # 更新按钮的文本
            data=data[self.week_number]
            chinese2num={'一': 1,'二': 2, '三': 3,'四': 4,'五': 5,'六': 6,'日': 7,}
            col_c=0

            for i in data:
                for j in i["时间（见习课）"]:
                    col_c+=1

                    coun=chinese2num[i["星期"]]-1+int(j[0])*7
                    self.buttons[coun].text="\n".join([i["科目"],i["地点（见习课）"],"组别"+j[1:]])
                    col_rbga=color_list[col_c].split(",")
                    col_rbga=list(map(lambda x:int(x)/255,col_rbga[0:3]))
                    col_rbga.append(0.9)
                    self.buttons[coun].background_color = col_rbga
                    self.buttons[coun+7].background_color = col_rbga
                    output_string = '\n'.join([f"{key}: {', '.join(value) if isinstance(value, list) else value}" for key, value in i.items()])
                    self.buttons[coun].additional_info = [i["科目"],output_string]
                    self.buttons[coun+7].additional_info =[i["科目"],output_string]

    def updata_button_text_according2data(self,data):
        with open(col_file_path) as f:
            color_list=f.readlines()

        for i in range(len(self.buttons)):
            self.buttons[i].text= ''  # 初始文本为空，设置字体大小
            self.buttons[i].background_color = (1, 1, 1, 1)
            self.buttons[i].additional_info = ["课程信息",'无信息']


    def updata_button_text_according2week(self,week=1):
        with open(col_file_path) as f:
            color_list=f.readlines()

        for i in range(len(self.buttons)):
            self.buttons[i].text= ''  # 初始文本为空，设置字体大小
            self.buttons[i].background_color = (1, 1, 1, 1)
            self.buttons[i].additional_info = ["课程信息",'无信息']
        # 改变抬头

        result_dates = self.get_week_dates(self.start_date+timedelta(days=7*week-7))
        for i in range(len(self.weekday_buttons)):
            self.weekday_buttons[i].text=self.config_row[i]+"\n"+result_dates[i][-5:]  # 初始文本为空，设置字体大小

        col_c=0
        try:
            chinese2num={'一': 1,'二': 2, '三': 3,'四': 4,'五': 5,'六': 6,'日': 7,}
            with open(os.path.join(os.path.dirname(current_file_path),"..","assets", "conf", "internetData"+str(week)+".txt"),"r",encoding='utf-8') as f:
                a_cache=f.readlines()
                for i in a_cache:
                    list_cache=i.split(",")
                    col_rbga=color_list[col_c].split(",")
                    col_rbga=list(map(lambda x:int(x)/255,col_rbga[0:3]))
                    col_rbga.append(0.9)
                    if list_cache[5]!="None":
                        classTime_cache=list_cache[5].split("-")

                        for j in range(int(classTime_cache[0]),int(classTime_cache[1])+1):
                            if j==int(classTime_cache[0]):
                                coun=chinese2num[list_cache[4]]-1+(int(j)-1)*7
                                self.buttons[coun].text="\n".join([list_cache[2],list_cache[10]])
                            else:
                                coun=chinese2num[list_cache[4]]-1+(int(j)-1)*7
                            self.buttons[coun].background_color = col_rbga
                            output_string = '\n'.join(['授课老师: '+list_cache[8],"授课地点: "+list_cache[10],"授课内容:"+list_cache[7]])
                            self.buttons[coun].additional_info = [list_cache[2],output_string]
                    if list_cache[11]!="None":
                        classTime_cache=self.practice_time_justice(list_cache[11])
                        #这是全天的课程，绷不住了
                        if classTime_cache[0]=="全天":
                            coun=chinese2num[list_cache[4]]-1
                            self.buttons[coun].text="\n".join([list_cache[2],list_cache[15]])
                            output_string = '\n'.join(["实践课:",list_cache[13],list_cache[15],list_cache[12]])
                            for k in range(0,12):
                                self.buttons[coun+7*k].additional_info = [list_cache[2],output_string]
                                self.buttons[coun+7*k].background_color = col_rbga
                        else:
                            for k in classTime_cache:
                                coun=chinese2num[list_cache[4]]-1+(k[0])*7
                                self.buttons[coun].text="\n".join([list_cache[2],list_cache[15]])
                                self.buttons[coun].background_color = col_rbga
                                self.buttons[coun+7].background_color = col_rbga
                                output_string = '\n'.join(["实践课:","授课老师: "+list_cache[13],"授课地点: "+list_cache[15].rstrip(),"授课内容: "+list_cache[12]])
                                self.buttons[coun].additional_info = [list_cache[2],output_string]
                                self.buttons[coun+7].additional_info =[list_cache[2],output_string]
                    col_c+=1
                del a_cache
        except IOError:
            print("超出课程周数")
            for i in range(len(self.buttons)):
                self.buttons[i].text= ''  # 初始文本为空，设置字体大小
                self.buttons[i].background_color = (1, 1, 1, 1)
                self.buttons[i].additional_info = ["课程信息",'无信息']


    def practice_time_justice(self,time):
        time=time.split("、")
        classTime_list=[]
        for j in time:
            if j=="全天":# 为什么有人会输入全天?有没有点武德了
                return ["全天",'']
            if j[-1].isdigit()==1:
                if len(j)==4:
                    t_time=(int(j[0:1])-8)
                    classTime_list.append([t_time,""])
                else:
                    if j[0:2]<='12':
                        t_time=(int(j[0:2])-8)
                        classTime_list.append([t_time,''])
                    elif j[0:2]>'12' and j[0:2]<'18':
                        t_time=(int(j[0:2])-14)+4
                        classTime_list.append([t_time,''])
                    elif j[0:2]>'18':
                        t_time=8
                        classTime_list.append([t_time,''])
            else:   
                if j[1].isdigit()==0:
                    t_time=(int(j[0:1])-8)
                    classTime_list.append([t_time,j[4:]])
                elif j[0:2]<='12':
                    t_time=(int(j[0:2])-8)
                    classTime_list.append([t_time,j[5:]])
                elif j[0:2]>'12' and j[0:2]<'18':
                    t_time=(int(j[0:2])-14)+4
                    classTime_list.append([t_time,j[5:]])
                elif j[0:2]>'18':
                    t_time=8
                    classTime_list.append([t_time,j[5:]])
        return classTime_list
        

    def switch_to_second_screen(self, instance):
        # 获取屏幕管理器
        screen_manager = App.get_running_app().root
        self.manager.transition = SlideTransition(direction="left")
        # 切换到第二个屏幕
        screen_manager.current = 'second'


    def on_button_press(self, instance):
        # 打开课程具体信息
        additional_info = instance.additional_info

        # 创建关闭按钮
        close_button = Button(text='关闭', font_name="chinese_font", size_hint=(0.1, 0.1), pos_hint={"x": 0.9, "y": 0}, on_press=lambda x: info_popup.dismiss())
        close_button.background_color=(0,0,0,0)
        close_button.color=(1,1,1,1)

        layout_label=BoxLayout(size_hint=(1,0.9))
        layout_label.set_color((0,0,0,0))

        label = Label(text=additional_info[1],color=(1,1,1,1),font_name="chinese_font",halign='left',valign="top",size_hint=(1,1),font_size="20sp",text_size=(window_width*0.75,None),pos_hint={"x":0,"y":0})
        label.set_color((1,1,1,0))
        # 创建包含 Label 和关闭按钮的布局
        content_layout = BoxLayout(orientation='vertical')
        content_layout.set_color((0,0, 0,0))
        layout_label.add_widget(label)

        content_layout.add_widget(layout_label)
        content_layout.add_widget(close_button)

        #创建popup
        info_popup = Popup(title=additional_info[0],
                           title_size="20sp",
                        title_font="chinese_font",
                        content=content_layout,
                        size_hint=(0.8, 0.7),
                        background_color=Popup_color_background)
        info_popup.open()


    def get_week_dates(self,target_date):
        # 将输入的日期字符串转换为 datetime 对象
        target_datetime = target_date
        # 获取该天是星期几（0表示星期一，6表示星期日）
        day_of_week = target_datetime.weekday()
        # 计算该天到该周第一天的天数差
        days_since_start_of_week = day_of_week
        # 计算该周的第一天
        start_of_week = target_datetime - timedelta(days=days_since_start_of_week)
        # 获取该周的每天日期
        week_dates = [start_of_week + timedelta(days=i) for i in range(7)]
        # 将日期格式化为字符串
        week_dates_str = [date.strftime("%Y-%m-%d") for date in week_dates]
        return week_dates_str
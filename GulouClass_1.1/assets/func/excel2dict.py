# import pandas as pd

def excel2dict(path):
    data_frame=pd.read_excel(path)# 此处后续将会自动导入
    data_list = list(data_frame.to_dict(orient='records'))
    data_dict={}
    for i in data_list:
        classTime=i["时间（见习课）"].split("、")
        classTime_list=[]
        for j in classTime:
            if j[1].isdigit()==0:
                t_time=(int(j[0:1])-8)
                classTime_list.append(str(t_time)+j[5:])
            elif j<='12':
                t_time=(int(j[0:2])-8)
                classTime_list.append(str(t_time)+j[5:])
            elif j>'12' and j<'18':
                t_time=(int(j[0:2])-14)+4
                classTime_list.append(str(t_time)+j[5:])
            elif j>'18':
                t_time=8
                classTime_list.append(str(t_time)+j[5:])
        i["时间（见习课）"]=classTime_list
        if i["周次"] in data_dict:
            data_dict[i['周次']].append(i)
        else:
            data_dict[i['周次']]=[i]
    return data_dict


import os
import pandas as pd


#该程序将计算得到的每个水面的水量加和，得到某个时期某片区域的总水量
excel_path = r'D:\python_Scripts\volumeComByDEM\excel_res'
project_path = r'D:\python_Scripts\volumeComByDEM'

sta = {}
sta['time']=[]
sta['area']=[]
sta['vol']=[]

for excel_file in os.listdir(excel_path):
    sta['time'].append(excel_file[8:12]+'-'+excel_file[12:14]+'-'+excel_file[14:16])
    df = pd.read_excel(os.path.join(excel_path,excel_file))
    sum_area=0
    sum_vol=0
    for i in range(len(df['area'])):
        if(df['volume'][i] != 99999):
            sum_area+=df['area'][i]
            sum_vol += df['volume'][i]
    sta['area'].append(sum_area)
    sta['vol'].append(sum_vol)

f2=pd.DataFrame.from_dict(sta)
f2.to_excel(os.path.join(project_path,'total.xlsx'), encoding='utf-8', index=False)

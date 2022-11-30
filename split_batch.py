import os
import arcpy
import re

#该程序主要针对一个shp中包含多个水面的数据，负责shp进行分割，使得分割后的shp中只包含一个水面
#每个shp分割后得到的水面会输出在一个文件夹中，文件夹名是捕获shp文件名中的时间


lake_shp_file = r'D:\python_Scripts\volumeComByDEM\clip_water1'
split_path = r'D:\python_Scripts\volumeComByDEM\split'

for lake_shp in os.listdir(lake_shp_file):
    if(lake_shp.split('.')[-1]=='shp'):

        raw_hrefs = re.findall('20[0-9]+', lake_shp, 0)
        filename = 'Taitema_'+raw_hrefs[0]

        new_file = os.path.join(split_path,filename)
        if(not os.path.exists(new_file)):
            os.mkdir(new_file)
        arcpy.SplitByAttributes_analysis(os.path.join(lake_shp_file,lake_shp), new_file, ["id_num"])
        print(filename)
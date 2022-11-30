# -*- coding:utf-8 -*-
import os
import numpy as np
import arcpy
import pandas as pd
from arcpy.sa import ExtractValuesToPoints
import openpyxl

project_path = r'D:\python_Scripts\volumeComByDEM'
terr_DEM = r'D:\python_Scripts\volumeComByDEM\DEM\TaitemaLake.tif'
# water_ground_gdb = os.path.join(project_path, 'water_ground.gdb')
# water_ground_path = os.path.join(project_path, 'water_ground')
water_ground_split_path = os.path.join(project_path, 'split')


for file in os.listdir(water_ground_split_path):
    print('*****************')
    print(file)
    cut_fill_error_file = []
    p2r_fill_error_file = []
    polygon_height={}
    polygon_file_path = os.path.join(water_ground_split_path,file)
    toLine_file_path = os.path.join(polygon_file_path, 'a_toLine')
    toPoint_file_path = os.path.join(polygon_file_path, 'b_toPoint')
    v_Point_file_path = os.path.join(polygon_file_path, 'c_vPoint')
    # dem_c_file_path = os.path.join(polygon_file_path, 'e_dem_c')

    polygon2R_file_path = os.path.join(polygon_file_path, 'h_polygon2R')
    cutfill_file_path = os.path.join(polygon_file_path, 'i_cutfill')

    #面转线
    print('面转线')
    for polygon_file in os.listdir(polygon_file_path):
        if not os.path.exists(toLine_file_path):
            os.mkdir(toLine_file_path)
        if polygon_file[-4:] == '.shp':
            arcpy.FeatureToLine_management(os.path.join(polygon_file_path,polygon_file),
                                           os.path.join(toLine_file_path,polygon_file),
                                           "0.001 Meters", "ATTRIBUTES")

            Fieldlist=[]
            tmp = arcpy.ListFields(os.path.join(polygon_file_path, polygon_file))
            for Field in tmp:
                Fieldlist.append(Field.name)
            print(Fieldlist)
            if 'AreaKM2' not in Fieldlist:
                arcpy.AddField_management(os.path.join(polygon_file_path,polygon_file), "AreaKM2", "DOUBLE", "", "",
                                          "", "", "NULLABLE", "NON_REQUIRED", "")
            if 'height' not in Fieldlist:
                arcpy.AddField_management(os.path.join(polygon_file_path, polygon_file), "height", "DOUBLE", "", "",
                                          "", "", "NULLABLE", "NON_REQUIRED", "")
            arcpy.CalculateField_management(os.path.join(polygon_file_path,polygon_file), "AreaKM2",
                                            "!shape.geodesicArea@SQUAREKILOMETERS!", "PYTHON_9.3")

            tmp = arcpy.SearchCursor(os.path.join(polygon_file_path,polygon_file), ['AreaKM2'])
            area = tmp.next().AreaKM2
            polygon_height[polygon_file[:-4]] = [area]

    #线转点
    print('线转点')
    for line_file in os.listdir(toLine_file_path):
        if not os.path.exists(toPoint_file_path):
            os.mkdir(toPoint_file_path)
        if line_file[-4:] == '.shp':
            arcpy.FeatureVerticesToPoints_management(os.path.join(toLine_file_path, line_file),
                                           os.path.join(toPoint_file_path, line_file), "ALL")

    #点提取高程值
    print('点提取高程值')
    for point_file in os.listdir(toPoint_file_path):

        if not os.path.exists(v_Point_file_path):
            os.mkdir(v_Point_file_path)
        if point_file[-4:] == '.shp':
            # print(point_file)
            arcpy.CheckOutExtension("Spatial")
            ExtractValuesToPoints(os.path.join(toPoint_file_path, point_file), terr_DEM,
                                  os.path.join(v_Point_file_path, point_file),
                                  "INTERPOLATE", "VALUE_ONLY")

    #计算点的中位高程值作为湖面的高程
    print('计算点的中位高程值作为湖面的高程')
    for vpoint_file in os.listdir(v_Point_file_path):
        height_list=[]
        if vpoint_file[-4:] == '.shp':
            # 计算中位值
            heights = arcpy.SearchCursor(os.path.join(v_Point_file_path, vpoint_file), ['RASTERVALU'])
            while True:
                height = heights.next()
                if not height:
                    break
                height_list.append(height.RASTERVALU)
            if(len(height_list)==0):
                height_median = 99999
            else:
                height_median = np.median(height_list)
            polygon_height[vpoint_file[:-4]].append(height_median)

    for polygon_file in os.listdir(polygon_file_path):
        if polygon_file[-4:] == '.shp':
            cursor = arcpy.UpdateCursor(os.path.join(polygon_file_path, polygon_file))
            for row in cursor:
                # print(fiel[:-4])
                row.setValue("height", polygon_height[polygon_file[:-4]][1])
                cursor.updateRow(row)

    #根据湖面裁剪DEM
    # print('根据湖面裁剪DEM')
    # for polygon_file in os.listdir(polygon_file_path):
    #     if not os.path.exists(dem_c_file_path):
    #         os.mkdir(dem_c_file_path)
    #     if polygon_file[-4:] == '.shp':
    #         arcpy.env.parallelProcessingFactor = 0
    #         arcpy.Clip_management(terr_DEM, "595952.688 4355189.046 686502.688 4389459.046",
    #                               os.path.join(dem_c_file_path, polygon_file[:-4]+'.tif'),
    #             os.path.join(polygon_file_path, polygon_file), "", "ClippingGeometry", "NO_MAINTAIN_EXTENT")


    #将湖面转成DEM，高程为湖面高程
    print('将湖面转成DEM，高程为湖面高程')
    for polygon_file in os.listdir(polygon_file_path):
        if not os.path.exists(polygon2R_file_path):
            os.mkdir(polygon2R_file_path)
        if polygon_file[-4:] == '.shp':
            inFeatures = os.path.join(polygon_file_path, polygon_file)
            valField = "height"
            outRaster = os.path.join(polygon2R_file_path, polygon_file[:-4]+'.tif')
            assignmentType = "MAXIMUM_AREA"
            priorityField = ""
            cellSize = 10

            # Execute PolygonToRaster
            try:
                arcpy.PolygonToRaster_conversion(inFeatures, valField, outRaster,
                                             assignmentType, priorityField, cellSize)
            except:
                p2r_fill_error_file.append(polygon_file[:-4])
                cut_fill_error_file.append(polygon_file[:-4])
                # polygon_height[polygon_file[:-4]].append('99999')


    #计算两个DEM的差，求得体积
    print('计算两个DEM的差，求得体积')
    for polygon2R_file in os.listdir(polygon2R_file_path):
        if not os.path.exists(cutfill_file_path):
            os.mkdir(cutfill_file_path)
        if polygon2R_file[-4:] == '.tif':
            if polygon2R_file[:-4] in p2r_fill_error_file:
                continue
            inBeforeRaster = terr_DEM
            inAfterRaster = os.path.join(polygon2R_file_path, polygon2R_file)
            outRaster = os.path.join(cutfill_file_path, polygon2R_file)
            zFactor = 1
            arcpy.CheckOutExtension("3D")
            try:
                arcpy.CutFill_3d(inBeforeRaster, inAfterRaster, outRaster, zFactor)
            except:
                cut_fill_error_file.append(polygon2R_file[:-4])
                # polygon_height[polygon2R_file[:-4]].append('99999')

    for cutfill_file in os.listdir(cutfill_file_path):
        if cutfill_file[-4:] == '.tif':
            volumes = arcpy.SearchCursor(os.path.join(cutfill_file_path, cutfill_file), ['VOLUME'])
            sum_vol=0
            while True:
                volume = volumes.next()
                if not volume:
                    break
                if(volume.VOLUME<0):
                    sum_vol-=volume.VOLUME
            polygon_height[cutfill_file[:-4]].append(sum_vol)

    table=[]
    for key in polygon_height.keys():
        data = {}
        if(key in cut_fill_error_file or key in p2r_fill_error_file):
            data['split_id'] = key
            data['area'] = polygon_height[key][0]
            data['height'] = polygon_height[key][1]
            data['volume'] = '99999'
            table.append(data)
        else:
            data['split_id']=key
            data['area'] = polygon_height[key][0]
            data['height'] = polygon_height[key][1]
            data['volume'] = polygon_height[key][2]
        table.append(data)

    pf = pd.DataFrame(table)
    # 指定字段顺序
    order = ['split_id', 'area', 'height','volume']
    pf = pf[order]
    file_path = os.path.join(project_path,file+'.xlsx')
    # 替换空单元格
    pf.fillna(' ', inplace=True)
    # 输出
    pf.to_excel(file_path, encoding='utf-8', index=False)
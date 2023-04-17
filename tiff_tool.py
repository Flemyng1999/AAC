from osgeo import gdal
import numpy as np


# 简单读取文件
def readTiff(file, datatype=np.float32):
    data_set = gdal.Open(file, gdal.GA_ReadOnly)
    if data_set is None:
        print(file + "文件无法打开")
        return
    img_width = data_set.RasterXSize
    img_height = data_set.RasterYSize
    img_data = data_set.ReadAsArray(0, 0, img_width, img_height)
    img_data = img_data.astype(datatype)
    return data_set, img_data


# 简单读取文件，返回投影、仿射矩阵
def readPG(file, datatype=np.float32):
    data_set = gdal.Open(file, gdal.GA_ReadOnly)
    if data_set is None:
        print(file + "文件无法打开")
        return
    im_proj = data_set.GetProjection()  # 获取投影信息
    im_geotrans = data_set.GetGeoTransform()  # 获取仿射矩阵信息
    return im_proj, im_geotrans


# 简单读取文件，只返回数组
def readTiffArray(file, datatype=np.float32):
    data_set = gdal.Open(file, gdal.GA_ReadOnly)
    if data_set is None:
        print(file + "文件无法打开")
        return
    data_set = gdal.Open(file)
    img_width = data_set.RasterXSize
    img_height = data_set.RasterYSize
    img_data = data_set.ReadAsArray(0, 0, img_width, img_height)
    img_data = img_data.astype(datatype)
    return img_data


# 简单读取文件，只返回数据
def readTiffData(file, datatype=np.float32):
    data_set = gdal.Open(file, gdal.GA_ReadOnly)
    if data_set is None:
        print(file + "文件无法打开")
        return
    return data_set


# 写入新tiff
def writeTiff(data_set_1, img_data, save_path):
    min_ = np.min(img_data)
    max_ = np.max(img_data)
    if max_ <= 4000:
        datatype = gdal.GDT_Float32
    elif min_ >= 0 and max_ > 4000:
        datatype = gdal.GDT_Int32
    else:
        datatype = gdal.GDT_Float32

    im_proj = data_set_1.GetProjection()  # 获取投影信息
    im_geotrans = data_set_1.GetGeoTransform()  # 获取仿射矩阵信息

    if len(img_data.shape) == 3:
        im_bands, im_height, im_width = img_data.shape
    elif len(img_data.shape) == 2:
        im_height, im_width = img_data.shape
        im_bands = 1
    else:
        im_height, im_width = img_data.shape
        im_bands = 1

    # 创建文件
    driver = gdal.GetDriverByName("GTiff")
    new_dataset = driver.Create(save_path, im_width, im_height, im_bands, datatype)

    if new_dataset is not None:
        new_dataset.SetGeoTransform(im_geotrans)  # 写入仿射变换参数
        new_dataset.SetProjection(im_proj)  # 写入投影

    if im_bands == 1:  # 单层tif
        new_dataset.GetRasterBand(1).WriteArray(img_data)
    else:
        for i in range(im_bands):  # 多层tif（超立方）
            new_dataset.GetRasterBand(i+1).WriteArray(img_data[i])
    del new_dataset


# 写入新tiff
def writeTiff_SE(im_proj, im_geotrans, img_data, save_path):
    # min_ = np.min(img_data)
    # max_ = np.max(img_data)
    # if max_ <= 4000:
    #     datatype = gdal.GDT_Float32
    # elif min_ >= 0 and max_ > 4000:
    #     datatype = gdal.GDT_Int64
    # else:
    #     datatype = gdal.GDT_Float32

    if len(img_data.shape) == 3:
        im_bands, im_height, im_width = img_data.shape
    elif len(img_data.shape) == 2:
        im_height, im_width = img_data.shape
        im_bands = 1
    else:
        im_height, im_width = img_data.shape
        im_bands = 1

    # 创建文件
    driver = gdal.GetDriverByName("GTiff")
    new_dataset = driver.Create(save_path, im_width, im_height, im_bands, gdal.GDT_UInt16)

    if new_dataset is not None:
        new_dataset.SetGeoTransform(im_geotrans)  # 写入仿射变换参数
        new_dataset.SetProjection(im_proj)  # 写入投影

    if im_bands == 1:  # 单层tif
        new_dataset.GetRasterBand(1).WriteArray(img_data)
    else:
        for i in range(im_bands):  # 多层tif（超立方）
            new_dataset.GetRasterBand(i+1).WriteArray(img_data[i])
    del new_dataset


if __name__ == '__main__':
    dataset, arr = readTiff(r"D:\2022_8_14_sunny\4rad\rad.bip")
    writeTiff(dataset, arr, r"D:\2022_8_14_sunny\4rad\rad111.bip")

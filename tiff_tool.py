import os
from osgeo import gdal
import numpy as np
import time


# 简单读取文件
def read_tif(file_path: str) -> (np.ndarray, tuple, str): # type: ignore
    # Open the file using gdal
    ds = gdal.Open(file_path)
    if ds is None:
        print(file_path + "file can't open")
        return

    # Get the image size
    width = ds.RasterXSize
    height = ds.RasterYSize

    # Read the data into numpy arrays
    data_ = ds.ReadAsArray(0, 0, width, height)

    # Get the geotransform and projection information
    geotransform_ = ds.GetGeoTransform()
    projection_ = ds.GetProjection()

    # Close the gdal dataset
    del ds

    return data_, geotransform_, projection_


# 简单读取文件，只返回数组
def read_tif_array(file: str)-> np.ndarray:
    data_set = gdal.Open(file, gdal.GA_ReadOnly)
    if data_set is None:
        print(file + "文件无法打开")
        return # type: ignore
    data_set = gdal.Open(file)
    img_width = data_set.RasterXSize
    img_height = data_set.RasterYSize
    img_data = data_set.ReadAsArray(0, 0, img_width, img_height)
    del data_set
    return img_data


# 写入新tiff
def write_tif(save_path:str, data_:np.ndarray, geotransform_:tuple, projection_:str):
    # set dtype by its size and range
    min_value = np.min(data_)
    max_value = np.max(data_)

    if min_value >= 0 and 1024 <= max_value < 65535:
        output_dtype = gdal.GDT_UInt16
    elif -32768 < min_value <= -1024 and max_value < 32767:
        output_dtype = gdal.GDT_Int16
    else:
        output_dtype = gdal.GDT_Float32

    if len(data_.shape) == 3:
        im_bands, im_height, im_width = data_.shape
    elif len(data_.shape) == 2:
        im_height, im_width = data_.shape
        im_bands = 1
    else:
        im_height, im_width = data_.shape
        im_bands = 1

    # 创建文件
    driver = gdal.GetDriverByName("GTiff")
    new_dataset = driver.Create(save_path, im_width, im_height, im_bands, output_dtype)

    if new_dataset is not None:
        new_dataset.SetGeoTransform(geotransform_)  # 写入仿射变换参数
        new_dataset.SetProjection(projection_)  # 写入投影

    if im_bands == 1:  # 单层tif
        new_dataset.GetRasterBand(1).WriteArray(data_)
    else:
        for i in range(im_bands):  # 多层tif（超立方）
            new_dataset.GetRasterBand(i+1).WriteArray(data_[i])
    del new_dataset, driver, data_


if __name__ == '__main__':
    # Example usage
    dir_path = r"D:\2022_7_5_sunny"
    input_file = os.path.join(dir_path, "4rad", "rad.bip")
    output_file = os.path.join(dir_path, "4rad", "rad_readwrite_demo.bip")

    s_t = time.time()
    data, geotransform, projection = read_tif(input_file) # type: ignore
    e_t = time.time()
    print("Read tif took {} seconds".format(e_t - s_t))

    s_t = time.time()
    write_tif(output_file, data, geotransform, projection)
    e_t = time.time()
    print("Write tif took {} seconds".format(e_t - s_t))

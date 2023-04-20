import os
import numpy as np
import tiff_tool as tt
import all_sides as side


def pixel_info(arr):

    center = side.center_line(arr)
    center = np.array(center)  # 将list转化为array
    pixel_index = np.argwhere(arr != 0)  # 返回tif中所有非0像素的索引,行、列在一起
    pixel_index2 = np.where(arr != 0)  # 返回tif中所有非0像素的索引，行、列分开
    linear_model = np.polyfit(center[:, 0], center[:, 1], 1)  # 求出拟合直线方程的两个参数

    distance = abs(pixel_index2[1] - linear_model[0] * pixel_index2[0] - linear_model[1]) / pow(
        1 + linear_model[0] * linear_model[0], 0.5)

    pix_info = np.c_[pixel_index, distance]
    return pix_info, distance


def pixel(arr):
    pixel_index = np.argwhere(arr != 0)  # 返回tif中所有非0像素的索引
    return pixel_index


if __name__ == "__main__":
    # path
    dir_path = r"E:\2022_8_16_sunny"
    tif_name = "rad_part.bip"

    # data
    array = tt.read_tif_array(os.path.join(dir_path, "4rad", tif_name))
    index_, dist_ = pixel_info(array[100, :, :])

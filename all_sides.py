import numpy as np
import tiff_tool as tt


# 获取数组非0（建议NDVI）矩形上长边所有pixel的位置
def up_sides(img_data):
    var = img_data.shape
    up_side = []  # 创建一个空列表
    n = 3000
    for i in range(var[1]):
        for j in range(var[0]):
            if img_data[j, i] != 0 and j <= n:
                up_side.append(np.array((j, i)))
                n = j
                break
    return up_side

def down_sides(img_data):
    var = img_data.shape
    down_side = []  # 创建一个空列表
    n_1 = list(range(var[0]))
    n_2 = list(range(var[1]))
    n_1.reverse()
    n_2.reverse()
    n = 1
    for i in n_2:
        for j in n_1:
            if img_data[j, i] != 0 and j >= n:
                down_side.append(np.array((j, i)))
                n = j
                break
    down_side.reverse()  # 将down_side转向
    return down_side

# def down_sides(img_data):
#     var = img_data.dist_shape
#     down_side = []  # 创建一个空列表
#     #  创建一个反向迭代的循环条件
#     n_1 = list(range(var[0]))
#     n_2 = list(range(var[1]))
#     n_1.reverse()
#     n_2.reverse()
#     m = 0
#     for i in n_1:
#         for j in n_2:
#             if img_data[i, j] != 0 and j >= m:
#                 down_side.append(np.array((i, j)))
#                 m = j
#                 break
#     down_side.reverse()  # 将down_side转向
#     return down_side


def right_sides(img_data):
    var = img_data.shape
    right_side = []  # 创建一个空列表
    #  创建一个反向迭代的循环条件
    n_1 = list(range(var[1]))
    n_1.reverse()
    m = 0
    for i in range(var[0]):
        for j in n_1:
            if img_data[i, j] != 0 and j >= m:
                right_side.append(np.array((i, j)))
                m = j
                break
    return right_side


def left_sides(img_data):
    var = img_data.shape
    left_side = []  # 创建一个空列表
    #  创建一个反向迭代的循环条件
    n_1 = list(range(var[0]))
    n_1.reverse()
    m = 3000
    for i in n_1:
        for j in range(var[1]):
            if img_data[i, j] != 0 and j <= m:
                left_side.append(np.array((i, j)))
                m = j
                break
    left_side.reverse()  # 将left_side转向
    return left_side


def center_line(img_data):
    up_side = up_sides(img_data)
    down_side = down_sides(img_data)
    if len(up_side) > len(down_side):
        n = len(up_side) - len(down_side)
        del up_side[-n - 1:-1]
    if len(up_side) < len(down_side):
        n = len(down_side) - len(up_side)
        del down_side[0:n]
    center_ = []
    for i in range(len(up_side)):
        center_.append(up_side[i] / 2 + down_side[i] / 2)
    return center_


# path_ = r"E:\2022_7_20_sunny\4rad\rad.bip"
# arr_data = tt.readTiffArray(path_)
# dist_arr = arr_data[100, :, :]
#
# up = up_sides(dist_arr)
# down = down_sides(dist_arr)
# center = center_line(dist_arr)

# left = left_sides(dist_arr)
# right = right_sides(dist_arr)
#
# x = np.ones((min(len(left), len(right)), min(len(up), len(down))))
# y = np.ones((min(len(left), len(right)), min(len(up), len(down))))
#
# for i in range(min(len(left), len(right))):
#     up_ = np.transpose(up)
#     x[i] = up_[0]
#     y[i] = up_[1]
#     up = up_sides(arr_data)
#     if len(up) > length0:
#         n = len(up) - length0
#         del up[-n - 1:-1]

import os

import numpy as np
import tiff_tool as tt


# 获取数组非0矩形上边所有pixel的位置
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
    # 判断行列大小，以确定中心线的方向
    row_size = img_data.shape[0]
    col_size = img_data.shape[1]

    # 东西向条带
    if row_size <= col_size:
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
            center_.append((up_side[i] / 2 + down_side[i] / 2).astype(int))

    # 南北向条带
    else:
        left_side = left_sides(img_data)
        right_side = right_sides(img_data)
        if len(left_side) > len(right_side):
            n = len(left_side) - len(right_side)
            del left_side[-n - 1:-1]
        if len(left_side) < len(right_side):
            n = len(right_side) - len(left_side)
            del right_side[0:n]
        center_ = []
        for i in range(len(left_side)):
            center_.append((left_side[i] / 2 + right_side[i] / 2).astype(int))
    return center_


def test(path):
    arr_data = tt.read_tif_array(os.path.join(path, "4rad", "rad.bip"))
    r = arr_data[59, :, :]
    g = arr_data[36, :, :]
    b = arr_data[18, :, :]
    # 将三个数组组合为一个(1000, 1000, 3)的数组
    arr = np.stack((r, g, b), axis=-1)
    # 归一化
    nonzero_idx = arr.nonzero()  # 找到所有非0元素的索引
    min_value = arr[nonzero_idx].min()  # 计算最小的非0值
    max_value = np.max(arr)
    arr = (arr - min_value) / (max_value - min_value)
    arr[arr <= 0] = 1
    arr = np.power(arr, 0.5)

    up = up_sides(r)
    down = down_sides(r)
    left = left_sides(r)
    right = right_sides(r)
    center = center_line(r)

    # plot
    import matplotlib.pyplot as plt
    plt.rc('font', size=13)
    plt.rcParams['xtick.direction'] = 'in'  # 将x周的刻度线方向设置向内
    plt.rcParams['ytick.direction'] = 'in'  # 将y轴的刻度方向设置向内
    fig, ax = plt.subplots(figsize=(8, 5), dpi=300, constrained_layout=1)

    ax.imshow(arr)
    ax.plot([i[1] for i in up], [i[0] for i in up], 'r')
    ax.plot([i[1] for i in down], [i[0] for i in down], 'r')
    ax.plot([i[1] for i in left], [i[0] for i in left], 'r')
    ax.plot([i[1] for i in right], [i[0] for i in right], 'r')
    ax.plot([i[1] for i in center], [i[0] for i in center], 'r')
    ax.axis('off')
    plt.savefig(os.path.join(path, "4rad", "outlines.png"), dpi=300)
    plt.show()


if __name__ == "__main__":
    path_ = r"D:\2022_7_20_sunny"
    test(path_)
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 18 15:37:27 2022

@author: Flemyng
"""

import os
import numpy as np
import tiff_tool as tt
import matplotlib.pyplot as plt


# 寻找n在array中的位置（index）
def xxx(N, array):
    z = np.abs(N - array).tolist()
    a = z.index(min(z))
    return a


# 寻找n在array中的位置（index）
def yyy(N, array):
    f = array-N
    f = f[f > 0]
    sorted_arr = sorted(f)
    # 选择前4个元素
    min_four = sorted_arr[:4]
    g = min_four[2]+N
    return g


# 使用NDVI自动分离植被
def VegeDivision(red, nir, img_data, save_path="plot.png"):
    red_band = (img_data[red - 2] + img_data[red - 1] + img_data[red]) / 3
    nir_band = (img_data[nir - 2] + img_data[nir - 1] + img_data[nir]) / 3
    red_band, nir_band = red_band.astype(np.float64), nir_band.astype(np.float64)
    sub = nir_band - red_band
    add = nir_band + red_band
    ndvi_ = np.divide(sub, add, out=np.zeros_like(sub), where=add != 0)  # 防止除数为零

    bins_num = 500
    arr = ndvi_[ndvi_ > 0]
    y, x = np.histogram(arr, bins=bins_num)
    x = (x[1:] + x[:-1]) / 2

    n = 3  # 数字越大阈值越低
    a1 = np.max(y[int(bins_num / 2):])
    a1_i = np.argwhere(y == a1)
    a2 = np.min(y[int(bins_num / 5):int(bins_num * 4 / 5)])
    a2_i = np.argwhere(y == a2)
    a3 = int((a1 + (n - 1) * a2) / n)
    if a1_i.size > 1:
        for i in range(a1_i.size):
            candy = int(a1_i[i])
            if a2 < candy < a1:
                up_lim = candy
    else:
        up_lim = int(a1_i[0])
    a4 = yyy(a3, y[int(a2_i[0]):up_lim])

    th = x[xxx(a4, y)]  # 计算阈值

    plt.rcParams['xtick.direction'] = 'in'  # 将x周的刻度线方向设置向内
    plt.rcParams['ytick.direction'] = 'in'  # 将y轴的刻度方向设置向内
    plt.rc('font', family='Times New Roman', size=10)
    fig, axe = plt.subplots(2, constrained_layout=1, figsize=(4, 5.5), dpi=300)

    axe[0].plot(x, y)
    axe[0].scatter(th, y[xxx(th, x)], c='r', zorder=5)
    axe[0].set_ylabel('Times')

    # print('\n' + 'NDVI Threshold is ' + str(th))

    ndvi_[ndvi_ >= th] = 1  # 大于等于阈值设为1
    ndvi_[ndvi_ < th] = 0  # 小于阈值设为0

    axe[1].imshow(ndvi_)
    axe[1].set_xlabel('NDVI')
    # plt.savefig(save_path)
    plt.show()
    return ndvi_


# 使用RGB自动分离阴阳叶
def VegeDivision_2(r, g, b, img_data):
    r_band = (img_data[r - 2] + img_data[r - 1] + img_data[r]) / 3
    g_band = (img_data[g - 2] + img_data[g - 1] + img_data[g]) / 3
    b_band = (img_data[b - 2] + img_data[b - 1] + img_data[b]) / 3
    r_band, g_band, b_band = r_band.astype(np.float64), g_band.astype(np.float64), b_band.astype(np.float64)
    cive = -2 * r_band + 4 * g_band - 2 * b_band

    bins_num = 500
    arr = cive[cive > 0]
    y, x = np.histogram(arr, bins=bins_num)
    x = (x[1:] + x[:-1]) / 2

    n = 3  # 数字越大阈值越低
    a1 = np.max(y[int(bins_num / 2):])
    a1_i = np.argwhere(y == a1)
    a2 = np.min(y[int(bins_num / 5):int(bins_num * 4 / 5)])
    a2_i = np.argwhere(y == a2)
    a3 = int((a1 + (n - 1) * a2) / n)
    if a1_i.size > 1:
        for i in range(a1_i.size):
            candy = int(a1_i[i])
            if a2 < candy < a1:
                up_lim = candy
    else:
        up_lim = int(a1_i[0])
    a4 = yyy(a3, y[int(a2_i[0]):up_lim])

    th = x[xxx(a4, y)]  # 计算阈值

    plt.rcParams['xtick.direction'] = 'in'  # 将x周的刻度线方向设置向内
    plt.rcParams['ytick.direction'] = 'in'  # 将y轴的刻度方向设置向内
    plt.rc('font', family='Times New Roman', size=10)
    fig, ax = plt.subplots(2, constrained_layout=1, figsize=(4, 5.5), dpi=300)
    ax[0].plot(x, y)
    ax[0].scatter(th, y[xxx(th, x)], c='r')
    ax[0].set_ylabel('Times')
    # print('\n' + 'rgb Threshold is ' + str(th))

    cive[cive >= th] = 1  # 大于等于阈值设为1
    cive[cive < th] = 0  # 小于阈值设为0

    ax[1].imshow(cive)
    ax[1].set_xlabel('Cive')
    plt.show()

    print('rgb Separating vegetation...')
    return cive


def main(path_):

    vi = ["ndvi", "nirv", "fcvi", "sif", "APAR"]

    dataset, im_data = tt.readTiff(os.path.join(path_, "5ref", "ref.bip"))  # type: ignore # 读取地表反射率文件
    mask = VegeDivision(60, 100, im_data)
    shadow = VegeDivision_2(59, 38, 16, im_data)

    ref = im_data * mask * shadow
    tt.writeTiff(dataset, ref, os.path.join(path_, "5ref", "ref_in_vege.tif"))

    plt.rcParams['xtick.direction'] = 'in'  # 将x周的刻度线方向设置向内
    plt.rcParams['ytick.direction'] = 'in'  # 将y轴的刻度方向设置向内
    plt.rc('font', family='Times New Roman', size=10)
    fig, ax = plt.subplots(constrained_layout=1, figsize=(4, 2.5), dpi=300)
    shape = ref.shape
    rgb = np.zeros([shape[1], shape[2], 3])
    rgb[:, :, 0] = ref[61]
    rgb[:, :, 1] = ref[39]
    rgb[:, :, 2] = ref[17]
    image = np.power(rgb, 0.18)
    ax.imshow(image)
    plt.show()

    for i in vi:
        print('Cutting ' + i + ' ...')
        VI = tt.readTiffArray(os.path.join(path_, "VIs", i+".tif"))
        new_vi = VI * mask * shadow
        tt.writeTiff(dataset, new_vi, os.path.join(path_, "VIs", i+"_in_vege.tif"))


# 主函数
if __name__ == '__main__':
    path = r"E:\2022_8_14_sunny"
    VegeDivision(60, 100, path)

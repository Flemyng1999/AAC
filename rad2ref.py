#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/4/12 23:05
# @Author  : Flemyng
# @File    : rad2ref.py
# @Software: PyCharm
import os
import tiff_tool as tt
import numpy as np
import matplotlib.pyplot as plt


def read_target(txt_path: str) -> np.ndarray:
    li = []
    with open(txt_path, 'r', encoding='utf-8') as f:
        for x, line in enumerate(f):
            if x < 4:
                continue
            if x > 153:
                break
            result = line.split('\t')
            li.append(result[3])
    array = np.array(li, dtype=np.float32)
    return array


def rad2ref(rad: np.ndarray, dir_path: str) -> np.ndarray:
    # [dir_path] is ONLY for target_rad
    target_rad = read_target(os.path.join(dir_path, "4rad", "rad_target.txt"))
    target_ref = np.loadtxt(os.path.join("docs", "resample50178.txt"), dtype=np.float32)

    irr = target_rad / target_ref[:, 1]
    irr_ = irr.reshape((150, 1, 1))
    ref_ = (rad / irr_).astype(np.float32)

    # # plot
    # plt.rc('font', size=13)
    # plt.rcParams['xtick.direction'] = 'in'  # 将x周的刻度线方向设置向内
    # plt.rcParams['ytick.direction'] = 'in'  # 将y轴的刻度方向设置向内
    # fig, ax = plt.subplots(2, figsize=(8, 8), dpi=100, constrained_layout=1)
    #
    # ax[0].plot(target_ref[:, 0], target_rad, label="target_rad")
    # ax[0].plot(target_ref[:, 0], irr, label="irr")
    # ax[1].plot(target_ref[:, 0], target_ref[:, 1], color='k', label="target_ref")
    # ax[1].plot(target_ref[:, 0], ref[:, 555, 1849], color='g', label="canopy_ref")
    #
    # ax[0].legend(loc=0)
    # ax[1].legend(loc=0)
    # plt.show()

    return ref_


def main(dir_path: str, img_show=False) -> np.ndarray:
    # data
    folder_path = os.path.join(dir_path, "4rad")
    # 检查文件夹中是否有rad_corr.tif文件
    if os.path.exists(os.path.join(folder_path, 'rad_corr.tif')):
        # 如果有，则读取rad_corr.tif文件
        file_path = os.path.join(folder_path, 'rad_corr.tif')
        rad, geo, proj = tt.read_tif(file_path)
    else:
        # 如果没有，则读取rad.bip文件
        file_path = os.path.join(folder_path, 'rad.bip')
        rad, geo, proj = tt.read_tif(file_path)

    target_rad = read_target(os.path.join(dir_path, "4rad", "rad_target.txt"))
    target_ref = np.loadtxt(os.path.join("docs", "resample50178.txt"), dtype=np.float32)

    irr = target_rad / target_ref[:, 1]
    irr_ = irr.reshape((150, 1, 1))
    ref_ = (rad / irr_).astype(np.float32)
    tt.write_tif(os.path.join(dir_path, "5ref", "ref.bip"), ref_, geo, proj)

    # plot
    if img_show:
        plt.rc('font', size=13)
        plt.rcParams['xtick.direction'] = 'in'  # 将x周的刻度线方向设置向内
        plt.rcParams['ytick.direction'] = 'in'  # 将y轴的刻度方向设置向内
        fig, ax = plt.subplots(2, figsize=(8, 8), dpi=200, constrained_layout=1)

        ax[0].plot(target_ref[:, 0], target_rad, label="target_rad", solid_capstyle='round')
        ax[0].plot(target_ref[:, 0], irr, label="irr", solid_capstyle='round')
        ax[1].plot(target_ref[:, 0], target_ref[:, 1], color='k', label="target_ref", solid_capstyle='round')
        ax[1].plot(target_ref[:, 0], ref_[:, 555, 1849], color='g', label="canopy_ref", solid_capstyle='round')

        ax[0].legend(loc=0)
        ax[1].legend(loc=0)
        plt.show()
    else:
        plt.close()

    return ref_


if __name__ == '__main__':
    disk1 = 'D:'
    disk2 = 'E:'
    path = ["2022_7_5_sunny"]
    # path = ["2022_7_5_sunny", "2022_7_9_cloudy", "2022_7_12_sunny",
    #         "2022_7_13_cloudy", "2022_7_16_sunny", "2022_7_20_sunny",
    #         "2022_7_23_sunny", "2022_7_27_sunny", "2022_8_2_sunny",
    #         "2022_8_9_cloudy", "2022_8_13_cloudy", "2022_8_14_sunny",
    #         "2022_8_16_sunny", "2022_8_20_sunny", "2022_8_24_cloudy"]

    for i in range(len(path)):
        if i < 9:
            ref = main(os.path.join(disk1, path[i]), True)
        else:
            ref = main(os.path.join(disk2, path[i]))
    # path = r"D:\2022_7_5_sunny"
    # main(path)

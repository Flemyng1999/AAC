import os
import numpy as np

import matplotlib
from matplotlib import colors
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

import VegeDivision as vd
import all_sides as side
import rad2ref
import tiff_tool as tt


def read_target(txt_path):
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


def sif(rad_):
    # 寻找3个波段
    irr = read_target(r"D:\2022_7_13_cloudy\4rad\rad_target.txt")
    list_irr = irr.tolist()  # 转为List
    E_min = min(list_irr[30:100])  # 返回最小值
    s_in = list_irr.index(E_min)  # 返回最小值的索引
    max1, max2 = max(list_irr[s_in - 10:s_in]), max(list_irr[s_in:s_in + 10])
    s_1, s_2 = list_irr.index(max1), list_irr.index(max2)

    L = rad_  # 读取地表上行辐射文件
    R = rad_ / irr.reshape((150, 1, 1))  # 计算下行辐射
    R_in = R[s_in, :, :]
    L_in = L[s_in, :, :]
    R_out1 = R[s_1, :, :]
    R_out2 = R[s_2, :, :]
    a1 = (s_in - s_1) / (s_2 - s_1)  # 差分系数
    a2 = (s_2 - s_in) / (s_2 - s_1)
    F = L_in * (R_in - a2 * R_out1 - a1 * R_out2)
    return F


def new_colormap(colormap, max_=1, min_=0, N=2560):
    map_color = colors.LinearSegmentedColormap.from_list('my_list', colormap)
    # 把背景值设为白色
    my_colors = matplotlib.colormaps.get_cmap(map_color)
    new_colors = my_colors(np.linspace(0, 1, N))
    num = int(N * (0 - min_) / (max_ - min_))
    new_colors[num, :] = np.array([256 / 256, 256 / 256, 256 / 256, 1])
    new_cmp = ListedColormap(new_colors)
    return new_cmp


def main(path_):
    rad = tt.readTiffArray(os.path.join(path_, "4rad", "rad_corr.tif"))
    ref = rad2ref.rad2ref(rad, path_)
    ndvi = vd.VegeDivision(60, 100, ref)
    ref_in_vege = ref * ndvi
    wl = np.loadtxt(r"C:\Users\imFle\OneDrive\resample50178.txt")[:, 0]

    up_index = np.array(side.up_sides(ref[100, :, :])).T
    down_index = np.array(side.down_sides(ref[100, :, :])).T
    center_index = np.array(side.center_line(ref[100, :, :])).T

    center_ref = ref_in_vege[:, center_index[0], center_index[1]]
    line1 = np.nonzero(center_ref[0, :])
    center_ref = np.mean(center_ref[:, line1[0]], axis=1)

    edge_ref = np.hstack((ref_in_vege[:, up_index[0], up_index[1]], ref_in_vege[:, down_index[0], down_index[1]]))
    line2 = np.nonzero(edge_ref[0, :])
    edge_ref = np.mean(edge_ref[:, line2[0]], axis=1)

    flu = sif(rad)

    up = side.up_sides(flu)
    down = side.down_sides(flu)
    left = side.left_sides(flu)
    right = side.right_sides(flu)
    center = side.center_line(flu)

    # plot
    plt.rc('font', size=13)
    plt.rcParams['xtick.direction'] = 'in'  # 将x周的刻度线方向设置向内
    plt.rcParams['ytick.direction'] = 'in'  # 将y轴的刻度方向设置向内
    fig, ax = plt.subplots(2, figsize=(8, 9), dpi=300, constrained_layout=1)

    ax[0].plot(wl, center_ref,
               label="Center reflectance", linewidth=2,
               alpha=0.7, solid_capstyle='round', )
    ax[0].plot(wl, edge_ref,
               label="Edge reflectance", linewidth=2,
               alpha=0.7, solid_capstyle='round', )
    ax[0].set_title("Center and edge reflectance of canopy")
    ax[0].set_xlabel('Wavelength(nm)')
    ax[0].set_ylabel('Reflectance')
    ax[0].legend(loc=0)

    min_, max_ = np.min(flu), np.max(flu)
    new_cmp = new_colormap(['white', '#f6f6f6', '#ececec',
                            '#e2e2e2', '#d8d8d8', '#cecece', '#b9bf45',
                            '#64a83d', '#167f39', '#044c29', '#00261c',
                            'k', 'k', 'k', 'k', 'k'], max_, min_)

    im = ax[1].imshow(flu, cmap=new_cmp)
    fig.colorbar(im,
                 label="SIF",
                 ticks=list(np.linspace(min_, max_, 5))
                 )
    ax[1].plot([i[1] for i in up], [i[0] for i in up], 'r', solid_capstyle='round')
    ax[1].plot([i[1] for i in down], [i[0] for i in down], 'r', solid_capstyle='round')
    ax[1].plot([i[1] for i in left], [i[0] for i in left], 'r', solid_capstyle='round')
    ax[1].plot([i[1] for i in right], [i[0] for i in right], 'r', solid_capstyle='round')
    ax[1].plot([i[1] for i in center], [i[0] for i in center], 'r', solid_capstyle='round')
    ax[1].set_title("SIF of canopy")
    ax[1].axis('off')

    plt.savefig(os.path.join(path_, "5ref", "center_edge.png"), dpi=300)
    plt.show()


if __name__ == "__main__":
    # 读取图像
    path = r"D:\2022_7_5_sunny"
    main(path)


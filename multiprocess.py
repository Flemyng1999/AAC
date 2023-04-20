import os
import math
from tqdm import tqdm
import VegeDivision as vd
import numpy as np
import tiff_tool as tt
import all_pixels as ap
import curve_fitting as cf
import rad2ref
import center_edge_ref as cer
from multiprocessing import Pool


def baseline(part_, bands_):
    # print('Generating baseline...')
    all_baseline = part_[bands_]
    baseline_ = np.mean(all_baseline, axis=0)  # 计算所有bands上的平均值
    return baseline_


# 用于计算系数使用的distance
def distance(arr, height=80, view_angle=17.6):
    index__, dist_ = ap.pixel_info(arr)
    long = height * math.tan(view_angle * math.pi / 360)
    dist_ = long * dist_ / max(dist_)  # 将地面上的像素距离转化为真实长度
    index__[:, 2] = pow(height ** 2 + dist_ * dist_, 0.5) - height + 1e-6  # 勾股定理将地面距离转化为物体到传感器距离
    # 将实际距离放入二维矩阵
    shape = np.shape(arr)

    distance_ = np.zeros((shape[0], shape[1]))
    rows = list(np.array(index__[:, 0], dtype=int))
    cols = list(np.array(index__[:, 1], dtype=int))
    distance_[rows, cols] = index__[:, 2]

    return index__, distance_


def beta_coe(o2a, bl, ndvi, save_path):
    # print('Calculating β')
    o2a_ = o2a * ndvi
    baseline_ = bl * ndvi
    index_, d = distance(o2a_)
    rows = list(np.array(index_[:, 0], dtype=int))
    cols = list(np.array(index_[:, 1], dtype=int))
    shape_part_ = np.shape(o2a_)

    # 计算o2a与周围波段平均辐射的比值α
    alpha = np.zeros(shape_part_)
    alpha[rows, cols] = o2a_[rows, cols] / baseline_[rows, cols]

    # 这是α的多项式拟合值α_
    y = alpha[alpha > 0]
    x = d[d > 0]
    p = cf.fitting(x, y, 5, save_path, 'Δ Distance (m)', 'α')  # 计算拟合函数系数并绘制曲线和散点

    alpha_ = (p[5] * np.power(d, 5) + p[4] * np.power(d, 4) + p[3] * np.power(d, 3) + p[2] * np.power(d, 2)
              + p[1] * d + p[0])

    # 计算纠正系数β
    shape = np.shape(o2a_)
    beta_ = np.zeros((shape[0], shape[1]))
    rows = list(np.array(index_[:, 0], dtype=int))
    cols = list(np.array(index_[:, 1], dtype=int))
    beta_[rows, cols] = p[0] / alpha_[rows, cols]

    return beta_, index_


def correct(o2a_, baseline_, ndvi, save_path):
    # print('Correcting Radiance in the {}th Wavelength'.format(wavelength_))
    beta, index = beta_coe(o2a_, baseline_, ndvi, save_path)
    rows = list(np.array(index[:, 0], dtype=int))
    cols = list(np.array(index[:, 1], dtype=int))
    # 对O2-A的吸收做矫正
    o2a_[rows, cols] = o2a_[rows, cols] * beta[rows, cols]
    # print('Correction is DONE')
    return o2a_


def process_array_set(args):
    """
    Processes a set of three numpy arrays using the add_arrays function.

    Args:
    args: a tuple containing three numpy arrays of shape (1000, 1000) and a string argument

    Returns:
    A string representing the element-wise sum of the input arrays, with the string argument concatenated to it.
    """
    arr1, arr2, arr3, string_arg = args
    result = correct(arr1, arr2, arr3, string_arg)
    return result


def main(path_, arr_wl, baseline_wl):
    rad, geo, proj = tt.read_tif(os.path.join(path_, '4rad', 'rad.bip'))  # type: ignore
    ref = rad2ref.rad2ref(rad, path_)
    ndvi = vd.VegeDivision(60, 100, ref)
    del ref  # 释放变量ref占用的内存

    # create sets of numpy arrays to process
    array_sets = []
    arr3 = ndvi
    for i_ in range(len(arr_wl)):
        arr1 = rad[arr_wl[i_]]
        arr2 = baseline(rad, baseline_wl[i_])
        string_arg = os.path.join(path_, '4rad', 'α_{}.png'.format(arr_wl[i_]))
        array_sets.append((arr1, arr2, arr3, string_arg))

    # create a multiprocessing pool with number of processes equal to the number of CPU cores
    pool = Pool(os.cpu_count()-1)

    # process each array set in parallel using the pool.map function
    results = pool.map(process_array_set, array_sets)

    # replace the results for each set of arrays to [rad] in the original array
    for j, result in enumerate(results):
        rad[arr_wl[j]] = result

    pool.close()
    pool.join()

    tt.write_tif(os.path.join(path_, '4rad', 'rad_corr.tif'), rad, geo, proj)  # type: ignore


def test(path_):
    # 计算ref
    ref = rad2ref.main(path_)
    # 计算VegeDivision
    ndvi = vd.VegeDivision(60, 100, ref)
    ref_in_vege = ref * ndvi
    np.save(os.path.join(path_, "5ref", "ref_in_vege"), ref_in_vege)

    # 展示中心于边缘的ref
    cer.main(path_)


if __name__ == '__main__':

    wavelength = [0,
                  77, 78,
                  87, 88, 89,
                  90,
                  119, 120, 121,
                  128, 129, 130,
                  136, 137,
                  126, 127]  # 校正波段
    bands = [[2, 3],
             [74, 81, 82, 83], [74, 81, 82, 83],
             [84, 85, 90, 91], [84, 85, 90, 91], [84, 85, 90, 91],
             [81, 82, 83, 91, 92, 93, 94],
             [114, 115, 116, 117, 122, 123], [114, 115, 116, 117, 122, 123], [114, 115, 116, 117, 122, 123],
             [122, 123, 132, 133, 134], [122, 123, 132, 133, 134], [122, 123, 132, 133, 134],
             [132, 133, 134, 138, 139, 140, 141], [132, 133, 134, 138, 139, 140, 141],
             [114, 115, 116, 117, 139, 140, 141, 142], [114, 115, 116, 117, 139, 140, 141, 142]]  # 作为基线的参考波段

    disk1 = 'D:'
    disk2 = 'E:'
    path = ["2022_7_5_sunny"]
    # path = ["2022_7_5_sunny", "2022_7_9_cloudy", "2022_7_12_sunny",
    #         "2022_7_13_cloudy", "2022_7_16_sunny", "2022_7_20_sunny",
    #         "2022_7_23_sunny", "2022_7_27_sunny", "2022_8_2_sunny",
    #         "2022_8_9_cloudy", "2022_8_13_cloudy", "2022_8_14_sunny",
    #         "2022_8_16_sunny", "2022_8_20_sunny", "2022_8_24_cloudy"]

    for i in tqdm(range(len(path))):
        if i < 9:
            main(os.path.join(disk1, path[i]), wavelength, bands)
        else:
            main(os.path.join(disk2, path[i]), wavelength, bands)
    print("\n_________Test Begin_________\n")
    for i in tqdm(range(len(path))):
        if i < 9:
            test(os.path.join(disk1, path[i]))
        else:
            test(os.path.join(disk2, path[i]))
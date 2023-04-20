import os
import numpy as np
import tiff_tool as tt
import matplotlib.pyplot as plt


def get_name(path, trait='.tif'):
    # Get roi names
    files = os.listdir(path)  # 得到文件夹下的所有文件名称
    ls = []
    for i in files:
        if trait in i:
            name = os.path.join(path, i)
            ls.append(name)
    return ls


def main(dir_path):
    # path
    roi_path = os.path.join(dir_path, "ROI")

    # data
    roi_name = get_name(roi_path, ".npy")
    if len(roi_name) != 20:
        roi_name_ = get_name(roi_path, ".tif")
        for i_ in roi_name_:
            tif = tt.read_tif(i_)
            np.save(i_.replace(".tif", ""), tif)

        roi_path = os.path.join(dir_path, "ROI")
        roi_name = get_name(roi_path, ".npy")

    vege_ = np.zeros((150, 20))
    arr = np.load(os.path.join(dir_path, "5ref", "ref_in_vege.npy"), allow_pickle=True)

    for j in range(20):
        roi = np.load(roi_name[j])
        ws = roi * arr
        pos = np.nonzero(ws[2])
        ws_ = arr[:, pos[0], pos[1]]
        vege_[:, j] = np.mean(ws_, axis=1)

    # plot
    plt.rc('font', family='Times New Roman', size=12)
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300, constrained_layout=1)
    x = np.linspace(1, 150, 150)*4+400
    name = ['w1s1', 'w1s2', 'w1s3', 'w1s4', 'w1s5',
            'w2s1', 'w2s2', 'w2s3', 'w2s4', 'w2s5',
            'w3s1', 'w3s2', 'w3s3', 'w3s4', 'w3s5',
            'w4s1', 'w4s2', 'w4s3', 'w4s4', 'w4s5']
    my_cmap = plt.get_cmap('rainbow', len(name))  # 设置colormap，数字为颜色数量

    for i in range(20):
        ax.plot(x, vege_[:, i], label=name[i], color=my_cmap(i), alpha=0.5, solid_capstyle='round', )

    ax.legend(loc=0)
    plt.ylabel("Reflectance")
    plt.xlabel("Wavelength(nm)")
    plt.title(dir_path.replace("D://2022_", "").replace("E://2022_", ""))
    plt.savefig(os.path.join(dir_path, "5ref", "ref_in_vege"))
    plt.show()

    return vege_


if __name__ == "__main__":
    disk1 = r'D:'
    disk2 = r'E:'
    path = ["2022_7_16_sunny"]
    for i in range(len(path)):
        if i < 9:
            main(os.path.join(disk1, path[i]))
        else:
            main(os.path.join(disk2, path[i]))
import numpy as np
from matplotlib.offsetbox import AnchoredText
import matplotlib.pyplot as plt


# function to convert to superscript
def get_super(x):
    normal = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-=()"
    super_s = "ᴬᴮᶜᴰᴱᶠᴳᴴᴵᴶᴷᴸᴹᴺᴼᴾQᴿˢᵀᵁⱽᵂˣʸᶻᵃᵇᶜᵈᵉᶠᵍʰᶦʲᵏˡᵐⁿᵒᵖ۹ʳˢᵗᵘᵛʷˣʸᶻ⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾"
    res = x.maketrans(''.join(normal), ''.join(super_s))
    return x.translate(res)


def curve(x, y, p, save_path, x_name=None, y_name=None):
    parameter = p.c  # 拟合deg次多项式
    aa = ''  # 方程拼接  ——————————————————
    for i in range(p.o + 1):
        bb = round(parameter[i], 3)
        if bb > 0:
            if i == 0:
                bb = str(bb)
            else:
                bb = ' + ' + str(bb)
        else:
            bb = ' - ' + str(np.absolute(bb))
        if i == p.o:
            aa = aa + bb
        elif i == p.o-1:
            aa = aa + bb + 'x'
        else:
            aa = aa + bb + 'x' + get_super(str(p.o - i))
        # 方程拼接  ——————————————————

    # Plot
    plt.rcParams['xtick.direction'] = 'in'  # 将x周的刻度线方向设置向内
    plt.rcParams['ytick.direction'] = 'in'  # 将y轴的刻度方向设置向内
    plt.rc('font', family='Times New Roman', size=13)
    fig, ax = plt.subplots(constrained_layout=1, figsize=(8, 4), dpi=300)
    # 设置坐标轴名称
    plt.xlabel(x_name)
    plt.ylabel(y_name)
    plt.scatter(x, y, s=1, alpha=0.003)  # 原始数据散点图
    min_, max_ = np.min(x), np.max(x)
    x_ = np.linspace(min_, max_, 200)
    plt.plot(x_, p(x_), color='orangered', linewidth=1.5, solid_capstyle='round')  # 画拟合曲线
    plt.tick_params(which='both', direction='in')  # 设置刻度
    # plt.tick_params(which='major', width=line_pixel)  # 单独设置主刻度
    plt.minorticks_on()  # 开启次刻度

    # 绘制方程式与相关性系数
    at = AnchoredText('y = ' + aa + '\n' + 'R' + get_super('2') + ' = ' + str(round(np.corrcoef(y, p(x))[0, 1] ** 2, 3)),
                      frameon=0, loc='upper right')
    at.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
    ax.add_artist(at)

    plt.savefig(save_path)
    # plt.show()
    # print('The equation of the curve is:\n', p)
    # print('R^2 = ', round(np.corrcoef(y, p(x))[0, 1] ** 2, 4))


def fitting(x, y, deg, save_path, x_name=None, y_name=None):
    parameter = np.polyfit(x, y, deg)  # 拟合deg次多项式
    p = np.poly1d(parameter)  # 拟合deg次多项式
    curve(x, y, p, save_path, x_name, y_name)
    return p


if __name__ == '__main__':
    x = np.linspace(0, 10, 5000)
    y = 0.765237 * x ** 2 + 1.2 * x + 0.78 + np.random.normal(0, 20, 5000)
    p = fitting(x, y, 2, r'G:')

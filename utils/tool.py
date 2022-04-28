import numpy as np


def distance(p1, p2):
    """
    p1到p2两个点的距离
    :param p1:点1
    :param p2:点2
    :return: 距离:float
    """
    return np.sqrt((p1[0] - p2[0]) * (p1[0] - p2[0]) + (p1[1] - p2[1]) * (p1[1] - p2[1]))

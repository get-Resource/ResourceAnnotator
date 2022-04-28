import cv2
import numpy as np

from utils.tool import distance


class region_shape:
    """
    实现区域的计算：

    """
    nst_thresh = 12  # 小于此距离时，自动黏合
    cbox_rect_min_size = (10, 10)  # 创建矩形box的最小尺寸，小于该尺寸则不存储
    cbox_polygan_min_area = 400  # 创建多边形box的最小外接圆面积

    def __init__(self):
        pass

    def get_box_index(self, p, boxes):
        """
        获取距离 p 点所在的box index
        :param p, 目标点
        :param boxes, 图片中所有的boxes
        :return: boxes中的索引号
        """
        for i, box in enumerate(boxes):
            if cv2.pointPolygonTest(box, (p[0], p[1]), False) > 0:
                return i
        return -1

    def get_nearest_point_index(self, p, box):
        """
        获取 box 中距离 p 点最近的点的位置
        :param p, 目标点
        :param box, 图片中所有的boxe
        :return: box中的索引号
        """
        index = np.Inf
        nst_value = np.Inf
        for point_index, point in enumerate(box):
            dst = distance(point, [p[0], p[1]])
            if dst < nst_value and dst < self.nst_thresh:
                nst_value = dst
                index = point_index
        return index

    def is_too_small(self, boxes):
        """
        形状是否太小，太小就返回True
        :param boxes:
        :return: bool
        """
        shape_ = False
        center, radius = cv2.minEnclosingCircle(boxes)
        if np.pi * radius * radius > self.cbox_polygan_min_area:
            shape_ = True
        return shape_

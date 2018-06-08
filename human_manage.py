# coding=utf-8

import cv2

from human import Human
from tool import center, distance

min_contour_area = 500
threshold_distance = 150


class HumanManager():
    """human class

    每一个 human 包含一个 ROI, 一个 ID and 一个 Kalman filter
    """

    def __init__(self):
        self.humans = {}

    def is_new_object(self, contour):
        """判断是否为最新 object[human]"""
        (x, y, w, h) = cv2.boundingRect(contour)
        _center = center([[x, y], [x + w, y], [x, y + h], [x + w, y + h]])

        # 遍历计算中心店距离
        distances = []
        for _id, human in self.humans.items():
            p = (_id, distance(human.predictCenter, _center))
            distances.append(p)

        # 排序
        sorted(distances, key=lambda d: d[1])

        # 筛选 < threshold_distance
        filter(lambda d: d[1] < threshold_distance, distances)

        if len(distances) > 0:
            _id = distances[0][0]
            match_human = self.humans[_id]
            _distance = distances[0][1]

            # 更新
            match_human.kalman.correct(_center)
            return False, match_human, _distance

        return True, None, -1

    def get_next_id(self):
        """获取一个 human id"""
        return len(self.humans) + 1

    def add_human(self, frame, contour):
        """尝试添加 human"""
        if cv2.contourArea(contour) < min_contour_area:
            return

        # 判断是否是新的 human
        is_true, _ = self.is_new_object(contour)
        if is_true:
            # 添加新的 human
            (x, y, w, h) = cv2.boundingRect(contour)
            human = Human(self.get_next_id(), frame, (x, y, w, h))
            self.humans[human.id] = human

    def update(self, frame):
        """更新当前 frame"""
        for _id, human in self.humans.items():
            human.update(frame)

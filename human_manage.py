# coding=utf-8

import cv2

from config import threshold_distance
from human import Human
from tool import center, distance


class HumanManager():
    """human class

    每一个 human 包含一个 ROI, 一个 ID and 一个 Kalman filter
    """

    def __init__(self):
        self.num = 0
        self.humans = {}

    def is_new_object(self, contour):
        """判断是否为最新 object[human]"""
        (x, y, w, h) = cv2.boundingRect(contour)
        _center = center([[x, y], [x + w, y], [x, y + h], [x + w, y + h]])

        # 遍历计算中心店距离
        distances = []
        for _id, human in self.humans.items():
            _distance = distance(human.center, _center)
            p = (_id, _distance)
            distances.append(p)

        # 排序
        sorted(distances, key=lambda d: d[1])

        # 筛选 < threshold_distance
        distances = [elem for elem in distances if elem[1] < threshold_distance]

        if len(distances) > 0:
            _id = distances[0][0]
            match_human = self.humans[_id]
            _distance = distances[0][1]

            # 更新
            match_human.kalman.correct(_center)

            print("一共有 %d 符合的对象，match 对象id: %d" % (len(distances), _id))
            return False, match_human, _distance

        print("检测到新的对象")
        return True, None, -1

    def get_next_id(self):
        """获取一个 human id"""
        self.num += 1
        return self.num

    def add_human(self, frame, contour):
        """尝试添加 human"""
        # 判断是否是新的 human
        is_true, _, _ = self.is_new_object(contour)
        if is_true:
            # 添加新的 human
            (x, y, w, h) = cv2.boundingRect(contour)
            human = Human(self.get_next_id(), frame, (x, y, w, h))
            self.humans[human.id] = human

    def update(self, frame):
        """更新当前 frame"""
        for _id, human in self.humans.items():
            human.update(frame)

        # 删除静止的物体或者错误的物体
        _del_ids = []
        for _id, human in self.humans.items():
            l = len(human.centers)
            if l > 5:
                # 前后帧错误
                if distance(human.centers[l - 5], human.centers[l - 1]) < 15:
                    _del_ids.append(_id)

        for _id in _del_ids:
            del self.humans[_id]
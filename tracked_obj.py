# coding=utf-8

from typing import List

from config import threshold_distance
from detected_obj import DetectedObject
from tool import distance


class TrackedObject():
    """已经被跟踪的物体"""

    def __init__(self, detected_obj: DetectedObject):
        """构造函数
        :parameter detected_obj DetectedObject
        """
        self._current_center = None
        self._centers = []
        self._current_track_window = None
        self._is_update = False
        self._mark_in = False
        self._track_failed_num = 0  # 跟踪失败的次数
        self._current_detect_object = None  # Type: DetectedObject
        self._last_detect_object = None  # Type: DetectedObject
        # 进行第一次更新
        self.update(detected_obj)

    def mark_un_update(self) -> None:
        """更新前，标注为未更新"""
        self._is_update = False

    def mark_track_fail(self) -> None:
        self._track_failed_num += 1

    def is_update(self) -> bool:
        """是否更新"""
        return self._is_update

    def update(self, detected_obj: DetectedObject) -> None:
        """根据 detected_obj 更新数据
        :parameter detected_obj DetectedObject
        """
        self._track_failed_num = 0  # 置零
        self._is_update = True
        self._last_detect_object = self._current_detect_object
        self._current_detect_object = detected_obj
        self._current_track_window = detected_obj.get_track_window()
        self._current_center = detected_obj.get_center()
        self._centers.append(self._current_center)

        # 标记为进入
        if self._last_detect_object is not None:
            if detected_obj.is_far_door() & self._last_detect_object.is_near_door():
                self._mark_in = True

    def is_mark_in(self) -> bool:
        """判断是否进入门店"""
        return self._mark_in

    def distance_to(self, p) -> float:
        """计算质心和 p 的距离
        :parameter p [x, y]
        :return distance
        """
        return distance(self._current_center, p)

    def has_probable_tracked_zoom(self, objs: List[DetectedObject]) -> (bool, List[DetectedObject]):
        """可能的区域，遍历 contours 进行
        :param objs detected objects
        :return bool, List[DetectedObject]
        """
        filter_objs = [(obj, obj.distance_to(self._current_center)) for obj in objs if
                       obj.distance_to(self._current_center) < threshold_distance]

        if len(filter_objs) == 0:
            return False, []

        # 依据距离，从小到大排序
        filter_objs = sorted(filter_objs, key=lambda d: d[1])
        return True, filter_objs

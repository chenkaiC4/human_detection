# coding=utf-8

from tool import center, distance


class DetectedObject:
    """已经被跟踪的物体"""

    def __init__(self, track_window):
        """构造函数
        :parameter track_window (x, y, w, h)
        """
        self._center = None
        self._track_window = None
        self._mark_matched = False
        self._in_zoom_near_door = False  # 在进门区域
        self._in_zoom_far_door = False  # 在远离门的区域

        # 初始化
        self._update(track_window)

    def _update(self, track_window) -> None:
        """根据 contour 更新数据
        :parameter track_window (x, y, w, h)
        """
        (x, y, w, h) = track_window
        self._center = center([[x, y], [x + w, y], [x, y + h], [x + w, y + h]])
        self._track_window = track_window
        # TODO 360 这个数应该是在第一帧时，画上去，或者根据屏幕大小自动设置
        if x > 360:
            self._in_zoom_far_door = True
        else:
            self._in_zoom_near_door = True

    def is_near_door(self) -> bool:
        """是否在靠门区域"""
        return self._in_zoom_near_door

    def is_far_door(self) -> bool:
        """是否在远门区域"""
        return self._in_zoom_far_door

    def distance_to(self, p) -> float:
        """计算质心和 p 的距离
        :parameter p [x, y]
        """
        return distance(self._center, p)

    def get_track_window(self) -> list:
        """获取方形外围
        :return [x, y, w, h]
        """
        return self._track_window

    def get_center(self) -> list:
        """获取方形外围
        :return [x, y]
        """
        return self._center

    def mark_matched(self) -> None:
        """标记为绑定
        """
        self._mark_matched = True

    def is_matched(self) -> bool:
        """是否被找到 match obj"""
        return self._mark_matched

# coding=utf-8

from typing import List

from detected_obj import DetectedObject
from tracked_obj import TrackedObject


class Manager:
    """Manager class"""

    def __init__(self):
        self.num = 0
        self.humans = []  # type: List[TrackedObject]

    def get_num(self) -> int:
        """获取进入门店的人数"""
        return self.num

    def process_detect_objs(self, objs: List[DetectedObject]):
        """读入一帧中检测到的数据"""

        # TODO 先对上一帧标记的 human 进行删除，比如，已经进入的删除

        for human in self.humans:
            human.mark_un_update()  # 标记为未跟踪
            has, detect_objects = human.has_probable_tracked_zoom(objs)
            if has:
                human.update(detect_objects[0][0])  # 跟新时，会标记为已跟踪
                detect_objects[0][0].mark_matched()  # 标记被绑定的 detect_object

        # 筛选出跟踪成功的物体
        track_success_humans = [human for human in self.humans if human.is_update() is True]
        for human in track_success_humans:
            # 判断进店动作
            is_in = human.is_mark_in()
            if is_in is True:
                self.num += 1
                print("进入一个人，当前一共 %d" % self.num)

        # 筛选出未被跟踪的物体
        track_fail_humans = [human for human in self.humans if human.is_update() is False]
        # TODO 处理这些跟踪失败的 human
        for human in track_fail_humans:
            human.mark_track_fail()

        # 筛选出未被加入任何跟踪物体的 detect_object
        # TODO 逻辑 创建 TrackedObject，或者 丢弃
        un_tracked_object = [obj for obj in objs if obj.is_matched() is False]

        for obj in un_tracked_object:
            self.humans.append(TrackedObject(obj))

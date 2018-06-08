# coding=utf-8
import cv2
import numpy as np

from tool import center

font = cv2.FONT_HERSHEY_SIMPLEX


class Human():
    """human class

    每一个 human 包含一个 ROI, 一个 ID and 一个 Kalman filter
    """

    def __init__(self, id, frame, track_window):
        """使用 track_window 初始化 human"""

        # 设置 id
        self.id = int(id)

        # 设置跟踪区域
        self.track_window = track_window

        # 设置中心点
        self.center = None
        self.predictCenter = None  # 卡尔曼预测的中心点

        # 设置起始 检查点 和 预测点
        self.measurement = np.array((2, 1), np.float32)
        self.prediction = np.zeros((2, 1), np.float32)

        # 设置 roi
        x, y, w, h = track_window
        self.roi = cv2.cvtColor(frame[y:y + h, x:x + w], cv2.COLOR_BGR2HSV)

        # 计算 roi 的 hist 直方图，并归一化
        roi_hist = cv2.calcHist([self.roi], [0], None, [16], [0, 180])
        self.roi_hist = cv2.normalize(roi_hist, roi_hist, 0, 255, cv2.NORM_MINMAX)

        # 设置 kalman 滤波器
        self.kalman = cv2.KalmanFilter(4, 2)
        self.kalman.measurementMatrix = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], np.float32)
        self.kalman.transitionMatrix = np.array([[1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0], [0, 0, 0, 1]], np.float32)
        self.kalman.processNoiseCov = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
                                               np.float32) * 0.03
        self.term_crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)

        # 执行第一次 update
        self.update(frame)

    def __del__(self):
        print("人物 %d 被清除" % self.id)

    def update(self, frame):
        print("人物 %d 进行 update" % self.id)

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        back_project = cv2.calcBackProject([hsv], [0], self.roi_hist, [0, 180], 1)

        # 以下两个 if 中的代码主要用于跟踪物体，计算当前 center
        # 采用 CamShift
        ret, self.track_window = cv2.CamShift(back_project, self.track_window, self.term_crit)
        pts = cv2.boxPoints(ret)
        pts = np.int0(pts)
        self.center = center(pts)
        cv2.polylines(frame, [pts], True, 255, 1)

        # if args.get("algorithm") == "c":
        #     ret, self.track_window = cv2.CamShift(back_project, self.track_window, self.term_crit)
        #     pts = cv2.boxPoints(ret)
        #     pts = np.int0(pts)
        #     self.center = center(pts)
        #     cv2.polylines(frame, [pts], True, 255, 1)
        #
        # # 采用 meanShift
        # if not args.get("algorithm") or args.get("algorithm") == "m":
        #     ret, self.track_window = cv2.meanShift(back_project, self.track_window, self.term_crit)
        #     x, y, w, h = self.track_window
        #     self.center = center([[x, y], [x + w, y], [x, y + h], [x + w, y + h]])
        #     cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 0), 2)

        # 将计算好的中心点喂给卡尔曼滤波器，并预测下一个中心点
        self.kalman.correct(self.center)
        prediction = self.kalman.predict()
        self.predictCenter = prediction

        # 绘制预测的 center
        cv2.circle(frame, (int(prediction[0]), int(prediction[1])), 4, (255, 0, 0), -1)

        # fake shadow
        cv2.putText(frame, "ID: %d -> %s" % (self.id, self.center), (11, (self.id + 1) * 25 + 1),
                    font, 0.6,
                    (0, 0, 0),
                    1,
                    cv2.LINE_AA)
        # actual info
        cv2.putText(frame, "ID: %d -> %s" % (self.id, self.center), (10, (self.id + 1) * 25),
                    font, 0.6,
                    (0, 255, 0),
                    1,
                    cv2.LINE_AA)

# coding=utf-8

"""Tracking Pedestrians in Camera Feed

The application opens a video (could be a camera or a video file)
and tracks pedestrians in the video.
"""

import argparse
import os.path as path

import cv2

from config import background_frame
from human_manage import HumanManager

parser = argparse.ArgumentParser()
parser.add_argument("-a", "--algorithm",
                    help="m (or nothing) for meanShift and c for camshift")
args = vars(parser.parse_args())


def main():
    # camera = cv2.VideoCapture(path.join(path.dirname(__file__), "traffic.flv"))
    camera = cv2.VideoCapture(path.join(path.dirname(__file__), "human.avi"))
    # camera = cv2.VideoCapture(path.join(path.dirname(__file__), "..", "movie.mpg"))
    # camera = cv2.VideoCapture(0)
    # KNN background subtractor
    bs = cv2.createBackgroundSubtractorKNN()

    # MOG subtractor
    # bs = cv2.bgsegm.createBackgroundSubtractorMOG(history = history)
    # bs.setHistory(history)

    # GMG
    # bs = cv2.bgsegm.createBackgroundSubtractorGMG(initializationFrames = history)

    cv2.namedWindow("surveillance")
    human_manager = HumanManager()
    frames = 0
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))
    while True:
        print(" -------------------- FRAME %d --------------------" % frames)
        grabbed, frame = camera.read()
        if (grabbed is False):
            print("failed to grab frame.")
            break

        fgmask = bs.apply(frame)

        # this is just to let the background subtractor build a bit of history
        if frames < background_frame:
            frames += 1
            continue

        th = cv2.threshold(fgmask.copy(), 127, 255, cv2.THRESH_BINARY)[1]
        th = cv2.erode(th, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)), iterations=2)
        dilated = cv2.dilate(th, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (8, 3)), iterations=2)
        image, contours, hier = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for c in contours:
            (x, y, w, h) = cv2.boundingRect(c)
            # 绘制检测到的 contour，绿色
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 1)

            human_manager.add_human(frame, c)

        human_manager.update(frame)

        frames += 1

        cv2.imshow("surveillance", frame)
        out.write(frame)
        if cv2.waitKey(110) & 0xff == 27:
            break
    out.release()
    camera.release()


if __name__ == "__main__":
    main()

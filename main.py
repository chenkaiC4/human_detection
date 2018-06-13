# coding=utf-8

"""Tracking Pedestrians in Camera Feed

The application opens a video (could be a camera or a video file)
and tracks pedestrians in the video.
"""

from os import path

import cv2

from config import background_frame, min_contour_area
from detected_obj import DetectedObject
from manage import Manager
from tool import is_inside


def draw_person(image, person):
    x, y, w, h = cv2.boundingRect(person)
    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 255), 2)


def main():
    camera = cv2.VideoCapture(path.join(path.dirname(__file__), "samples/traffic.flv"))
    # camera = cv2.VideoCapture(path.join(path.dirname(__file__), "samples/human.avi"))
    # camera = cv2.VideoCapture(0)
    # KNN background subtractor
    bs = cv2.createBackgroundSubtractorKNN()

    # MOG subtractor
    # bs = cv2.bgsegm.createBackgroundSubtractorMOG(history = background_frame)
    # bs.setHistory(history)

    # GMG
    # bs = cv2.bgsegm.createBackgroundSubtractorGMG(initializationFrames = history)

    cv2.namedWindow("视窗")
    human_manager = Manager()
    frames = 0

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
        image, contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 遍历两遍，过滤内置小框
        found_filtered = []
        for ridx, o in enumerate(contours):
            for qidx, i in enumerate(contours):
                # i 在 o 内
                if ridx != qidx and is_inside(cv2.boundingRect(o), cv2.boundingRect(i)):
                    break
                else:
                    found_filtered.append(i)

        detected_objects = []
        for contour in found_filtered:
            if cv2.contourArea(contour) > min_contour_area:
                draw_person(frame, contour)
                track_window = cv2.boundingRect(contour)
                detected_objects.append(DetectedObject(track_window))

        human_manager.process_detect_objs(detected_objects)

        frames += 1

        cv2.imshow("surveillance", frame)
        if cv2.waitKey(110) & 0xff == 27:
            break
    camera.release()


if __name__ == "__main__":
    main()

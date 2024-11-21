import cv2
from cv2 import aruco
from cv2.typing import MatLike
from enum import Enum
from pathlib import Path
from loguru import logger
from itertools import chain

from matplotlib.pyplot import stem


class ArucoDictionary(Enum):
    Dict_4X4_50 = aruco.DICT_4X4_50
    Dict_4X4_100 = aruco.DICT_4X4_100
    Dict_4X4_250 = aruco.DICT_4X4_250
    Dict_4X4_1000 = aruco.DICT_4X4_1000
    Dict_5X5_50 = aruco.DICT_5X5_50
    Dict_5X5_100 = aruco.DICT_5X5_100
    Dict_5X5_250 = aruco.DICT_5X5_250
    Dict_5X5_1000 = aruco.DICT_5X5_1000
    Dict_6X6_50 = aruco.DICT_6X6_50
    Dict_6X6_100 = aruco.DICT_6X6_100
    Dict_6X6_250 = aruco.DICT_6X6_250
    Dict_6X6_1000 = aruco.DICT_6X6_1000
    Dict_7X7_50 = aruco.DICT_7X7_50
    Dict_7X7_100 = aruco.DICT_7X7_100
    Dict_7X7_250 = aruco.DICT_7X7_250
    Dict_7X7_1000 = aruco.DICT_7X7_1000
    Dict_APRILTAG_16h5 = aruco.DICT_APRILTAG_16h5
    Dict_APRILTAG_25h9 = aruco.DICT_APRILTAG_25h9
    Dict_APRILTAG_36h10 = aruco.DICT_APRILTAG_36h10
    Dict_APRILTAG_36h11 = aruco.DICT_APRILTAG_36h11
    Dict_ArUco_ORIGINAL = aruco.DICT_ARUCO_ORIGINAL


IMAGE_FOLDER = Path("xx")
OUTPUT_FOLDER = Path("output")
DICTIONARY = ArucoDictionary.Dict_4X4_50

def main():
    OUTPUT_FOLDER.mkdir(exist_ok=True)
    images = chain(IMAGE_FOLDER.glob("*.jpeg"), IMAGE_FOLDER.glob("*.png"), IMAGE_FOLDER.glob("*.jpg"))
    for img_path in images:
        img = cv2.imread(str(img_path))
        # 10x7
        # minus 1 when dealing with normal chessboard
        border_num_x = 10
        border_num_y = 7
        # 115mm square
        # 90mm marker
        # https://docs.opencv.org/3.4/df/d4a/tutorial_charuco_detection.html
        # https://docs.opencv.org/4.x/df/d4a/tutorial_charuco_detection.html
        # https://docs.opencv.org/4.x/da/d13/tutorial_aruco_calibration.html
        # https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html

        # https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html#ga93efa9b0aa890de240ca32b11253dd4a
        # https://github.com/opencv/opencv/issues/22083
        # OpenCV 4.10.x
        dictionary = aruco.getPredefinedDictionary(DICTIONARY.value)
        board = aruco.CharucoBoard(
            (border_num_x, border_num_y), 0.115, 0.09, dictionary
        )
        detector = aruco.CharucoDetector(board)

        ch_corners, ch_ids, markers_corners, marker_ids = detector.detectBoard(img)
        # https://docs.opencv.org/4.10.0/d9/df5/classcv_1_1aruco_1_1CharucoDetector.html
        if ch_corners is not None:
            # https://docs.opencv.org/4.x/d4/db2/classcv_1_1aruco_1_1Board.html
            aruco.drawDetectedCornersCharuco(
                img, ch_corners, ch_ids, (0, 255, 0)
            )
        else: 
            logger.warning(f"Failed to detect Charuco board in {img_path}")
            continue
        if markers_corners is not None:
            aruco.drawDetectedMarkers(img, markers_corners, marker_ids)
        output_path = OUTPUT_FOLDER / (f"{img_path.stem}_output.jpg")
        logger.info(f"Saving to {output_path}")
        cv2.imwrite(str(output_path), img)

if __name__ == "__main__":
    main()

import cv2
from cv2 import aruco
from cv2.typing import MatLike
from enum import Enum
from pathlib import Path
from loguru import logger
from itertools import chain


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


def create_charuco_board(
    square_x: int,
    square_y: int,
    square_length: float,
    marker_length: float,
    dictionary: aruco.Dictionary,
) -> aruco.CharucoBoard:
    return aruco.CharucoBoard(  # type: ignore
        (square_x, square_y), square_length, marker_length, dictionary
    )


# IMAGE_PATH = Path("/Users/crosstyan/Downloads/IMG_1505.jpeg")
# IMAGE_PATH = Path("ss.png")
IMAGE_FOLDER = Path("at")
OUTPUT_FOLDER = Path("output")
DICTIONARY = ArucoDictionary.Dict_4X4_50

def main():
    OUTPUT_FOLDER.mkdir(exist_ok=True)
    images = chain(IMAGE_FOLDER.glob("*.jpeg"), IMAGE_FOLDER.glob("*.png"), IMAGE_FOLDER.glob("*.jpg"))
    for img_path in images:
        img = cv2.imread(str(img_path))
        # 10x7
        # minus 1
        border_num_x = 9
        border_num_y = 6
        # 115mm square
        # 90mm marker
        # https://docs.opencv.org/4.x/d9/d6a/group__aruco.html#ga3bc50d61fe4db7bce8d26d56b5a6428a
        # https://docs.opencv.org/4.x/df/d4a/tutorial_charuco_detection.html
        # https://docs.opencv.org/3.4/df/d4a/tutorial_charuco_detection.html
        # https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html

        # https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html#ga93efa9b0aa890de240ca32b11253dd4a
        # https://docs.opencv.org/4.x/da/d13/tutorial_aruco_calibration.html
        # https://github.com/opencv/opencv/issues/22083
        ret, chess_corners = cv2.findChessboardCorners(
            img,
            (border_num_x, border_num_y),
            flags=cv2.CALIB_CB_ADAPTIVE_THRESH
            | cv2.CALIB_CB_NORMALIZE_IMAGE
            | cv2.CALIB_CB_FAST_CHECK,
        )
        if ret:
            cv2.drawChessboardCorners(
                img, (border_num_x, border_num_y), chess_corners, ret
            )
            cv2.imwrite(str(OUTPUT_FOLDER / f"{img_path.stem}_chess.jpg"), img)
            logger.info("Chessboard found for {}", img_path)
        else:
            logger.warning("Chessboard not found for {}", img_path)

        # predefined_dict = aruco.getPredefinedDictionary(DICTIONARY.value)
        # corners, ids, rejected = aruco.detectMarkers(img, predefined_dict)
        # board = create_charuco_board(10, 7, 115, 90, predefined_dict)
        # detector = aruco.CharucoDetector(board)
        # if ids is not None:
        #     aruco.drawDetectedMarkers(img, corners, ids)
        #     ret, ch_corners, ch_ids =  aruco.interpolateCornersCharuco(corners, ids, img, board)
        #     if ch_corners is not None and ch_ids is not None:
        #         aruco.drawDetectedCornersCharuco(img, ch_corners, ch_ids)
        # cv2.imwrite("output.jpg", img)


if __name__ == "__main__":
    main()

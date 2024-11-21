import cv2
from cv2 import aruco
from cv2.typing import MatLike
from enum import Enum
from pathlib import Path


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
    return aruco.CharucoBoard( # type: ignore
        (square_x, square_y), square_length, marker_length, dictionary
    )

IMAGE_PATH= Path("/Users/crosstyan/Downloads/IMG_1505.jpeg")

def main():
    ...
    img: MatLike
    img = cv2.imread(str(IMAGE_PATH))
    # 10x7
    # 115mm square
    # 90mm marker
    dictionary = ArucoDictionary.Dict_4X4_50
    predifined = aruco.getPredefinedDictionary(dictionary.value)
    # https://docs.opencv.org/4.x/d9/d6a/group__aruco.html#ga3bc50d61fe4db7bce8d26d56b5a6428a
    # https://docs.opencv.org/4.x/df/d4a/tutorial_charuco_detection.html
    corners, ids, rejected = aruco.detectMarkers(img, predifined)
    board = create_charuco_board(10, 7, 115, 90, predifined)
    if ids is not None:
        aruco.drawDetectedMarkers(img, corners, ids)
        _, ch_corners, ch_ids =  aruco.interpolateCornersCharuco(corners, ids, img, board)
        if ch_corners is not None and ch_ids is not None:
            aruco.drawDetectedCornersCharuco(img, ch_corners, ch_ids)
    cv2.imwrite("output.jpg", img)
    

if __name__ == "__main__":
    main()


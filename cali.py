import cv2
import numpy as np
from cv2 import aruco
from cv2.typing import MatLike
from enum import Enum
from pathlib import Path
from loguru import logger
from itertools import chain
from typing import Optional, Sequence, TypedDict, cast
import awkward as ak

from matplotlib.pyplot import stem
from numpy import ndarray


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


IMAGE_FOLDER = Path("dumped/cam")
OUTPUT_FOLDER = Path("output")
DICTIONARY = ArucoDictionary.Dict_4X4_50
CALIBRATION_PARQUET: Optional[Path] = OUTPUT_FOLDER / "usbcam_cal.parquet"


class CameraParams(TypedDict):
    camera_matrix: MatLike
    distortion_coefficients: MatLike
    rotation_vectors: MatLike
    translation_vectors: MatLike


def main():
    OUTPUT_FOLDER.mkdir(exist_ok=True)
    images = chain(
        IMAGE_FOLDER.glob("*.jpeg"),
        IMAGE_FOLDER.glob("*.png"),
        IMAGE_FOLDER.glob("*.jpg"),
    )
    border_num_x = 10
    border_num_y = 7
    dictionary = aruco.getPredefinedDictionary(DICTIONARY.value)
    board = aruco.CharucoBoard((border_num_x, border_num_y), 0.115, 0.09, dictionary)
    detector = aruco.CharucoDetector(board)
    all_ch_corners: list[MatLike] = []
    all_ch_ids: list[MatLike] = []
    all_image_points: list[MatLike] = []
    all_object_points: list[MatLike] = []
    last_shape = np.array((0, 0))
    calibration: Optional[ak.Record] = None

    def has_cal():
        return CALIBRATION_PARQUET is not None and CALIBRATION_PARQUET.exists()

    try:
        if has_cal():
            calibration_arr = ak.from_parquet(CALIBRATION_PARQUET)
            calibration = calibration_arr[0]
            logger.info(f"Loaded calibration parameters: {calibration}")
    except Exception as e:
        logger.error(f"Failed to load calibration parameters: {e}")
    for img_path in images:
        img = cv2.imread(str(img_path))
        last_shape = img.shape
        # 10x7
        # minus 1 when dealing with normal chessboard
        # 115mm square
        # 90mm marker
        # https://docs.opencv.org/3.4/df/d4a/tutorial_charuco_detection.html
        # https://docs.opencv.org/4.x/df/d4a/tutorial_charuco_detection.html
        # https://docs.opencv.org/4.x/da/d13/tutorial_aruco_calibration.html
        # https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html

        # https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html#ga93efa9b0aa890de240ca32b11253dd4a
        # https://github.com/opencv/opencv/issues/22083
        # OpenCV 4.10.x
        # pylint: disable-next=unpacking-non-sequence
        ch_corners, ch_ids, markers_corners, marker_ids = detector.detectBoard(img)
        # https://docs.opencv.org/4.10.0/d9/df5/classcv_1_1aruco_1_1CharucoDetector.html
        if ch_corners is not None:
            # https://docs.opencv.org/4.x/d4/db2/classcv_1_1aruco_1_1Board.html
            aruco.drawDetectedCornersCharuco(img, ch_corners, ch_ids, (0, 255, 0))
            all_ch_corners.append(ch_corners)
            all_ch_ids.append(ch_ids)
            # pylint: disable-next=unpacking-non-sequence
            op, ip = board.matchImagePoints(cast(Sequence[MatLike], ch_corners), ch_ids)
            all_object_points.append(op)
            all_image_points.append(ip)
            if calibration is not None:
                mtx = cast(MatLike, ak.to_numpy(calibration["camera_matrix"]))
                dist = cast(
                    MatLike, ak.to_numpy(calibration["distortion_coefficients"])
                )
                ret, rvec, tvec = cv2.solvePnP(op, ip, mtx, dist)
                if ret:
                    img = cv2.drawFrameAxes(img, mtx, dist, rvec, tvec, 0.1)
                else:
                    logger.warning(f"Failed to draw frame axes in {img_path}")
        else:
            logger.warning(f"Failed to detect Charuco board in {img_path}")
            continue
        if markers_corners is not None:
            aruco.drawDetectedMarkers(img, markers_corners, marker_ids)
        output_path = OUTPUT_FOLDER / (f"{img_path.stem}_output.jpg")
        logger.info(f"Saving to {output_path}")
        cv2.imwrite(str(output_path), img)

    # compute calibration
    if calibration is None and len(all_image_points) > 0:
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
            all_object_points, all_image_points, (last_shape[0], last_shape[1]), None, None  # type: ignore
        )  # type: ignore
        logger.info(f"Camera matrix: {mtx}")
        logger.info(f"Distortion coefficients: {dist}")
        logger.info(f"Rotation vectors: {rvecs}")
        logger.info(f"Translation vectors: {tvecs}")
        parameters = {
            "camera_matrix": mtx,
            "distortion_coefficients": dist,
            "rotation_vectors": rvecs,
            "translation_vectors": tvecs,
        }
        ak.to_parquet([parameters], CALIBRATION_PARQUET)
    else:
        logger.warning(
            "no calibration data calculated; either no images or already calibrated"
        )


if __name__ == "__main__":
    main()

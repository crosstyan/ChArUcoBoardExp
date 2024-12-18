import cv2
from cv2 import aruco
from datetime import datetime
from loguru import logger
from pathlib import Path
from typing import cast, Final
import awkward as ak
from cv2.typing import MatLike
import numpy as np

NDArray = np.ndarray
CALIBRATION_PARQUET = Path("output") / "usbcam_cal.parquet"
OBJECT_POINTS_PARQUET = Path("output") / "object_points.parquet"
DICTIONARY: Final[int] = aruco.DICT_4X4_50
# 400mm
MARKER_LENGTH: Final[float] = 0.4


def gen():
    API = cv2.CAP_AVFOUNDATION
    cap = cv2.VideoCapture(0, API)
    while True:
        ret, frame = cap.read()
        if not ret:
            logger.warning("Failed to grab frame")
            break
        yield frame


def main():
    aruco_dict = aruco.getPredefinedDictionary(DICTIONARY)
    cal = ak.from_parquet(CALIBRATION_PARQUET)[0]
    camera_matrix = cast(MatLike, ak.to_numpy(cal["camera_matrix"]))
    distortion_coefficients = cast(MatLike, ak.to_numpy(cal["distortion_coefficients"]))
    ops = ak.from_parquet(OBJECT_POINTS_PARQUET)
    board = aruco.CharucoBoard(
        size=(3, 3), squareLength=0.127, markerLength=0.097, dictionary=aruco_dict
    )
    detector = aruco.CharucoDetector(board)

    for frame in gen():
        grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # pylint: disable-next=unpacking-non-sequence
        diamond_corners, diamond_ids, markers, marker_ids = detector.detectDiamonds(
            grey
        )
        # `markers` is [N, 1, 4, 2]
        # `ids` is [N, 1]
        if diamond_ids is not None:
            aruco.drawDetectedDiamonds(frame, diamond_corners, diamond_ids)
        cv2.imshow("frame", frame)
        if (k := cv2.waitKey(1)) == ord("q"):
            logger.info("Exiting")
            break
        elif k == ord("s"):
            now = datetime.now().strftime("%Y%m%d%H%M%S")
            file_name = f"aruco_{now}.png"
            logger.info("Saving to {}", file_name)
            cv2.imwrite(file_name, frame)


if __name__ == "__main__":
    main()

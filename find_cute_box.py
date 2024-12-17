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
    detector = aruco.ArucoDetector(
        dictionary=aruco_dict, detectorParams=aruco.DetectorParameters()
    )

    for frame in gen():
        grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # pylint: disable-next=unpacking-non-sequence
        markers, ids, rejected = detector.detectMarkers(grey)
        # `markers` is [N, 1, 4, 2]
        # `ids` is [N, 1]
        if ids is not None:
            markers = np.reshape(markers, (-1, 4, 2))
            ids = np.reshape(ids, (-1, 1))
            # logger.info("markers={}, ids={}", np.array(markers).shape, np.array(ids).shape)
            for m, i in zip(markers, ids):
                center = np.mean(m, axis=0).astype(int)
                GREY = (128, 128, 128)
                logger.info("id={}, center={}", i, center)
                cv2.circle(frame, tuple(center), 5, GREY, -1)
                cv2.putText(
                    frame,
                    str(i),
                    tuple(center),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    GREY,
                    2,
                )
                # BGR
                RED = (0, 0, 255)
                GREEN = (0, 255, 0)
                BLUE = (255, 0, 0)
                YELLOW = (0, 255, 255)
                color_map = [RED, GREEN, BLUE, YELLOW]
                for color, corners in zip(color_map, m):
                    corners = corners.astype(int)
                    frame = cv2.circle(frame, corners, 5, color, -1)
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

import re
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
    detector = aruco.ArucoDetector(
        dictionary=aruco_dict, detectorParams=aruco.DetectorParameters()
    )

    total_ids = cast(NDArray, ak.to_numpy(ops["ids"])).flatten()
    total_corners = cast(NDArray, ak.to_numpy(ops["corners"])).reshape(-1, 4, 3)
    ops_map: dict[int, NDArray] = dict(zip(total_ids, total_corners))
    logger.info("ops_map={}", ops_map)

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
            ips_map: dict[int, NDArray] = {}
            for cs, id in zip(markers, ids):
                id = int(id)
                cs = cast(NDArray, cs)
                ips_map[id] = cs
                center = np.mean(cs, axis=0).astype(int)
                GREY = (128, 128, 128)
                # logger.info("id={}, center={}", id, center)
                cv2.circle(frame, tuple(center), 5, GREY, -1)
                cv2.putText(
                    frame,
                    str(id),
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
                for color, corners in zip(color_map, cs):
                    corners = corners.astype(int)
                    frame = cv2.circle(frame, corners, 5, color, -1)
            # https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html#ga50620f0e26e02caa2e9adc07b5fbf24e
            ops: NDArray = np.empty((0, 3), dtype=np.float32)
            ips: NDArray = np.empty((0, 2), dtype=np.float32)
            for id, ip in ips_map.items():
                try:
                    op = ops_map[id]
                    assert ip.shape == (4, 2), f"corners.shape={ip.shape}"
                    assert op.shape == (4, 3), f"op.shape={op.shape}"
                    ops = np.concatenate((ops, op), axis=0)
                    ips = np.concatenate((ips, ip), axis=0)
                except KeyError:
                    logger.warning("No object points for id={}", id)
                    continue
            assert len(ops) == len(ips), f"len(ops)={len(ops)} != len(ips)={len(ips)}"
            if len(ops) > 0:
                # https://docs.opencv.org/4.x/d5/d1f/calib3d_solvePnP.html
                # https://docs.opencv.org/4.x/d5/d1f/calib3d_solvePnP.html#calib3d_solvePnP_flags
                ret, rvec, tvec= cv2.solvePnP(
                    objectPoints=ops,
                    imagePoints=ips,
                    cameraMatrix=camera_matrix,
                    distCoeffs=distortion_coefficients,
                    flags=cv2.SOLVEPNP_SQPNP,
                )
                # ret, rvec, tvec, inliners = cv2.solvePnPRansac(
                #     objectPoints=ops,
                #     imagePoints=ips,
                #     cameraMatrix=camera_matrix,
                #     distCoeffs=distortion_coefficients,
                #     flags=cv2.SOLVEPNP_SQPNP,
                # )
                if ret:
                    cv2.drawFrameAxes(
                        frame,
                        camera_matrix,
                        distortion_coefficients,
                        rvec,
                        tvec,
                        MARKER_LENGTH,
                    )
                else:
                    logger.warning("Failed to solvePnPRansac")
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

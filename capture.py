import cv2
from datetime import datetime
from loguru import logger
from pathlib import Path

BASE_PATH = Path("dumped/cam")

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
    for frame in gen():
        cv2.imshow("frame", frame)
        k = cv2.waitKey(1)
        if k == ord("q"):
            break
        elif k == ord("s"):
            now = datetime.now()
            filename = BASE_PATH / f"capture_{now.strftime('%Y%m%d%H%M%S')}.jpg"
            logger.warning(f"Saving to {filename}")
            cv2.imwrite(str(filename), frame)
        else:
            ...

if __name__ == "__main__":
    main()

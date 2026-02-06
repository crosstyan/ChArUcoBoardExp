import cv2
import time


def test_props():
    # Force AVFoundation
    cap = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)

    if not cap.isOpened():
        print("Cannot open camera")
        return

    print(f"Backend: {cap.getBackendName()}")

    # Properties to test
    props = {
        "EXPOSURE": cv2.CAP_PROP_EXPOSURE,
        "BRIGHTNESS": cv2.CAP_PROP_BRIGHTNESS,
        "GAIN": cv2.CAP_PROP_GAIN,
        "SATURATION": cv2.CAP_PROP_SATURATION,
        "CONTRAST": cv2.CAP_PROP_CONTRAST,
        "AUTO_EXPOSURE": cv2.CAP_PROP_AUTO_EXPOSURE,
        "IRIS": cv2.CAP_PROP_IRIS,
        "SETTINGS": cv2.CAP_PROP_SETTINGS,
    }

    print("\nInitial Values:")
    for name, prop_id in props.items():
        val = cap.get(prop_id)
        print(f"  {name}: {val}")

    print("\nAttempting to set EXPOSURE to various values...")
    # Try typical ranges. Some backends use -10..10, others 0..1, others raw ms
    test_vals = [-5.0, -1.0, 0.0, 0.5, 50.0]

    for v in test_vals:
        print(f"  Setting EXPOSURE to {v}...", end="")
        cap.set(cv2.CAP_PROP_EXPOSURE, v)
        time.sleep(0.5)
        new_val = cap.get(cv2.CAP_PROP_EXPOSURE)
        print(f" -> Result: {new_val}")

    print("\nAttempting to open Settings Dialog (CAP_PROP_SETTINGS)...")
    cap.set(cv2.CAP_PROP_SETTINGS, 1)
    print("  (Did a window pop up?)")
    time.sleep(2)

    cap.release()


if __name__ == "__main__":
    test_props()

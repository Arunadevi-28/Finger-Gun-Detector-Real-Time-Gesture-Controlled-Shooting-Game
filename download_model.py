from pathlib import Path
from urllib.request import urlopen


MODEL_URL = (
    "https://storage.googleapis.com/"
    "mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/1/"
    "hand_landmarker.task"
)

MODEL_PATH = Path("hand_landmarker.task")


def download_model():
    if MODEL_PATH.exists() and MODEL_PATH.stat().st_size > 0:
        print("Hand Landmarker model already exists.")
        print(f"Size: {MODEL_PATH.stat().st_size:,} bytes")
        return

    print("Downloading MediaPipe Hand Landmarker model...")
    print()

    try:
        with urlopen(MODEL_URL) as response:
            model_data = response.read()

        MODEL_PATH.write_bytes(model_data)

        print("Download completed successfully.")
        print()
        print(f"File: {MODEL_PATH}")
        print(f"Size: {MODEL_PATH.stat().st_size:,} bytes")

    except Exception as error:
        print("ERROR: Could not download the model.")
        print(error)


if __name__ == "__main__":
    download_model()
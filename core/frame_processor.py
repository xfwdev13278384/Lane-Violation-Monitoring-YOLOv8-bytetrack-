import cv2


class FrameProcessor:

    BRIGHTNESS_THRESHOLD = 100

    @staticmethod
    def calculate_brightness(frame):
        gray = cv2 .cvtColor(frame, cv2 .COLOR_BGR2GRAY)
        return gray .mean()

    @staticmethod
    def is_daytime(frame):
        brightness = FrameProcessor .calculate_brightness(frame)
        return brightness > FrameProcessor .BRIGHTNESS_THRESHOLD

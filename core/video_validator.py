import cv2
import os


class VideoValidator:
    @staticmethod
    def validate(video_path):
        if not os .path .exists(video_path):
            error_msg = f"[ERROR] Video không tồn tại: {video_path }"
            print(error_msg)
            raise FileNotFoundError(error_msg)

        if not os .path .isfile(video_path):
            error_msg = f"[ERROR] Đường dẫn không phải là file: {video_path }"
            print(error_msg)
            raise ValueError(error_msg)

        cap = cv2 .VideoCapture(video_path)
        if not cap .isOpened():
            error_msg = f"[ERROR] Không thể mở video (file lỗi hoặc codec không hỗ trợ): {video_path }"
            print(error_msg)
            cap .release()
            raise ValueError(error_msg)

        ret, _ = cap .read()
        cap .release()
        if not ret:
            error_msg = f"[ERROR] Video không có frame hợp lệ: {video_path }"
            print(error_msg)
            raise ValueError(error_msg)

        print(f"[INFO] Video hợp lệ: {video_path }")

        video_name = os .path .splitext(os .path .basename(video_path))[0]
        return video_name

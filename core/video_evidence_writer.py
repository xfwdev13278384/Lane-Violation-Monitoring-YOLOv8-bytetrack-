import cv2
import os


class VideoEvidenceWriter:
    def __init__(
        self,
        output_root="core/outputs",
        slow_repeat=2,
        fps_out=30
    ):
        self .output_root = output_root
        self .slow_repeat = slow_repeat
        self .fps_out = fps_out

        self .writer = None
        self .out_path = None

    def start(self, run_dir, frame_shape):
        h, w = frame_shape[:2]

        self .out_path = os .path .join(
            run_dir,
            "lane_evidence.mp4"
        )

        fourcc = cv2 .VideoWriter_fourcc(*"mp4v")
        self .writer = cv2 .VideoWriter(
            self .out_path,
            fourcc,
            self .fps_out,
            (w, h)
        )

        print(f"[VIDEO] Evidence writer started → {self .out_path }")

    def write(self, frame, is_violation=False):
        if self .writer is None:
            return

        if is_violation:
            for _ in range(self .slow_repeat):
                self .writer .write(frame)
        else:
            self .writer .write(frame)

    def release(self):
        if self .writer is not None:
            try:
                self .writer .release()
            finally:
                self .writer = None
                print(f"[VIDEO] Evidence saved → {self .out_path }")

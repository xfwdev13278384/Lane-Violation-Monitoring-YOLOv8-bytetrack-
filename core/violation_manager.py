import os
import cv2
import csv
from core .db_writer import insert_violation
from datetime import datetime


class ViolationManager:
    def __init__(self, output_root="core/outputs"):
        self .output_root = output_root

        self .reset_for_new_video()

    def reset_for_new_video(self):
        self .violated_ids = set()
        self .violation_count = 0
        self .car_violation_count = 0
        self .motor_violation_count = 0
        self .run_id = datetime .now().strftime("run_%Y%m%d_%H%M%S")

    def handle_violation(
        self,
        track_id,
        vehicle_class,
        frame,
        bbox,
        frame_id,
        lane,
        video_name,
        run_dir
    ):
        if track_id in self .violated_ids:
            return

        self .violated_ids .add(track_id)
        self .violation_count += 1

        if vehicle_class in {"car", "truck", "bus"}:
            self .car_violation_count += 1
        elif vehicle_class == "motorcycle":
            self .motor_violation_count += 1

        image_dir = os .path .join(run_dir, "images")
        os .makedirs(image_dir, exist_ok=True)

        csv_path = os .path .join(run_dir, "violations.csv")

        img_name = f"id{track_id }_f{frame_id }.jpg"
        img_path = os .path .join(image_dir, img_name)
        cv2 .imwrite(img_path, frame)

        insert_violation(
            vehicle_type=vehicle_class,
            license_plate=None,
            violation_type="Đi sai làn đường",
            violation_time=datetime .now(),
            image_path=img_path,
            video_name=video_name
        )

        write_header = not os .path .exists(csv_path)
        with open(csv_path, "a", newline="", encoding="utf-8")as f:
            writer = csv .writer(f)
            if write_header:
                writer .writerow([
                    "video", "run_id", "track_id", "vehicle_class",
                    "frame_id", "lane", "image_path"
                ])
            writer .writerow([
                video_name, self .run_id, track_id, vehicle_class,
                frame_id, lane, img_path
            ])

        print(
            f"[VIOLATION] {video_name } | {self .run_id } | "
            f"ID={track_id } | CAR={self .car_violation_count } | MOTOR={self .motor_violation_count }"
        )

import cv2
import os
from ultralytics import YOLO

from core .geometry_utils import bbox_inside_polygon_by_2_centers
from core .lane_violation_logic import LaneViolationLogic
from core .violation_manager import ViolationManager
from core .video_evidence_writer import VideoEvidenceWriter
from core .db_writer import flush_pending_inserts


from core .video_validator import VideoValidator
from core .frame_processor import FrameProcessor
from core .lane_configuration import LaneConfiguration
from core .frame_visualizer import FrameVisualizer


class TrackingROIDirection:
    def __init__(self, model_path, device="cuda"):

        self .model = YOLO(model_path)
        self .model .to(device)
        self .names = self .model .names

        self .validator = VideoValidator()
        self .frame_processor = FrameProcessor()
        self .lane_config = LaneConfiguration()
        self .visualizer = FrameVisualizer()

        self .violation_logic = LaneViolationLogic()
        self .violation_manager = ViolationManager()

        self .video_writer = VideoEvidenceWriter(
            slow_repeat=2,
            fps_out=30
        )

    def run(self, video_path):
        video_name = self .validator .validate(video_path)

        self .violation_manager .reset_for_new_video()
        run_id = self .violation_manager .run_id
        base_run_dir = os .path .join(
            self .violation_manager .output_root,
            video_name,
            run_id
        )
        os .makedirs(base_run_dir, exist_ok=True)
        print(f"[RUN] Output dir: {base_run_dir }")

        motor_lane = self .lane_config .get_motor_lane()
        car_lane = self .lane_config .get_car_lane()

        results = self .model .track(
            source=video_path,
            stream=True,
            persist=True,
            tracker="bytetrack.yaml",
            conf=0.3,
            iou=0.5,
            show=False
        )

        video_started = False

        for frame_id, result in enumerate(results, start=1):
            frame = result .orig_img .copy()

            if not video_started:
                self .video_writer .start(
                    run_dir=base_run_dir,
                    frame_shape=frame .shape
                )
                video_started = True

            self .visualizer .draw_lanes(frame, motor_lane, car_lane)

            is_daytime = self .frame_processor .is_daytime(frame)

            has_violation_in_frame = False

            if result .boxes is not None:
                for i in range(len(result .boxes)):
                    cls_id = int(result .boxes .cls[i])
                    vehicle_class = self .names[cls_id]

                    track_id = (
                        int(result .boxes .id[i])
                        if result .boxes .id is not None
                        else -1
                    )

                    x1, y1, x2, y2 = result .boxes .xyxy[i].int().tolist()
                    box = (x1, y1, x2, y2)

                    in_car = bbox_inside_polygon_by_2_centers(box, car_lane)
                    in_motor = bbox_inside_polygon_by_2_centers(
                        box, motor_lane)

                    if in_car:
                        current_lane = "CAR"
                    elif in_motor:
                        current_lane = "MOTOR"
                    else:
                        continue

                    violated, _ = self .violation_logic .check_violation(
                        track_id=track_id,
                        vehicle_class=vehicle_class,
                        current_lane=current_lane
                    )

                    if violated:
                        has_violation_in_frame = True
                        self .violation_manager .handle_violation(
                            track_id=track_id,
                            vehicle_class=vehicle_class,
                            frame=frame,
                            bbox=box,
                            frame_id=frame_id,
                            lane=current_lane,
                            video_name=video_name,
                            run_dir=base_run_dir
                        )

                    self .visualizer .draw_bbox(
                        frame=frame,
                        bbox=box,
                        track_id=track_id,
                        vehicle_class=vehicle_class,
                        current_lane=current_lane,
                        is_violation=violated
                    )

            self .visualizer .draw_statistics(
                frame=frame,
                car_violation_count=self .violation_manager .car_violation_count,
                motor_violation_count=self .violation_manager .motor_violation_count,
                is_daytime=is_daytime
            )

            self .video_writer .write(
                frame,
                is_violation=has_violation_in_frame
            )

            cv2 .imshow("Lane violation", frame)
            if cv2 .waitKey(1) & 0xFF == ord("q"):
                break

        self .video_writer .release()
        cv2 .destroyAllWindows()

        flush_pending_inserts()

        return {
            "run_id": run_id,
            "total_violations": self .violation_manager .violation_count,
            "car_violations": self .violation_manager .car_violation_count,
            "motor_violations": self .violation_manager .motor_violation_count,
            "output_dir": os .path .join(
                self .violation_manager .output_root,
                video_name,
                run_id
            )
        }

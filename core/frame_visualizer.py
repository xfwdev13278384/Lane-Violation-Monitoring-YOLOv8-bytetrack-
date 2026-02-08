import cv2


class FrameVisualizer:

    COLOR_DAY = (0, 165, 255)
    COLOR_NIGHT = (255, 255, 0)

    COLOR_MOTOR_LANE = (255, 255, 0)
    COLOR_CAR_LANE = (0, 255, 255)

    COLOR_VIOLATION = (0, 0, 255)
    COLOR_NORMAL = (0, 255, 0)

    @staticmethod
    def draw_lanes(frame, motor_lane, car_lane):
        cv2 .polylines(
            frame,
            [motor_lane],
            True,
            FrameVisualizer .COLOR_MOTOR_LANE,
            2
        )
        cv2 .polylines(
            frame,
            [car_lane],
            True,
            FrameVisualizer .COLOR_CAR_LANE,
            2
        )

    @staticmethod
    def draw_bbox(frame, bbox, track_id, vehicle_class, current_lane, is_violation):
        x1, y1, x2, y2 = bbox

        color = FrameVisualizer .COLOR_VIOLATION if is_violation else FrameVisualizer .COLOR_NORMAL

        if is_violation:
            label = f"ID {track_id } | {vehicle_class } | VIOLATION"
        else:
            label = f"ID {track_id } | {vehicle_class } | {current_lane }"

        cv2 .rectangle(frame, (x1, y1), (x2, y2), color, 2)

        cv2 .putText(
            frame,
            label,
            (x1, y1 - 6),
            cv2 .FONT_HERSHEY_SIMPLEX,
            0.6,
            color,
            2
        )

    @staticmethod
    def draw_statistics(frame, car_violation_count, motor_violation_count, is_daytime):
        text_color = FrameVisualizer .COLOR_DAY if is_daytime else FrameVisualizer .COLOR_NIGHT

        cv2 .putText(
            frame,
            f"car violation: {car_violation_count }",
            (30, 40),
            cv2 .FONT_HERSHEY_SIMPLEX,
            0.9,
            text_color,
            3
        )

        cv2 .putText(
            frame,
            f"motor violation: {motor_violation_count }",
            (30, 80),
            cv2 .FONT_HERSHEY_SIMPLEX,
            0.9,
            text_color,
            3
        )

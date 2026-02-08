import numpy as np


class LaneConfiguration:
    def __init__(self):

        self .motor_lane = np .array([
            (2, 178),
            (246, 180),
            (273, 533),
            (4, 538)
        ])

        self .car_lane = np .array([
            (248, 181),
            (417, 175),
            (468, 529),
            (276, 533)
        ])

    def get_motor_lane(self):
        return self .motor_lane

    def get_car_lane(self):
        return self .car_lane

    def get_all_lanes(self):
        return {
            "motor": self .motor_lane,
            "car": self .car_lane
        }

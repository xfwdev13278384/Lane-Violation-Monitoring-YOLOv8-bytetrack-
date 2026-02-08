class LaneViolationLogic:
    def __init__(self):

        self .vehicle_states = {}

        self .motor_classes = {"motorcycle"}
        self .car_classes = {"car", "truck", "bus"}

    def check_violation(self, track_id, vehicle_class, current_lane):

        if current_lane is None:
            return False, None

        if vehicle_class in self .motor_classes and current_lane == "CAR":
            return True, "MOTOR_IN_CAR_LANE"

        if vehicle_class in self .car_classes and current_lane == "MOTOR":
            return True, "CAR_IN_MOTOR_LANE"

        if track_id not in self .vehicle_states:

            self .vehicle_states[track_id] = {
                "initial_lane": current_lane,
                "violated": False
            }
            return False, None

        state = self .vehicle_states[track_id]

        if state["violated"]:
            return True, "PREVIOUS_VIOLATION"

        if current_lane != state["initial_lane"]:
            state["violated"] = True
            return True, "LANE_CHANGE_VIOLATION"

        return False, None

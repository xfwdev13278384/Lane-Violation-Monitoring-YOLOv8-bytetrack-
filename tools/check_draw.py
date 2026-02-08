from draw_lane_roi import draw_two_lanes 

motor_lane ,car_lane =draw_two_lanes (r"D:\PyCharm\ITS\71.-yolov8-main\VIDEOOO\lane.mp4")

print ("\n=== MOTOR LANE ===")
for p in motor_lane :
    print (p )

print ("\n=== CAR LANE ===")
for p in car_lane :
    print (p )

import cv2 
import os 

current_points =[]
all_lanes =[]
frame_show =None 

def mouse_callback (event ,x ,y ,flags ,param ):
    global current_points ,frame_show 

    if event ==cv2 .EVENT_LBUTTONDOWN :
        current_points .append ((x ,y ))
        print (f"[CLICK] ({x }, {y })")

        cv2 .circle (frame_show ,(x ,y ),5 ,(0 ,0 ,255 ),-1 )

        if len (current_points )>1 :
            cv2 .line (
            frame_show ,
            current_points [-2 ],
            current_points [-1 ],
            (0 ,255 ,255 ),
            2 
            )

def save_coordinates_to_file (motor_lane ,car_lane ,video_name =None ):
    if video_name :

        base_name =os .path .splitext (os .path .basename (video_name ))[0 ]
        output_file =f"{base_name }_coordinates.txt"
    else :
        output_file ="video_coordinates.txt"

    with open (output_file ,'w',encoding ='utf-8')as f :

        f .write ("=== MOTOR LANE === \n")
        for x ,y in motor_lane :
            f .write (f"({x }, {y }),\n")


        f .write ("=== CAR LANE === \n")
        for x ,y in car_lane :
            f .write (f"({x }, {y }),\n")


    print (f"✅ Đã lưu tọa độ vào file: {output_file }")
    return output_file 

def draw_two_lanes (video_path ):
    global current_points ,all_lanes ,frame_show 

    cap =cv2 .VideoCapture (video_path )
    ret ,frame =cap .read ()
    cap .release ()

    if not ret :
        print ("❌ Không đọc được video")
        return None ,None 

    frame_show =frame .copy ()

    cv2 .namedWindow ("DRAW ROI")
    cv2 .setMouseCallback ("DRAW ROI",mouse_callback )

    print ("\n👉 VẼ LANE XE MÁY (click 4 điểm, Enter để chốt)")
    while True :
        cv2 .imshow ("DRAW ROI",frame_show )
        key =cv2 .waitKey (1 )&0xFF 
        if key ==13 :
            break 

    all_lanes .append (current_points .copy ())
    current_points .clear ()

    print ("\n👉 VẼ LANE Ô TÔ (click 4 điểm, Enter để chốt)")
    while True :
        cv2 .imshow ("DRAW ROI",frame_show )
        key =cv2 .waitKey (1 )&0xFF 
        if key ==13 :
            break 

    all_lanes .append (current_points .copy ())
    cv2 .destroyAllWindows ()

    motor_lane ,car_lane =all_lanes 


    save_coordinates_to_file (motor_lane ,car_lane ,video_path )

    return motor_lane ,car_lane 

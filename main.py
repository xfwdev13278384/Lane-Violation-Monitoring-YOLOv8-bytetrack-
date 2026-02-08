import sys 
from core .tracking_roi_direction import TrackingROIDirection 

VIDEO_DEFAULT ="VIDEOOO/main.mp4"

if __name__ =="__main__":
    video_path =sys .argv [1 ]if len (sys .argv )>1 else VIDEO_DEFAULT 

    TrackingROIDirection (
    model_path ="runs/detect/train/weights/best.pt",
    device ="cuda"
    ).run (video_path )

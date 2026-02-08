import cv2
import numpy as np


def point_in_polygon(point, polygon):
    return cv2 .pointPolygonTest(
        np .array(polygon, np .int32),
        point,
        False
    ) >= 0


def get_bbox_centers(box):
    x1, y1, x2, y2 = box
    cx = (x1 + x2)//2

    top_center = (cx, y1)
    bottom_center = (cx, y2)

    return top_center, bottom_center


def bbox_inside_polygon_by_2_centers(box, polygon):
    top_center, bottom_center = get_bbox_centers(box)

    in_top = point_in_polygon(top_center, polygon)
    in_bottom = point_in_polygon(bottom_center, polygon)

    return in_top and in_bottom

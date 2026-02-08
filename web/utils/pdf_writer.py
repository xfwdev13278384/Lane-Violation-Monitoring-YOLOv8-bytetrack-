from reportlab .lib .pagesizes import A4
from reportlab .pdfgen import canvas
from reportlab .lib .units import cm
from reportlab .pdfbase import pdfmetrics
from reportlab .pdfbase .ttfonts import TTFont
from PIL import Image
import os


def generate_ticket_pdf(violation, output_path):

    font_path = os .path .join(os .path .dirname(__file__), "DejaVuSans.ttf")
    pdfmetrics .registerFont(TTFont("DejaVu", font_path))

    c = canvas .Canvas(output_path, pagesize=A4)
    c .setFont("DejaVu", 12)

    width, height = A4
    y = height - 2 * cm

    c .setFont("DejaVu", 13)
    c .drawCentredString(width / 2, y, "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM")
    y -= 0.8 * cm
    c .setFont("DejaVu", 11)
    c .drawCentredString(width / 2, y, "Độc lập, Tự do, Hạnh phúc")
    y -= 0.5 * cm
    y -= 1.2 * cm
    c .setFont("DejaVu", 15)
    c .drawCentredString(width / 2, y, "BIÊN BẢN VI PHẠM GIAO THÔNG")
    y -= 1 * cm
    c .setFont("DejaVu", 10)
    c .drawCentredString(
        width / 2, y, f"Số biên bản: #{violation .get ('id','N/A')}")
    y -= 0.5 * cm

    y -= 1.5 * cm
    c .setFont("DejaVu", 12)
    c .drawString(2 * cm, y, "THÔNG TIN VI PHẠM:")
    y -= 0.7 * cm
    c .setFont("DejaVu", 11)

    def draw_line(label, value):
        nonlocal y
        c .drawString(2.5 * cm, y, f"{label }:")
        c .drawString(7 * cm, y, str(value))
        y -= 0.7 * cm

    draw_line("Biển số phương tiện", violation .get(
        "license_plate", "(chưa nhận dạng)"))
    draw_line("Loại phương tiện", violation .get("vehicle_type", "N/A"))
    draw_line("Hành vi vi phạm", violation .get("violation_type", "N/A"))
    draw_line("Thời gian", str(violation .get("violation_time", "N/A")))
    draw_line("Nguồn video", violation .get("video_name", "N/A"))

    y -= 0.5 * cm
    y -= 0.8 * cm
    c .setFont("DejaVu", 12)
    c .drawString(2 * cm, y, "ẢNH MINH CHỨNG:")
    y -= 0.5 * cm
    BASE_DIR = os .path .dirname(os .path .dirname(
        os .path .dirname(os .path .abspath(__file__))))
    frame_path = violation .get("image_path")
    real_path = None
    if frame_path:
        candidate = os .path .join(BASE_DIR, frame_path)
        if os .path .exists(candidate):
            real_path = candidate
    if real_path:
        img = Image .open(real_path)
        max_width = width - 8 * cm
        max_height = 7 * cm
        img_width, img_height = img .size
        aspect = img_width / img_height
        if img_width > max_width or img_height > max_height:
            if (max_width / aspect) <= max_height:
                draw_width = max_width
                draw_height = max_width / aspect
            else:
                draw_height = max_height
                draw_width = max_height * aspect
        else:
            draw_width = img_width
            draw_height = img_height
        x_img = (width - draw_width)/2
        c .drawImage(real_path, x_img, y - draw_height,
                     draw_width, draw_height)
        y -= draw_height + 0.7 * cm
    else:
        c .setFont("DejaVu", 11)
        c .drawString(2.5 * cm, y, "Không có ảnh minh chứng.")
        y -= 1 * cm

    y -= 1 * cm
    c .setFont("DejaVu", 12)
    c .drawString(2 * cm, y, "KẾT LUẬN:")
    y -= 0.7 * cm
    c .setFont("DejaVu", 11)
    c .drawString(
        2.5 * cm, y, "Người vi phạm đã được thông báo về hành vi vi phạm.")
    y -= 0.7 * cm
    c .drawString(2.5 * cm, y, "Mức xử phạt theo quy định của pháp luật.")
    y -= 1.2 * cm

    y -= 2 * cm
    c .setFont("DejaVu", 11)
    c .drawString(3 * cm, y, "Người lập biên bản")
    c .drawString(width - 7 * cm, y, "Người vi phạm")
    y -= 1 * cm
    c .setFont("DejaVu", 10)
    c .drawString(3 * cm, y, "(Ký, ghi rõ họ tên)")
    c .drawString(width - 7 * cm, y, "(Ký, ghi rõ họ tên)")

    c .setFont("DejaVu", 8)
    c .setFillGray(0.5)
    c .drawCentredString(width / 2, 1.2 * cm, f"Trang 1")
    c .setFillGray(0)
    c .save()

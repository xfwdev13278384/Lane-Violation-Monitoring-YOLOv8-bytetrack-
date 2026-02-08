import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from flask import Flask, render_template, send_file, request, jsonify, redirect, url_for, flash
from werkzeug.utils import secure_filename
from web.utils.db import get_connection
from web.utils.pdf_writer import generate_ticket_pdf
import tempfile


def query_all(sql, params=None):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params or ())
        rows = cursor.fetchall()
        cursor.close()
        return rows
    finally:
        conn.close()


def query_one(sql, params=None):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params or ())
        row = cursor.fetchone()
        cursor.close()
        return row
    finally:
        conn.close()


app = Flask(__name__)
app.secret_key = 'its-traffic-system-2026-secret-key'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'web', 'static', 'evidence_videos')
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mkv', 'mov'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.template_filter('basename')
def basename_filter(path):
    if path:
        return os.path.basename(path)
    return ''


@app.errorhandler(404)
def not_found_error(error):
    return render_template("dashboard.html", stats={"total": 0, "car": 0, "motor": 0}, recent=[]), 404


@app.errorhandler(500)
def internal_error(error):
    return "Lỗi máy chủ nội bộ. Vui lòng thử lại sau.", 500


@app.route("/")
def home():
    sql_total = "SELECT COUNT(*) AS total FROM violations"
    sql_car = "SELECT COUNT(*) AS car FROM violations WHERE vehicle_type = 'car'"
    sql_motor = "SELECT COUNT(*) AS motor FROM violations WHERE vehicle_type = 'motorcycle'"
    sql_recent = """
                 SELECT id, vehicle_type, violation_type, violation_time, license_plate
                 FROM violations
                 ORDER BY violation_time DESC LIMIT 5
                 """

    total = query_one(sql_total)["total"]
    car = query_one(sql_car)["car"]
    motor = query_one(sql_motor)["motor"]
    recent_violations = query_all(sql_recent)

    stats = {"total": total, "car": car, "motor": motor}
    return render_template("dashboard.html", stats=stats, recent=recent_violations)


@app.route("/violations")
def violations():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)

    vehicle_type = request.args.get('vehicle_type', '', type=str)
    violation_type = request.args.get('violation_type', '', type=str)
    date_from = request.args.get('date_from', '', type=str)
    date_to = request.args.get('date_to', '', type=str)

    offset = (page - 1) * limit

    where_clauses = []
    params = []

    if vehicle_type:
        where_clauses.append("vehicle_type = %s")
        params.append(vehicle_type)

    if violation_type:
        where_clauses.append("violation_type LIKE %s")
        params.append(f"%{violation_type}%")

    if date_from:
        where_clauses.append("DATE(violation_time) >= %s")
        params.append(date_from)

    if date_to:
        where_clauses.append("DATE(violation_time) <= %s")
        params.append(date_to)

    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

    sql = f"""
        SELECT id, vehicle_type, violation_type, violation_time, license_plate, image_path
        FROM violations
        WHERE {where_sql}
        ORDER BY violation_time DESC
        LIMIT %s OFFSET %s
    """

    count_sql = f"SELECT COUNT(*) AS total FROM violations WHERE {where_sql}"

    params_with_limit = params + [limit, offset]
    rows = query_all(sql, params_with_limit)
    total_count = query_one(count_sql, params)["total"]

    violation_types_sql = "SELECT DISTINCT violation_type FROM violations ORDER BY violation_type"
    all_violation_types = query_all(violation_types_sql)

    total_pages = (total_count + limit - 1) // limit
    return render_template("violations.html",
                           violations=rows,
                           page=page,
                           total_pages=total_pages,
                           vehicle_type=vehicle_type,
                           violation_type=violation_type,
                           date_from=date_from,
                           date_to=date_to,
                           total_count=total_count,
                           all_violation_types=all_violation_types)


@app.route("/violations/<int:violation_id>")
def violation_detail(violation_id):
    sql = "SELECT * FROM violations WHERE id = %s"
    v = query_one(sql, (violation_id,))
    return render_template("ticket.html", v=v)


@app.route("/violations/<int:violation_id>/pdf")
def violation_pdf(violation_id):
    sql = "SELECT * FROM violations WHERE id = %s"
    v = query_one(sql, (violation_id,))
    if not v:
        return "Không tìm thấy biên bản", 404

    tmp_dir = tempfile.gettempdir()
    pdf_path = os.path.join(tmp_dir, f"violation_{violation_id}.pdf")
    generate_ticket_pdf(v, pdf_path)
    return send_file(pdf_path, as_attachment=True, download_name=f"bien_ban_vi_pham_{violation_id}.pdf")


@app.route("/statistics")
def statistics():
    sql_total = "SELECT COUNT(*) AS total FROM violations"
    sql_car = "SELECT COUNT(*) AS car FROM violations WHERE vehicle_type = 'car'"
    sql_motor = "SELECT COUNT(*) AS motor FROM violations WHERE vehicle_type = 'motorcycle'"

    total = query_one(sql_total)["total"]
    car = query_one(sql_car)["car"]
    motor = query_one(sql_motor)["motor"]

    sql_daily = """
                SELECT DATE(violation_time) as date, COUNT(*) as count
                FROM violations
                WHERE violation_time >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                GROUP BY DATE(violation_time)
                ORDER BY date DESC
                """
    daily_stats = query_all(sql_daily)

    sql_monthly = """
                  SELECT DATE_FORMAT(violation_time, '%Y-%m') as month, COUNT(*) as count
                  FROM violations
                  WHERE violation_time >= DATE_SUB(NOW(), INTERVAL 12 MONTH)
                  GROUP BY DATE_FORMAT(violation_time, '%Y-%m')
                  ORDER BY month DESC
                  """
    monthly_stats = query_all(sql_monthly)

    sql_hourly = """
                 SELECT HOUR(violation_time) as hour, COUNT(*) as count
                 FROM violations
                 GROUP BY HOUR(violation_time)
                 ORDER BY hour
                 """
    hourly_stats = query_all(sql_hourly)

    stats = {"total": total, "car": car, "motor": motor}
    return render_template("statistics.html", stats=stats, daily_stats=daily_stats,
                           monthly_stats=monthly_stats, hourly_stats=hourly_stats)


@app.route("/static/evidence/<path:filepath>")
def serve_evidence(filepath):
    real_path = os.path.join(BASE_DIR, filepath)
    if os.path.exists(real_path):
        return send_file(real_path, mimetype="image/jpeg")
    return "Image not found", 404


@app.route("/api/stats")
def api_stats():
    sql_total = "SELECT COUNT(*) AS total FROM violations"
    sql_car = "SELECT COUNT(*) AS car FROM violations WHERE vehicle_type = 'car'"
    sql_motor = "SELECT COUNT(*) AS motor FROM violations WHERE vehicle_type = 'motorcycle'"

    sql_today = "SELECT COUNT(*) AS today FROM violations WHERE DATE(violation_time) = CURDATE()"

    total = query_one(sql_total)["total"]
    car = query_one(sql_car)["car"]
    motor = query_one(sql_motor)["motor"]
    today = query_one(sql_today)["today"]

    return jsonify({
        "total": total,
        "car": car,
        "motor": motor,
        "today": today
    })


@app.route("/api/recent")
def api_recent():
    sql_recent = """
                 SELECT id, vehicle_type, violation_type, violation_time, license_plate
                 FROM violations
                 ORDER BY violation_time DESC LIMIT 5
                 """
    recent = query_all(sql_recent)

    for item in recent:
        if item.get('violation_time'):
            item['violation_time'] = str(item['violation_time'])

    return jsonify(recent)


@app.route("/violations/<int:violation_id>/upload-video", methods=['GET', 'POST'])
def upload_evidence_video(violation_id):
    if request.method == 'POST':

        if 'video_file' not in request.files:
            flash('Không có file video nào được chọn', 'error')
            return redirect(request.url)

        file = request.files['video_file']

        if file.filename == '':
            flash('Không có file video nào được chọn', 'error')
            return redirect(request.url)

        if file and allowed_file(file.filename):

            filename = secure_filename(file.filename)
            unique_filename = f"violation_{violation_id}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

            file.save(filepath)

            conn = get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE violations SET evidence_video = %s WHERE id = %s",
                    (unique_filename, violation_id)
                )
                conn.commit()
                cursor.close()
                flash('Tải lên video minh chứng thành công!', 'success')
            except Exception as e:
                flash(f'Lỗi khi cập nhật database: {str(e)}', 'error')
            finally:
                conn.close()

            return redirect(url_for('violation_detail', violation_id=violation_id))
        else:
            flash('Định dạng file không hợp lệ. Chỉ chấp nhận: mp4, avi, mkv, mov', 'error')
            return redirect(request.url)

    sql = "SELECT * FROM violations WHERE id = %s"
    v = query_one(sql, (violation_id,))
    return render_template("upload_video.html", violation=v)


@app.route("/evidence-video/<filename>")
def serve_evidence_video(filename):
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(video_path):
        return send_file(video_path, mimetype="video/mp4")
    return "Video not found", 404


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)

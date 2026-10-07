from flask import Flask, request, redirect, url_for, abort, make_response, jsonify
from markupsafe import escape

app = Flask(__name__)

app.config['JSON_AS_ASCII'] = False
app.json.ensure_ascii = False

STUDENTS = {
    "23T1020001": {"name": "Nguyễn Văn An", "lop": "K47A", "scores": {"PMMNM": 8.5, "CSDL": 7.0, "MMT": 9.0}},
    "23T1020002": {"name": "Trần Thị Bình", "lop": "K47A", "scores": {"PMMNM": 6.0, "CSDL": 5.5, "MMT": 7.0}},
    "23T1020003": {"name": "Lê Hoàng Cường", "lop": "K47B", "scores": {"PMMNM": 9.5, "CSDL": 9.0}},
    "23T1020004": {"name": "Phạm Minh Dũng", "lop": "K47B", "scores": {"PMMNM": 4.0, "CSDL": 3.5, "MMT": 5.0}},
    "23T1020005": {"name": "Hoàng Thu Hà", "lop": "K47A", "scores": {}},
    "23T1020006": {"name": "Võ Quốc Khánh", "lop": "K47C", "scores": {"PMMNM": 7.5, "MMT": 8.0}},
}

def average(scores):
    if not scores:
        return None
    return round(sum(scores.values()) / len(scores), 2)

def rank(avg):
    if avg is None:
        return "Chưa có điểm"
    if avg >= 8.5:
        return "Giỏi"
    if avg >= 7.0:
        return "Khá"
    if avg >= 5.0:
        return "Trung bình"
    return "Yếu"

def student_summary(mssv):
    if mssv not in STUDENTS:
        return None
    student = STUDENTS[mssv]
    avg = average(student["scores"])
    return {
        "mssv": mssv,
        "name": student["name"],
        "lop": student["lop"],
        "scores": student["scores"],
        "average": avg,
        "rank": rank(avg)
    }

def layout(title, body):
    escaped_title = escape(title)
    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>{escaped_title} - Sổ điểm</title>
</head>
<body>
    <nav>
        <a href="{url_for('home')}">Trang chủ</a> |
        <a href="{url_for('student_list')}">Sinh viên</a> |
        <a href="{url_for('search')}">Tìm kiếm</a>
    </nav>
    <hr>
    {body}
</body>
</html>"""

@app.route("/")
def home():
    total_students = len(STUDENTS)
    classes = sorted(list(set(s["lop"] for s in STUDENTS.values())))
    body = f"""
    <h1>Tổng quan sổ điểm</h1>
    <p>Tổng số sinh viên: <strong>{total_students}</strong></p>
    <p>Số lớp: <strong>{len(classes)}</strong></p>
    <p>
        <a href="{url_for('student_list')}">Xem danh sách sinh viên</a> | 
        <a href="{url_for('api_students')}">Xem API sinh viên</a>
    </p>
    """
    return layout("Trang chủ", body)

@app.route("/students")
def student_list():
    lop_filter = request.args.get("lop", "").strip()
    all_classes = sorted(list(set(s["lop"] for s in STUDENTS.values())))
    
    filter_links = [f'<a href="{url_for("student_list")}">Tất cả</a>']
    for c in all_classes:
        filter_links.append(f'<a href="{url_for("student_list", lop=c)}">{escape(c)}</a>')
        
    filtered_students = [
        student_summary(mssv) for mssv, info in STUDENTS.items()
        if not lop_filter or info["lop"].lower() == lop_filter.lower()
    ]
    
    if not filtered_students:
        content = "<p>Không có sinh viên phù hợp.</p>"
    else:
        rows = []
        for s in filtered_students:
            avg_str = f"{s['average']:.2f}" if s["average"] is not None else "-"
            rows.append(f"""
            <tr>
                <td><a href="{url_for('student_detail', mssv=s['mssv'])}">{escape(s['mssv'])}</a></td>
                <td>{escape(s['name'])}</td>
                <td>{escape(s['lop'])}</td>
                <td>{avg_str}</td>
                <td>{escape(s['rank'])}</td>
            </tr>""")
        content = f"<table border='1'><thead><tr><th>MSSV</th><th>Họ tên</th><th>Lớp</th><th>Điểm TB</th><th>Xếp loại</th></tr></thead><tbody>{''.join(rows)}</tbody></table>"
        
    body = f"<h1>Danh sách sinh viên</h1><p>Thanh lọc: {' | '.join(filter_links)}</p>{content}"
    return layout("Danh sách sinh viên", body)

@app.route("/students/<mssv>")
def student_detail(mssv):
    if mssv not in STUDENTS:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")
    s = student_summary(mssv)
    avg_str = f"{s['average']:.2f}" if s["average"] is not None else "-"
    
    scores_table = "<p>Chưa có điểm học phần nào.</p>"
    if s["scores"]:
        rows = "".join([f"<tr><td>{escape(c)}</td><td>{v}</td></tr>" for c, v in s["scores"].items()])
        scores_table = f"<table border='1'><tr><th>Học phần</th><th>Điểm</th></tr>{rows}</table>"
        
    body = f"""
    <h1>Thông tin sinh viên: {escape(s['name'])}</h1>
    <p><strong>MSSV:</strong> {escape(s['mssv'])}</p>
    <p><strong>Lớp:</strong> <a href="{url_for('student_list', lop=s['lop'])}">{escape(s['lop'])}</a></p>
    <p><strong>Điểm TB:</strong> {avg_str}</p>
    <p><strong>Xếp loại:</strong> {escape(s['rank'])}</p>
    <h3>Bảng điểm chi tiết</h3>{scores_table}
    <p><a href="{url_for('export_csv', mssv=mssv)}">Tải bảng điểm (CSV)</a> | Link rút gọn: <code>{url_for('short_student_link', mssv=mssv)}</code></p>
    """
    return layout(f"Chi tiết {s['mssv']}", body)

@app.route("/sv/<mssv>")
def short_student_link(mssv):
    return redirect(url_for("student_detail", mssv=mssv), code=301)

@app.route("/students/<mssv>/export")
def export_csv(mssv):
    if mssv not in STUDENTS:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")
    lines = ["hoc_phan,diem"] + [f"{c},{v}" for c, v in STUDENTS[mssv]["scores"].items()]
    res = make_response("\n".join(lines))
    res.headers["Content-Type"] = "text/csv; charset=utf-8"
    res.headers["Content-Disposition"] = f"attachment; filename=diem_{mssv}.csv"
    return res

@app.route("/search")
def search():
    q = request.args.get("q", "").strip()
    results = [
        student_summary(mssv) for mssv, info in STUDENTS.items()
        if q and (q.lower() in info["name"].lower() or q.lower() in mssv.lower())
    ] if q else []
    
    escaped_q = escape(q)
    header = f"<p>Tìm thấy {len(results)} kết quả cho &quot;{escaped_q}&quot;</p>" if q else ""
    items = "".join([f'<li><a href="{url_for("student_detail", mssv=s["mssv"])}">{escape(s["mssv"])} - {escape(s["name"])} ({escape(s["lop"])})</a></li>' for s in results])
    list_html = f"<ul>{items}</ul>" if results else ("<p>Không tìm thấy kết quả phù hợp.</p>" if q else "")
    
    body = f"""
    <h1>Tìm kiếm sinh viên</h1>
    <form method="GET"><input type="text" name="q" value="{escaped_q}"><button type="submit">Tìm</button></form>
    {header}{list_html}
    """
    return layout("Tìm kiếm", body)

@app.route("/api/students")
def api_students():
    lop_param = request.args.get("lop")
    min_avg = None
    if "min_avg" in request.args:
        try:
            min_avg = float(request.args["min_avg"])
        except ValueError:
            return jsonify({"error": "Tham số min_avg phải là số thực."}), 400

    results = []
    for mssv in STUDENTS:
        s = student_summary(mssv)
        if lop_param and s["lop"].lower() != lop_param.strip().lower():
            continue
        if min_avg is not None and (s["average"] is None or s["average"] < min_avg):
            continue
        results.append(s)
    return jsonify(results)

@app.route("/api/students/<mssv>")
def api_student_detail(mssv):
    if mssv not in STUDENTS:
        return jsonify({"error": "MSSV không tồn tại."}), 404
    return jsonify(student_summary(mssv))

@app.route("/api/students/<mssv>/scores/<course>", methods=["GET", "PUT", "DELETE"])
def api_manage_course_score(mssv, course):
    if mssv not in STUDENTS:
        return jsonify({"error": "MSSV không tồn tại."}), 404

    course_code = course.upper()
    student = STUDENTS[mssv]

    if request.method == "GET":
        if course_code not in student["scores"]:
            return jsonify({"error": "Học phần chưa có điểm."}), 404
        return jsonify({"mssv": mssv, "course": course_code, "score": student["scores"][course_code]})

    elif request.method == "PUT":
        score_param = request.args.get("score")
        if score_param is None:
            return jsonify({"error": "Thiếu tham số score."}), 400
        try:
            score_val = float(score_param)
        except ValueError:
            return jsonify({"error": "Tham số score phải là số."}), 400
        if not (0 <= score_val <= 10):
            return jsonify({"error": "Điểm phải nằm trong khoảng [0, 10]."}), 400

        is_new = course_code not in student["scores"]
        student["scores"][course_code] = score_val
        data = {"mssv": mssv, "course": course_code, "score": score_val, "average": student_summary(mssv)["average"]}

        if is_new:
            res = make_response(jsonify(data), 201)
            res.headers["Location"] = url_for("api_manage_course_score", mssv=mssv, course=course_code)
            return res
        return jsonify(data), 200

    elif request.method == "DELETE":
        if course_code not in student["scores"]:
            return jsonify({"error": "Học phần chưa có điểm."}), 404
        del student["scores"][course_code]
        return "", 204

@app.route("/api/students/<mssv>/scores/<course>", methods=["POST"])
def api_course_score_post(mssv, course):
    return jsonify({"error": "Phương thức POST không được hỗ trợ."}), 405

@app.errorhandler(400)
@app.errorhandler(404)
@app.errorhandler(405)
def handle_error(error):
    status_code = getattr(error, "code", 500)
    titles = {400: "Dữ liệu không hợp lệ", 404: "Không tìm thấy", 405: "Phương thức không được hỗ trợ"}
    title = titles.get(status_code, "Lỗi hệ thống")
    description = getattr(error, "description", str(error))

    if request.path.startswith("/api/"):
        return jsonify({"error": title, "detail": description}), status_code

    body = f"<h1>{status_code} - {escape(title)}</h1><p>{escape(description)}</p><p><a href='{url_for('home')}'>Quay lại trang chủ</a></p>"
    return layout(f"Lỗi {status_code}", body), status_code
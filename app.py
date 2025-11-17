from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import joblib
import os
import uuid

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
db = SQLAlchemy(app)

# === MÔ HÌNH CSDL ===
class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    level = db.Column(db.String(50))
    job = db.Column(db.String(20))
    n_company = db.Column(db.String(20))
    project = db.Column(db.String(20))
    cv_filename = db.Column(db.String(200))
    result = db.Column(db.String(50))

# === KIỂM TRA THƯ MỤC UPLOAD ===
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# === NẠP MÔ HÌNH HỌC MÁY ===
model_path = 'model_id3.pkl'
if not os.path.exists(model_path):
    raise FileNotFoundError("⚠️ Không tìm thấy 'model_id3.pkl' – hãy chạy 'model_train.py' trước!")
model = joblib.load(model_path)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # --- Nhận dữ liệu từ form ---
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        level = request.form['level']
        job = request.form['job']
        n_company = int(request.form['n_company'])
        project = int(request.form['project'])

        # --- Xử lý file CV ---
        cv_file = request.files['cv']
        cv_filename = None
        if cv_file and cv_file.filename != '':
            ext = cv_file.filename.split('.')[-1]
            unique_name = f"{uuid.uuid4()}.{ext}"
            cv_file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_name))
            cv_filename = unique_name

        # === CHUẨN HÓA DỮ LIỆU ===
        mapping = {
            'Đại học': 2,
            'Cao đẳng': 1,
            'Trung tâm tin học': 0,
            'có': 1,
            'không': 0
        }

        n_company_bin = 1 if n_company > 0 else 0
        project_bin = 1 if project > 0 else 0

        df = pd.DataFrame({
            'Level': [mapping[level]],
            'Job': [mapping[job]],
            'N_Company': [n_company_bin],
            'Project': [project_bin]
        })

        # === DỰ ĐOÁN ===
        result = model.predict(df)[0]
        result_text = 'Đủ điều kiện' if result == 1 or result == 'có' else 'Không đủ điều kiện'

        # === LƯU VÀO DATABASE ===
        candidate = Candidate(
            name=name,
            email=email,
            phone=phone,
            level=level,
            job=job,
            n_company=str(n_company),
            project=str(project),
            cv_filename=cv_filename,
            result=result_text
        )
        db.session.add(candidate)
        db.session.commit()

    except Exception as e:
        result_text = f"Lỗi xử lý dữ liệu: {e}"

    return render_template('result.html', name=name, result=result_text)

# === TRANG ADMIN ===
@app.route('/admin')
def admin():
    candidates = Candidate.query.all()
    return render_template('admin.html', candidates=candidates)

# === XEM FILE CV ===
@app.route('/uploads/<filename>')
def view_cv(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# === XÓA ỨNG VIÊN ===
@app.route('/delete/<int:id>')
def delete_candidate(id):
    candidate = Candidate.query.get(id)
    if candidate:
        if candidate.cv_filename:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], candidate.cv_filename)
            if os.path.exists(file_path):
                os.remove(file_path)
        db.session.delete(candidate)
        db.session.commit()
    return redirect(url_for('admin'))

# === TÌM KIẾM ỨNG VIÊN ===
@app.route('/search', methods=['GET'])
def search():
    keyword = request.args.get('q', '')
    results = Candidate.query.filter(
        (Candidate.name.contains(keyword)) | (Candidate.email.contains(keyword))
    ).all()
    return render_template('admin.html', candidates=results, keyword=keyword)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

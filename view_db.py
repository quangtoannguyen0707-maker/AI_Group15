from app import app, db, Candidate
from tabulate import tabulate

with app.app_context():
    candidates = Candidate.query.all()
    if not candidates:
        print("⚠️ Chưa có ứng viên nào trong database.")
    else:
        table = []
        for c in candidates:
            table.append([c.id, c.name, c.email, c.phone, c.level, c.job, c.n_company, c.project, c.result])
        print(tabulate(table, headers=["ID", "Họ Tên", "Email", "SĐT", "Trình độ", "Kinh nghiệm", "Số Cty", "Dự án", "Kết quả"], tablefmt="fancy_grid"))

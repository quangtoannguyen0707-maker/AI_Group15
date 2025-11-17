import pandas as pd
from sklearn.tree import DecisionTreeClassifier
import joblib
from sklearn import tree
import matplotlib.pyplot as plt

# === ĐỌC DỮ LIỆU ===
data = pd.read_csv(r"D:\Học tập\15-Trí Tuệ Nhân Tạo\data\data_v2_train.csv.txt")

# === GIỮ CÁC CỘT CẦN THIẾT ===
data = data[['Level', 'Job', 'N_Company', 'Project', 'Result']]

# === CHUẨN HÓA DỮ LIỆU ===
mapping = {
    'Đại học': 2,
    'Cao đẳng': 1,
    'Trung tâm tin học': 0,
    'có': 1,
    'không': 0
}
data = data.replace(mapping)

# === CHUYỂN ĐỔI SỐ LIỆU THÀNH CÓ / KHÔNG ===
# Nếu số công ty hoặc dự án > 0 thì = 1 (có), ngược lại = 0 (không)
data['N_Company'] = data['N_Company'].apply(lambda x: 1 if x > 0 else 0)
data['Project'] = data['Project'].apply(lambda x: 1 if x > 0 else 0)

# === TÁCH X và y ===
X = data[['Level', 'Job', 'N_Company', 'Project']]
y = data['Result']

# === HUẤN LUYỆN MÔ HÌNH ===
model = DecisionTreeClassifier(criterion='entropy', random_state=0)
model.fit(X, y)

# === LƯU MÔ HÌNH ===
joblib.dump(model, 'model_id3.pkl')
print("✅ Mô hình ID3 đã được huấn luyện và lưu thành công thành file 'model_id3.pkl'")

# === VẼ CÂY QUYẾT ĐỊNH ===
plt.figure(figsize=(16, 8))
tree.plot_tree(
    model,
    feature_names=['Level', 'Job', 'N_Company', 'Project'],
    class_names=['Không đủ điều kiện', 'Đủ điều kiện'],
    filled=True,
    rounded=True,
    fontsize=10
)
plt.show()

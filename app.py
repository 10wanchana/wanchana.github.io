from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # จำเป็นสำหรับการใช้ session

# การตั้งค่าการเชื่อมต่อกับฐานข้อมูล
db_config = {
    'user': 'root',       # เปลี่ยนให้ตรงกับผู้ใช้งาน MySQL ของคุณ
    'password': '',       # หากมีรหัสผ่าน MySQL ให้ใส่ที่นี่
    'host': 'localhost',
    'database': 'flask_db'
}

# สร้างการเชื่อมต่อกับฐานข้อมูล
def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    return conn

# เส้นทางหลัก (Home route)
#@app.route('/')
#def home():
    #return "Welcome to the Student API!"
@app.route('/')
def index():
    return render_template('index.html')  # หรือไฟล์ HTML ที่ถูกต้อง

# สร้างข้อมูล (Create)
@app.route('/student', methods=['POST'])
def add_student():
    try:
        name = request.json['name']
        email = request.json['email']
        phone = request.json['phone']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO students (name, email, phone) 
            VALUES (%s, %s, %s)
        ''', (name, email, phone))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Student added successfully!'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
# ฟังก์ชันสำหรับการดูรายละเอียดผู้ใช้
@app.route('/admin/view_user/<int:id>', methods=['GET'])
def admin_view_user(id):
    if 'logged_in' in session:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM students WHERE id = %s', (id,))
        user = cursor.fetchone()
        conn.close()

        if user:
            return render_template('admin_view_user.html', user=user)
        else:
            return "User not found", 404
    else:
        return redirect(url_for('login'))
# อ่านข้อมูล (Read) - อ่านทั้งหมด
@app.route('/students', methods=['GET'])
def get_students():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM students')
        rows = cursor.fetchall()
        conn.close()

        students = []
        for row in rows:
            students.append({
                'id': row[0],
                'name': row[1],
                'email': row[2],
                'phone': row[3]
            })

        return jsonify(students), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
# ฟังก์ชันสำหรับการค้นหาผู้ใช้
@app.route('/admin/search', methods=['GET', 'POST'])
def admin_search_user():
    if 'logged_in' in session:
        search_query = request.form['search_query'] if request.method == 'POST' else ""
        
        conn = get_db_connection()
        cursor = conn.cursor()

        # ค้นหาผู้ใช้ด้วยชื่อหรือเบอร์โทร
        query = "SELECT * FROM students WHERE name LIKE %s OR phone LIKE %s"
        cursor.execute(query, ('%' + search_query + '%', '%' + search_query + '%'))
        users = cursor.fetchall()

        conn.close()
        return render_template('admin_users.html', users=users, search_query=search_query)
    else:
        return redirect(url_for('login'))
# อ่านข้อมูล (Read) - อ่านจาก ID
@app.route('/student/<int:id>', methods=['GET'])
def get_student(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM students WHERE id = %s', (id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            student = {
                'id': row[0],
                'name': row[1],
                'email': row[2],
                'phone': row[3]
            }
            return jsonify(student), 200
        else:
            return jsonify({'message': 'Student not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 400
    

# อัปเดตข้อมูล (Update)
@app.route('/student/<int:id>', methods=['PUT'])
def update_student(id):
    try:
        name = request.json['name']
        email = request.json['email']
        phone = request.json['phone']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE students 
            SET name = %s, email = %s, phone = %s 
            WHERE id = %s
        ''', (name, email, phone, id))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Student updated successfully!'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
# ลบข้อมูล (Delete)
@app.route('/student/<int:id>', methods=['DELETE'])
def delete_student(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM students WHERE id = %s', (id,))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Student deleted successfully!'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
# ฟังก์ชันสำหรับแก้ไขผู้ใช้
@app.route('/admin/edit_user/<int:id>', methods=['GET', 'POST'])
def admin_edit_user(id):
    if 'logged_in' in session:
        conn = get_db_connection()
        cursor = conn.cursor()

        if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            phone = request.form['phone']

            cursor.execute('''
                UPDATE students 
                SET name = %s, email = %s, phone = %s 
                WHERE id = %s
            ''', (name, email, phone, id))
            conn.commit()
            conn.close()

            return redirect(url_for('admin_users'))
        else:
            cursor.execute('SELECT * FROM students WHERE id = %s', (id,))
            user = cursor.fetchone()
            conn.close()

            if user:
                return render_template('admin_edit_user.html', user=user)
            else:
                return "User not found", 404
    else:
        return redirect(url_for('login'))
# ฟังก์ชันสำหรับเพิ่มผู้ใช้ใหม่
@app.route('/admin/add_user', methods=['GET', 'POST'])
def admin_add_user():
    if 'logged_in' in session:
        if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            phone = request.form['phone']

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO students (name, email, phone) 
                VALUES (%s, %s, %s)
            ''', (name, email, phone))
            conn.commit()
            conn.close()

            return redirect(url_for('admin_users'))

        return render_template('admin_add_user.html')
    else:
        return redirect(url_for('login'))
# หน้าแดชบอร์ดแอดมิน
@app.route('/admin')
def admin_dashboard():
    return render_template('admin_dashboard.html')

# แสดงรายการผู้ใช้งานทั้งหมดในระบบ (สำหรับแอดมิน)
@app.route('/admin/users')
def admin_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students')  # แสดงรายการนักเรียนทั้งหมด
    users = cursor.fetchall()
    conn.close()
    return render_template('admin_users.html', users=users)

# ลบผู้ใช้งาน (สำหรับแอดมิน)
@app.route('/admin/delete_user/<int:id>', methods=['POST'])
def admin_delete_user(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM students WHERE id = %s', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_users'))

# ระบบล็อกอิน
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # ตรวจสอบการล็อกอิน (ตัวอย่างแบบง่าย ๆ)
        if username == 'admin' and password == 'admin123':
            session['logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return "Invalid credentials"
    return render_template('login.html')

# ระบบล็อกเอาต์
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# ตรวจสอบการล็อกอินก่อนเข้าถึงเส้นทางต่าง ๆ
@app.before_request
def require_login():
    allowed_routes = ['login']
    if request.endpoint not in allowed_routes and 'logged_in' not in session:
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5002)  # เปลี่ยนพอร์ตเป็น 5001 หรือพอร์ตอื่นที่คุณต้องการ
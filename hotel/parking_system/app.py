from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime, timedelta
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'


# 初始化数据库
def init_db():
    if not os.path.exists('parking.db'):
        conn = sqlite3.connect('parking.db')
        c = conn.cursor()

        # 创建车辆信息表
        c.execute('''CREATE TABLE IF NOT EXISTS vehicles
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      plate_number TEXT UNIQUE,
                      owner_name TEXT,
                      phone TEXT,
                      vehicle_type TEXT,
                      register_time TEXT)''')

        # 创建停车记录表
        c.execute('''CREATE TABLE IF NOT EXISTS parking_records
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      plate_number TEXT,
                      entry_time TEXT,
                      exit_time TEXT,
                      duration INTEGER,
                      fee REAL,
                      paid INTEGER DEFAULT 0)''')

        conn.commit()
        conn.close()


init_db()


# 首页
@app.route('/')
def index():
    return render_template('index.html')


# 车辆登记
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        plate_number = request.form['plate_number']
        owner_name = request.form['owner_name']
        phone = request.form['phone']
        vehicle_type = request.form['vehicle_type']
        register_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        try:
            conn = sqlite3.connect('parking.db')
            c = conn.cursor()
            c.execute(
                "INSERT INTO vehicles (plate_number, owner_name, phone, vehicle_type, register_time) VALUES (?, ?, ?, ?, ?)",
                (plate_number, owner_name, phone, vehicle_type, register_time))
            conn.commit()
            flash('车辆登记成功!', 'success')
            return redirect(url_for('index'))
        except sqlite3.IntegrityError:
            flash('该车牌号已存在!', 'danger')
        finally:
            conn.close()

    return render_template('register.html')


# 车辆入场
@app.route('/entry', methods=['POST'])
def entry():
    plate_number = request.form['plate_number']
    entry_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    conn = sqlite3.connect('parking.db')
    c = conn.cursor()

    # 检查车辆是否已登记
    c.execute("SELECT * FROM vehicles WHERE plate_number=?", (plate_number,))
    vehicle = c.fetchone()

    if not vehicle:
        flash('该车辆未登记，请先登记!', 'danger')
        return redirect(url_for('register'))

    # 检查是否有未完成的停车记录
    c.execute("SELECT * FROM parking_records WHERE plate_number=? AND exit_time IS NULL", (plate_number,))
    existing_record = c.fetchone()

    if existing_record:
        flash('该车辆已在停车场内!', 'danger')
        return redirect(url_for('index'))

    # 创建新的停车记录
    c.execute("INSERT INTO parking_records (plate_number, entry_time) VALUES (?, ?)",
              (plate_number, entry_time))
    conn.commit()
    conn.close()

    flash(f'车辆 {plate_number} 入场成功!', 'success')
    return redirect(url_for('index'))


# 车辆出场
@app.route('/exit', methods=['POST'])
def exit():
    plate_number = request.form['plate_number']
    exit_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    conn = sqlite3.connect('parking.db')
    c = conn.cursor()

    # 获取未完成的停车记录
    c.execute("SELECT * FROM parking_records WHERE plate_number=? AND exit_time IS NULL", (plate_number,))
    record = c.fetchone()

    if not record:
        flash('没有找到该车辆的入场记录!', 'danger')
        return redirect(url_for('index'))

    # 计算停车时长和费用
    entry_time = datetime.strptime(record[2], '%Y-%m-%d %H:%M:%S')
    duration = (datetime.now() - entry_time).seconds // 60  # 分钟数

    # 简单计费规则：每小时5元，不足1小时按1小时计算
    hours = duration // 60
    if duration % 60 > 0:
        hours += 1
    fee = hours * 5

    # 更新停车记录
    c.execute("UPDATE parking_records SET exit_time=?, duration=?, fee=? WHERE id=?",
              (exit_time, duration, fee, record[0]))
    conn.commit()
    conn.close()

    flash(f'车辆 {plate_number} 出场成功，停车时长: {duration}分钟，应缴费: {fee}元', 'success')
    return redirect(url_for('record', plate_number=plate_number))


# 停车记录
@app.route('/record/<plate_number>')
def record(plate_number):
    conn = sqlite3.connect('parking.db')
    c = conn.cursor()

    # 获取车辆信息
    c.execute("SELECT * FROM vehicles WHERE plate_number=?", (plate_number,))
    vehicle = c.fetchone()

    # 获取停车记录
    c.execute("SELECT * FROM parking_records WHERE plate_number=? ORDER BY entry_time DESC", (plate_number,))
    records = c.fetchall()

    conn.close()

    return render_template('record.html', vehicle=vehicle, records=records)


# 缴费
@app.route('/payment/<int:record_id>', methods=['GET', 'POST'])
def payment(record_id):
    conn = sqlite3.connect('parking.db')
    c = conn.cursor()

    if request.method == 'POST':
        # 更新缴费状态
        c.execute("UPDATE parking_records SET paid=1 WHERE id=?", (record_id,))
        conn.commit()
        conn.close()
        flash('缴费成功!', 'success')
        return redirect(url_for('index'))

    # 获取停车记录
    c.execute("SELECT * FROM parking_records WHERE id=?", (record_id,))
    record = c.fetchone()

    # 获取车辆信息
    c.execute("SELECT * FROM vehicles WHERE plate_number=?", (record[1],))
    vehicle = c.fetchone()

    conn.close()

    return render_template('payment.html', vehicle=vehicle, record=record)


# 查询
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        plate_number = request.form['plate_number']
        return redirect(url_for('record', plate_number=plate_number))

    return render_template('search.html')


if __name__ == '__main__':
    app.run(debug=True)
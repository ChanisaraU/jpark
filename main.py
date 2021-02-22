from flask_paginate import Pagination, get_page_parameter
from flask_restful import Api,Resource, abort ,reqparse
from flask_sqlalchemy import SQLAlchemy, Model
from openGate import control_Gate
from member import member
from member_two import member_two
from current import *
from receipt import *
import sqlalchemy
import json
from current import *
from flask import Flask, jsonify, request, render_template, Response, redirect, url_for, session, Blueprint, make_response
from app import app
from db_config import mysql  # import sql
import cv2
import time
from datetime import datetime ,date
import socket
import io
import xlwt
import pdfkit


path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

now = datetime.now() # current date and time
year = now.strftime("%Y")
year_two = now.strftime("%y")
month = now.strftime("%m")
day = now.strftime("%d")
time = now.strftime("%H:%M:%S")
date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
today = datetime.today()
today_date = date.today()
time_h = now.strftime("%H:%M")

def find_camera(id):
    cameras = ['rtsp://admin:ap123456789@172.16.6.4/profile3',
               'rtsp://admin:ap123456789@172.16.6.5/profile3', 'rtsp://admin:ap123456789@172.16.6.3/profile3']
    return cameras[int(id)]

# camera = cv2.VideoCapture('rtsp://admin:Jpark*2020*@172.20.1.138')  # use 0 for web camera
#  for cctv camera use rtsp://username:password@ip_address:554/user=username_password='password'_channel=channel_number_stream=0.sdp' instead of camera


def gen_frames(id):  # generate frame by frame from camera
    cam = find_camera(id)
    cap = cv2.VideoCapture(cam)

    while True:
        # Capture frame-by-frame
        success, frame = cap.read()  # read the camera frame
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            # concat frame one by one and show result
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed/<string:id>/', methods=["GET"])
def video_feed(id):
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen_frames(id), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/monitor-in')  # checkin
def monitorin():
    cursor = mysql.connection.cursor()
    sql = 'select * from test_log where gate = 0'
    cursor.execute(sql)
    info = cursor.fetchone()
    car_out = info[2]  # license_plate

    cursor3 = mysql.connection.cursor()
    sql3 = 'select * from member where license_plate = %s'
    val = (car_out,)
    cursor3.execute(sql3, val)
    member = cursor3.fetchone()

    if member:
        mem_type = member[2]
        expiry_date = member[11]
        licenseP = info[2]
        time_in = str(info[8])+" "+str(info[7])
        dt = info[15]
        amount = info[26]

    else:
        mem_type = "visitors"
        expiry_date = "-"
        licenseP = " "
        time_in = str(info[8])
        date_in = str(info[7])

    return render_template('monitor-in.html', mem_type=mem_type, expiry_date=expiry_date, licenseP=licenseP, time_in=time_in, car_out=car_out)


@app.route('/monitor-out')  # checkout
def monitorout():
    cursor = mysql.connection.cursor()
    sql = 'select * from test_log where gate = 0'
    cursor.execute(sql)
    info = cursor.fetchone()
    car_out = info[2]  # license_plate

    cursor3 = mysql.connection.cursor()
    sql3 = 'select * from member where license_plate = %s'
    val = (car_out,)
    cursor3.execute(sql3, val)
    member1 = cursor3.fetchone()

    price ,excluding_vat ,vat = member()
    if member1:
        mem_type = member1[2]
        expiry_date = member1[11]
        licenseP = info[2]
        time_in = str(info[8])+" "+str(info[7])
        dt = info[15]
        amount = info[26]
        time_in = str(info[7])
        time_out = str(info[14])
        date_in = info[8]
        date_out = info[15]
        dateIn = str(date_in.day) + "/" + str(date_in.month) + \
            "/" + str(date_in.year)
        dateOut = str(date_out.day) + "/" + \
            str(date_out.month) + "/" + str(date_out.year)

    else:
        mem_type = "visitors"
        expiry_date = "-"
        licenseP = " "
        time_in = str(info[7])
        time_out = str(info[14])
        date_in = info[8]
        date_out = info[15]
        dateIn = str(date_in.day) + "/" + str(date_in.month) + \
            "/" + str(date_in.year)
        dateOut = str(date_out.day) + "/" + \
            str(date_out.month) + "/" + str(date_out.year)

    return render_template('monitor-out.html', price=price, time_out=time_out, dateOut=dateOut, car_out=car_out, dateIn=dateIn, time_in=time_in, mem_type=mem_type, expiry_date=expiry_date)


@app.route('/', methods=['GET', 'POST'])  # ระบบ Login
def login():
    error = None
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute(
            'select * from user_admin where user_name = %s AND pass_word = %s', (username, password))
        account = cursor.fetchone()

        if account:
            session["roles"] = account[2]
            now = datetime.now()
            session['username'] = request.form['username']
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            login_date = now.strftime('%Y-%m-%d %H:%M:%S')
            sql = "INSERT INTO login_history(user_name,user_ip,system,login_date,status) VALUES (%s, %s, %s, %s, %s)"
            val = (account[9], ip_address,
                   "ระบบลานจอดรถสวนรถไฟ", login_date, "signed in")
            cursor.execute(sql, val)
            mysql.connection.commit()
            cursor.close()
            
            return redirect(url_for('transaction') )
        else:
            sql = 'select * from user_admin where user_name = %s'
            cursor.execute(sql, (username,))
            account = cursor.fetchone()
            if account:
                error = 'Incorrect password!'
            else:
                error = 'Incorrect username!'

    return render_template('login.html', error=error)


@app.route('/home')  # หน้า Dashboard
def dashboard():
    if session['username'] != " ":
        mycursor = mysql.connection.cursor()
        query = "select * from parking"
        mycursor.execute(query)
        result = mycursor.fetchall()
        total_car = result[0][2]

    if total_car < 500:
        diff = 500 - total_car
        colored = {'color': 'green'}
    else:
        diff = "FULL"
        colored = {'color': 'red'}
    return render_template('home.html', diff=diff, colored=colored)


@app.route("/livesearch", methods=["POST", "GET"])
def livesearch():
    if request.method == 'POST':
        searchbox = request.form.get("text")
        cursor = mysql.connection.cursor()
        # This is just example query , you should replace field names with yours
        query = "select * from member where first_name LIKE '{}%' order by insert_date".format(
            searchbox)
        cursor.execute(query)
        result = cursor.fetchall()
        return jsonify(result)
    else:
        cursor2 = mysql.connection.cursor()
        query2 = "select * from parking_log order by time_in DESC,date_in DESC"
        cursor2.execute(query2)
        data = cursor2.fetchall()
        sql = "INSERT INTO lately_comein(id,license_plate,province,car_type,img_license_plate_in,time_in,date_in,img_license_plate_out) VALUES (%s, %s, %s, %s, %s, %s, %s,%s)"
        val = (data[0][0], data[0][2], data[0][3], data[0][5],
               data[0][6], data[0][7], data[0][8], data[0][13])
        mycursor.execute(sql, val)
        mysql.connection.commit()
        mycursor.close()
        return 'success'

@app.route('/showled')  # แสดงจำนวนรถที่ว่าง
def showled():
    if session['username'] != " ":
        mycursor = mysql.connection.cursor()
        query = "select COUNT(*) from parking_log where status='0' AND date_in=%s"
        val = (today_date,)
        mycursor.execute(query, val)
        result = mycursor.fetchall()
        # print(result[0][0]) จำนวนรถที่มีสถานะเป็น 0 (จอดอยู่)
        total_car_status0 = result[0][0]

    if total_car_status0  < 1000:
        diff = 1000 - total_car_status0
        colored = {'color': 'green'}
    else:
        diff = "FULL"
        colored = {'color': 'red'}
    return render_template('showled.html',diff=diff, colored=colored) 


@app.route('/car-in')  # ข้อมูลรถเข้าลานจอด
def car_in():
    if session['username'] != " ":
        mycursor = mysql.connection.cursor()
        query = "select COUNT(*) from parking_log where status='0' AND date_in=%s"
        val = (today_date,)
        mycursor.execute(query,val)
        result = mycursor.fetchall()
        # print(result[0][0]) จำนวนรถที่มีสถานะเป็น 0 (จอดอยู่)
        total_car_status0 = result[0][0]
        total_car = 1000-total_car_status0 
        return render_template('car-in.html',total_car_status0=total_car_status0,total_car=total_car)


@app.route('/car-out1', methods=["POST"])
def current():
    cursor = mysql.connection.cursor()
    query = "select COUNT(id) from receipt where date = %s ORDER BY id DESC LIMIT 1"
    val = (today_date,)
    cursor.execute(query, val)
    result = cursor.fetchone()
    count_id = int(result[0])+1
    date = today_date
    count_id = '{:06d}'.format(count_id)
    no = year_two+month+day

    TAX_ID = '0735541000291'
    POS_ID = "Ps02020-01"
    user = session['username']
    cashier_box = "exit-1"
    today = datetime.today()
    receipt_no = 'SRTVBJP'+no+count_id

    discount = request.form.get("discount")  # คูปอง
    fines = request.form.get("fines")  # ค่าปรับ
    receieve = request.form.get("receieve")  # เงินที่ได้รับ
    changes = request.form.get("changes")  # เงินทอน
    gate = request.form.get("ID") #id 
    license_plate = request.form.get("license")
    time_in = request.form.get("time_in")
    time_out = request.form.get("time_out")
    total_time = request.form.get("time_total")
    amount = request.form.get("amount")
    
    cal_discount(discount, gate)
    cal_fines(fines, gate)
    cal_receieve(receieve,gate)
    cal_changes(changes,gate)
   
    record_receipt(TAX_ID, POS_ID, today, receipt_no, cashier_box, user,date,license_plate,discount ,fines ,changes ,receieve,time_in, time_out,total_time,amount)

    return maindown()


@app.route('/car-out2', methods=["POST"])
def current2():
    cursor = mysql.connection.cursor()
    query = "select COUNT(id) from receipt where date = %s ORDER BY id DESC LIMIT 1"
    val = (today_date,)
    cursor.execute(query, val)
    result = cursor.fetchone()
    count_id = int(result[0])+1
    date = today_date
    count_id = '{:06d}'.format(count_id)
    no = year_two+month+day

    TAX_ID = '0735541000291'
    POS_ID = "Ps02020-02"
    user = session['username']
    cashier_box = "exit-2"
    today = datetime.today()
    receipt_no = 'SRTVBJP'+no+count_id

    discount = request.form.get("discount")  # คูปอง
    fines = request.form.get("fines")  # ค่าปรับ
    receieve = request.form.get("receieve")  # เงินที่ได้รับ
    changes = request.form.get("changes")  # เงินทอน
    gate = request.form.get("ID") #id 
    license_plate = request.form.get("license")
    time_in = request.form.get("time_in")
    time_out = request.form.get("time_out")
    total_time = request.form.get("time_total")
    
    cal_discount(discount, gate)
    cal_fines(fines, gate)
    cal_receieve(receieve,gate)
    cal_changes(changes,gate)
   
    record_receipt(TAX_ID, POS_ID, today, receipt_no, cashier_box, user,date,license_plate,discount ,fines ,changes ,receieve,time_in, time_out,total_time)
    
    return maindown_two()


@app.route('/car-out1', methods=["GET"])  # ข้อมูลรถออกลานจอด
def maindown():
    if session['username'] != " ":
        mycursor = mysql.connection.cursor()
        query = "select COUNT(*) from parking_log where status='0' AND date_in=%s"
        val = (today_date,)
        mycursor.execute(query,val)
        result = mycursor.fetchall()
        # print(result[0][0]) จำนวนรถที่มีสถานะเป็น 0 (จอดอยู่)
        total_car_status0 = result[0][0]
        total_car = 1000-total_car_status0 
            
    return render_template('car-out1.html',total_car_status0=total_car_status0,total_car=total_car)


@app.route('/car-out2', methods=["GET"])  # ข้อมูลรถออกลานจอด
def maindown_two():
    if session['username'] != " ":
        mycursor = mysql.connection.cursor()
        query = "select COUNT(*) from parking_log where status='0' AND date_in=%s"
        val = (today_date,)
        mycursor.execute(query,val)
        result = mycursor.fetchall()
        # print(result[0][0]) จำนวนรถที่มีสถานะเป็น 0 (จอดอยู่)
        total_car_status0 = result[0][0]
        total_car = 1000-total_car_status0 
    return render_template('car-out2.html',total_car_status0=total_car_status0,total_car=total_car)


report_header_definition = {
    "": {
        "api": "",
        "title": "",
        "header": []
    },
    "car": {
        "api": "/report/table-car/datatable",
        "title": ["รายงานการเข้าออกของรถ"],
        "header": [
            "ลำดับ",
            "ประเภท",
            "ทะเบียนรถ",
            "เวลาเข้า",
            "เจ้าหน้าที่ขาออก",
            "เวลาออก",
            "ชม.จอด",
            "ชม.โปรโมชั่น",
            "ชม.ลด",
            "ชม.จ่าย",
            "ค่าปรับบัตรหาย",
            "รายได้",
            "ส่วนลด"
        ]
    },
    "salestax": {
        "api": "/report/table-salestax/datatable",
        "title": ["รายงานภาษีขาย"],
        "header": [
            "ลำดับ",
            "เลขที่ใบกำกับภาษี",
            "หมายเลขบัตร",
            "ทะเบียนรถ",
            "วันที่เข้า",
            "เวลาเข้า",
            "เจ้าหน้าที่ขาออก",
            "ตำแหน่งทำรายการ",
            "วันที่ออก",
            "เวลาออก",
            "ค่าปรับ",
            "ค่าบริการ",
            "ภาษีมูลค่าเพิ่ม",
            "รวม"
        ]
    },
    "outcar": {
        "api": "/report/outcar/datatable",
        "title": ["รายงานรถค้าง"],
        "header": [
            "ลำดับ",
            "ประเภท",
            "ทะเบียนรถ",
            "วันเวลาเข้า"
        ]
    },
    "staff": {
        "api": "/report/table-staff/datatable",
        "title": ["รายงานการทำงานของเจ้าหน้าที่"],
        "header": [
            "ลำดับ",
            "ชื่อเจ้าหน้าที่",
            "เวลาเข้า",
            "เวลาออก",
            "รายได้",
            "ส่วนลด"
        ]
    },
    "member_income": {
        "api": "/report/table_member_income/datatable",
        "title": ["รายงานรายได้จากสมาชิก"],
        "header": [
            "ลำดับ",
            "ชื่อ - นามสกุล",
            "ทะเบียนรถ",
            "เลขที่ใบเสร็จ",
            "วันที่ชำระ",
            "วันหมดอายุ",
            "รายได้",
            "เจ้าหน้าที่"
        ]
    },
        "amount": {
        "api": "/report/table_amount/datatable",
        "title": ["รายงานยอดเงินประจำวัน"],
        "header": [
            "ลำดับ",
            "ประเภทรถ",
            "ทะเบียนรถ",
            "เวลาเข้า",
            "วันที่เข้า",
            "เวลาออก",
            "วันที่ออก",
            "รายได้",
            "ภาษีหลังหัก",
            "ภาษี",
        ]
    },
}


@app.route('/report', methods=['GET', 'POST'])  # รายงาน
def report():
    if session['username'] != " ":
        if request.method == "POST":
            report_list = request.form.get("reports")
            if report_list != None:
                return render_template("report.html", report_list=report_list)

        report_name = request.args.get('reports') #รับค่ามาจาก ตัวเลือกหน้า report id="mySelect" name="reports"
        date_start = request.args.get('date_start')
        date_end = request.args.get('date_end') 
        member_type = request.args.get('member')


        if not report_name:
            report_name = list(report_header_definition.keys())[0]
        table_header = report_header_definition[report_name]['header']
        title = report_header_definition[report_name]['title']
        api = report_header_definition[report_name]['api']

        api_param = "?"
        params = []
        if date_start :
            params.append("date_start=" + date_start) # date_in=2020-10-10
        if date_end:
            params.append("date_end=" + date_end) # date_out=2020-10-10
        if member_type :
            params.append("member=" + member_type)    
            
        api_param += "&".join(params)
    return render_template("report.html", table_header=table_header, api=api, api_param=api_param, title=title)


@app.route('/report-dash')  # รายงาน
def reportdash():
    if session['username'] != " ":
        legend = "Data A"
        cursor = mysql.connection.cursor()
        try:
            cursor.execute("select amount from parking_log")
            rows = cursor.fetchall()
            labels = list()
            i = 0
            for row in rows:
                labels.append(row[i])

            cursor.execute("select date_out from parking_log")
            rows = cursor.fetchall()
            # Convert query to objects of key-value pairs
            values = list()
            i = 0
            for row in rows:
                values.append(row[i])
            mysql.connection.commit()
            cursor.close()

        except:
            print("Error: Unable to fetch items")
        return render_template('report-dash.html', values=values, labels=labels, legend=legend)


@app.route('/transaction', methods=['GET', 'POST'])
def transaction():
    if session['username'] != " ":
        roles = request.args.get('roles', None)
        page = request.args.get(get_page_parameter(), type=int, default=1)
        limit = 5
        offset = page*limit-limit
        cursor = mysql.connection.cursor()
        cursor.execute("select * from parking_log")
        result = cursor.fetchall()
        total = len(result)
        now = datetime.now()
        today = now.strftime('%Y-%m-%d')
        cur = mysql.connection.cursor()
        que = "select * from parking_log where date_in = %s ORDER By time_in DESC,date_in DESC LIMIT %s OFFSET %s"
        cur.execute(que, (today,limit, offset))
        data = cur.fetchall()
        cur.close()

        pagination = Pagination(page=page, per_page=limit,
                                total=total, record_name='transaction', css_framework='bootstrap4')
        return render_template('transaction.html', roles=roles,pagination=pagination, transaction=data, data=[{'in_out': 'เข้า'}, {'in_out': 'ออก'}], type=[{'typecar': 'รถยนต์ส่วนบุคคล'}, {'typecar': 'รถแท๊กซี่'}, {'typecar': 'รถจักรยานยนต์'}])



@app.route('/transaction/json', methods=['GET', 'POST'])
def transaction_json():
    mem_no = request.args.get('mem_no')
    cursor = mysql.connection.cursor()
    sql = "select id, car_type ,license_plate ,province  from parking_log where id = %s"
    val = (mem_no,)
    cursor.execute(sql,val)
    result = cursor.fetchone()

    payload = []
    content = {}
    content = {'id': result[0], 'car_type': result[1], 'license_plate' : result[2], 'province' : result[3]}
    return content


@app.route('/addcar', methods=['GET', 'POST'])  # รายการรถเข้า-ออกสะสม
def addcar():
    now = datetime.now()
    today = now.strftime('%Y-%m-%d')
    cursor = mysql.connection.cursor()
    query = "select * from parking_log where date_in = %s order by time_in DESC,date_in DESC"
    cursor.execute(query, (today,))
    resultt = cursor.fetchall()
    cursor2 = mysql.connection.cursor()
    in_out = request.form.get('comp_select')
    province = request.form.get('province')
    typecar = request.form.get('typecar')
    carregis = request.form.get('carregis')
    timeinout = request.form.get('timeinout')
    motive = request.form.get('motive')
    amountmoney = request.form.get('amountmoney')
    cursor2 = mysql.connection.cursor()
    if in_out == 'เข้า':
        sql = "INSERT INTO parking_log(id,license_plate,province,time_in,car_type) VALUES (%s, %s, %s, %s, %s)"
        val = (in_out, carregis, province, timeinout, typecar)
        cursor2.execute(sql, val)
        mysql.connection.commit()
        cursor2.close()
        
    return transaction()


@app.route('/edit', methods=["POST", "GET"])
def edit():
    
    id = request.values.get('id')
    license_plate = request.values.get('license_plate')
    province = request.values.get('province')
    car_type = request.values.get('car_type')

    cursor2 = mysql.connection.cursor()
    sql = "UPDATE parking_log SET license_plate = %s, province= %s ,car_type= %s WHERE id = %s"
    val = (license_plate, province, car_type, id)
    cursor2.execute(sql, val)
    mysql.connection.commit()
    cursor2.close()
    return transaction()


# Export to Excel :: Transaction
@app.route('/download/report/excel')
def download_report():
    cursor = mysql.connection.cursor()
    query = "select id, code, license_plate, province, car_type, insert_by_in, insert_date_in, cancel, time_total, discount_name, pay_fine, amount, discount, earn, reason from parking_log"
    cursor.execute(query)
    result = cursor.fetchall()

    # Output in bytes
    output = io.BytesIO()
    # Create Workbook Object
    workbook = xlwt.Workbook()
    # Add a sheet
    sh = workbook.add_sheet('Transaction Report')

    # Add headers
    sh.write(0, 0, 'ลำดับ')
    sh.write(0, 1, 'เลขสมาชิก')
    sh.write(0, 2, 'เลขทะเบียนรถ')
    sh.write(0, 3, 'จังหวัด')
    sh.write(0, 4, 'ประเภทรถ')
    sh.write(0, 5, 'ผู้ใช้ระบบขาเข้า')
    sh.write(0, 6, 'วันที่คีย์ข้อมูลเข้าระบบขาเข้า')
    sh.write(0, 7, 'กรณียกเลิกจากระบบ')
    sh.write(0, 8, 'เวลาทั้งหมดที่จอด')
    sh.write(0, 9, 'ชื่อส่วนลด')
    sh.write(0, 10, 'ค่าปรับบัตรหาย')
    sh.write(0, 11, 'ค่าจอดสุทธิ')
    sh.write(0, 12, 'ส่วนลดทั้งหมด')
    sh.write(0, 13, 'จำนวนเงินที่ได้รับ')
    sh.write(0, 14, 'สาเหตุ')

    idx = 0
    for row in result:
        sh.write(idx+1, 0, row[0])
        sh.write(idx+1, 1, row[1])
        sh.write(idx+1, 2, row[2])
        sh.write(idx+1, 3, row[3])
        sh.write(idx+1, 4, row[4])
        sh.write(idx+1, 5, row[5])
        sh.write(idx+1, 6, row[6])
        sh.write(idx+1, 7, row[7])
        sh.write(idx+1, 8, row[8])
        sh.write(idx+1, 9, row[9])
        sh.write(idx+1, 10, row[10])
        sh.write(idx+1, 11, row[11])
        sh.write(idx+1, 12, row[12])
        sh.write(idx+1, 13, row[13])
        sh.write(idx+1, 14, row[14])
        idx += 1
    workbook.save(output)
    output.seek(0)

    return Response(output, mimetype="application/ms-excel", headers={"Content-Disposition": "attachment;filename=transaction_report.xls"})


@app.route('/member-detail', methods=['GET', 'POST'])
def memberdetail():
    if session['username'] != " ":
        # โชว์เฉพาะ Member
        page = request.args.get(get_page_parameter(), type=int, default=1)
        limit = 10
        offset = page*limit-limit
        cursor = mysql.connection.cursor()
        cursor.execute("select * from member where type='Member'")

        result = cursor.fetchall()
        total = len(result)
        cur = mysql.connection.cursor()
        que = "select * from member where type='Member' LIMIT %s OFFSET %s"
        cur.execute(que, (limit, offset))
        data = cur.fetchall()
        cur.close()
        pagination = Pagination(page=page, per_page=limit,
                                total=total, record_name='mdetail', css_framework='bootstrap4')

        # โชว์เฉพาะ VIP
        page2 = request.args.get(get_page_parameter(), type=int, default=1)
        limit2 = 10
        offset2 = page2*limit2-limit2
        cursor2 = mysql.connection.cursor()
        cursor2.execute("select * from member where type='VIP'")

        result2 = cursor.fetchall()
        total2 = len(result2)
        cur2 = mysql.connection.cursor()
        que2 = "select * from member where type='VIP' LIMIT %s OFFSET %s"
        cur2.execute(que2, (limit, offset2))
        data2 = cur2.fetchall()
        cur2.close()
        pagination2 = Pagination(page2=page2, per_page=limit2,
                                 total=total2, record_name2='vdetail', css_framework='bootstrap4')

        return render_template('member-detail.html', pagination=pagination, mdetail=data, pagination2=pagination2, vdetail=data2)


@app.route('/addvip', methods=["POST", "GET"])
def addvip():
    title_name = request.form.get('title_name')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    phone = request.form.get('phone')
    license_plate = request.form.get('license_plate')
    province = request.form.get('province')
    car_type = request.form.get('car_type')
    modify_by= session['username']
    insert_date = now
    member_type = 'VIP'
    pay_date = date

    cursor = mysql.connection.cursor()
    sql = "INSERT INTO member(title_name, first_name,last_name, type, phone,car_type, license_plate, pay_date, province,modify_by,insert_date) VALUES  (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
    val = (title_name, first_name,last_name,member_type, phone,car_type, license_plate, pay_date, province,modify_by,insert_date)
    cursor.execute(sql, val)
    mysql.connection.commit()
    cursor.close()

    return memberdetail()


@app.route('/addmember', methods=['POST', "GET"])
def addmember():
    title_name = request.form.get('title_name')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    phone = request.form.get('phone')
    license_plate = request.form.get('license_plate')
    province = request.form.get('province')
    car_type = request.form.get('car_type')
    modify_by= session['username']
    insert_date = now
    member_type = 'member'
    pay_date = date

    cursor2 = mysql.connection.cursor()
    sql = "INSERT INTO member(title_name, first_name,last_name, type, phone,car_type, license_plate, pay_date, province,modify_by,insert_date) VALUES  (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
    
    val = (title_name, first_name,last_name,member_type, phone,car_type, license_plate, pay_date, province,modify_by,insert_date)
    cursor2.execute(sql, val)
    mysql.connection.commit()
    cursor2.close()
    
    return memberdetail()
    
    
@app.route('/remember', methods=["POST", "GET"])
def remember():
    cursor2 = mysql.connection.cursor()
    mem_no = request.values.get('memberno')
    title_name = request.values.get('title_name')
    first_name = request.values.get('first_name')
    last_name = request.values.get('last_name')
    phone = request.values.get('phone')
    license_plate = request.values.get('license_plate')
    province = request.values.get('province')
    member_package = request.values.get('member_package')
    position = request.values.get('position')
    remark = request.values.get('remark')
    sql = "UPDATE member SET title_name=%s, first_name=%s, last_name=%s, phone=%s, license_plate=%s, province=%s, member_package= %s, position= %s, remark= %s WHERE mem_no = %s"
    val = (title_name, first_name, last_name, phone, license_plate,province, member_package, position, remark, mem_no)
    cursor2.execute(sql, val)
    mysql.connection.commit()
    cursor2.close()

    return memberdetail()


@app.route('/editvip', methods=["POST", "GET"])
def editvip():
    cursor2 = mysql.connection.cursor()
    mem_no = request.values.get('vip_memberno')
    title_name = request.values.get('title_name')
    first_name = request.values.get('first_name')
    last_name = request.values.get('last_name')
    phone = request.values.get('phone')
    license_plate = request.values.get('license_plate')
    province = request.values.get('province')
    member_package = request.values.get('member_package')
    position = request.values.get('position')
    remark = request.values.get('remark')
    sql = "UPDATE member SET title_name=%s, first_name=%s, last_name=%s, phone=%s, license_plate=%s, province=%s, member_package= %s, position= %s, remark= %s WHERE mem_no = %s"
    val = (title_name, first_name, last_name, phone, license_plate,province, member_package, position, remark, mem_no)
    cursor2.execute(sql, val)
    mysql.connection.commit()
    cursor2.close()

    return memberdetail()

@app.route('/editmember', methods=["POST", "GET"])
def editmember():
    cursor2 = mysql.connection.cursor()
    mem_no = request.values.get('memberno')
    title_name = request.values.get('title_name')
    first_name = request.values.get('first_name')
    last_name = request.values.get('last_name')
    phone = request.values.get('phone')
    license_plate = request.values.get('license_plate')
    province = request.values.get('province')
    member_package = request.values.get('member_package')
    position = request.values.get('position')
    remark = request.values.get('remark')
    sql = "UPDATE member SET title_name=%s, first_name=%s, last_name=%s, phone=%s, license_plate=%s, province=%s, member_package= %s, position= %s, remark= %s WHERE mem_no = %s"
    val = (title_name, first_name, last_name, phone, license_plate,province, member_package, position, remark, mem_no)
    cursor2.execute(sql, val)
    mysql.connection.commit()
    cursor2.close()

    return memberdetail()
    return render_template('member-detail.html')

@app.route('/editmember/json')
def editmember_json():
    mem_no = request.args.get('mem_no')
    cursor = mysql.connection.cursor()
    sql = "select id, mem_no, title_name, first_name ,phone ,car_type ,license_plate ,province ,last_name from member where type ='Member' and mem_no = %s"
    val = (mem_no,)
    cursor.execute(sql,val)
    result = cursor.fetchone()

    payload = []
    content = {}
    content = {'id': result[0], 'mem_no' : result[1], 'title_name' : result[2], 'first_name': result[3], 'phone': result[4], 'car_type': result[5], 'license_plate' : result[6], 'province' : result[7] ,'last_name': result[8]}
    return content

@app.route('/renewmember/json')
def renewmember_json():
    mem_no = request.args.get('mem_no')
    cursor = mysql.connection.cursor()
    sql = "select id, mem_no, title_name, first_name ,phone ,car_type ,license_plate ,province ,last_name from member where type ='Member' and mem_no = %s"
    val = (mem_no,)
    cursor.execute(sql,val)
    result = cursor.fetchone()

    payload = []
    content = {}
    content = {'id': result[0], 'mem_no' : result[1], 'title_name' : result[2], 'first_name': result[3], 'phone': result[4], 'car_type': result[5], 'license_plate' : result[6], 'province' : result[7] ,'last_name': result[8]}
    return content

@app.route('/editvip/json')
def editvip_json():
    mem_no = request.args.get('mem_no')
    cursor = mysql.connection.cursor()
    sql = "select id, mem_no, title_name, first_name ,phone ,car_type ,license_plate ,province ,last_name from member where type ='VIP' and mem_no = %s"
    val = (mem_no,)
    cursor.execute(sql,val)
    result = cursor.fetchone()

    payload = []
    content = {}
    content = {'id': result[0], 'mem_no' : result[1], 'title_name' : result[2], 'first_name': result[3], 'phone': result[4], 'car_type': result[5], 'license_plate' : result[6], 'province' : result[7] ,'last_name': result[8]}

    return content

@app.route('/allCar_11')
def allCar_datein_11():
    cursor = mysql.connection.cursor()
    query = "select * from parking_log where date_in='2021-02-11'"
    cursor.execute(query)
    result = cursor.fetchall()
    return render_template('allCar_11.html',result=result)
@app.route('/allCar_12')
def allCar_datein_12():
    cursor = mysql.connection.cursor()
    query = "select * from parking_log where date_in='2021-02-12'"
    cursor.execute(query)
    result = cursor.fetchall()
    return render_template('allCar_12.html',result=result)
@app.route('/allCar_13')
def allCar_datein_13():
    cursor = mysql.connection.cursor()
    query = "select * from parking_log where date_in='2021-02-13'"
    cursor.execute(query)
    result = cursor.fetchall()
    return render_template('allCar_13.html',result=result)
@app.route('/allCar_14')
def allCar_datein_14():
    cursor = mysql.connection.cursor()
    query = "select * from parking_log where date_in='2021-02-14'"
    cursor.execute(query)
    result = cursor.fetchall()
    return render_template('allCar_14.html',result=result)

@app.route('/allCar_10')
def allCar_datein_10():
    cursor = mysql.connection.cursor()
    query = "select * from parking_log where date_in='2021-02-10'"
    cursor.execute(query)
    result = cursor.fetchall()
    return render_template('allCar_10.html',result=result)

@app.route('/allCar_15')
def allCar_datein_15():
    cursor = mysql.connection.cursor()
    query = "select * from parking_log where date_in='2021-02-15'"
    cursor.execute(query)
    result = cursor.fetchall()
    return render_template('allCar_15.html',result=result)

@app.route('/undefind_carin')
def test_undefind_carin():
    cursor = mysql.connection.cursor()
    query = "select * from undefind_carin"
    cursor.execute(query)
    result = cursor.fetchall()

    cursor1 = mysql.connection.cursor()
    query1 = "select count(id) from undefind_carin"
    cursor1.execute(query1)
    info = cursor1.fetchall()
    count = info[0]

    cursor2 = mysql.connection.cursor()
    query2 = "select count(id) from parking_log "
    cursor2.execute(query2)
    result2 = cursor2.fetchall()
    count_p = result2[0]

    return render_template('undefind_carin.html', count_p=count_p, count=count,result=result)

@app.route('/undefind_carin12')
def test_undefind_carin12():
    cursor = mysql.connection.cursor()
    query = "select * from undefind_carin where date_out='2021-02-12'"
    cursor.execute(query)
    result = cursor.fetchall()

    cursor1 = mysql.connection.cursor()
    query1 = "select count(id) from undefind_carin where date_out='2021-02-12'"
    cursor1.execute(query1)
    info = cursor1.fetchall()
    count = info[0]

    cursor2 = mysql.connection.cursor()
    query2 = "select count(id) from parking_log where date_in='2021-02-12'"
    cursor2.execute(query2)
    result2 = cursor2.fetchall()
    count_p = result2[0]

    return render_template('undefind_carin12.html', count_p=count_p, count=count,result=result)

@app.route('/undefind_carin13')
def test_undefind_carin13():
    cursor = mysql.connection.cursor()
    query = "select * from undefind_carin where date_out='2021-02-13'"
    cursor.execute(query)
    result = cursor.fetchall()

    cursor1 = mysql.connection.cursor()
    query1 = "select count(id) from undefind_carin where date_out='2021-02-13'"
    cursor1.execute(query1)
    info = cursor1.fetchall()
    count = info[0]

    cursor2 = mysql.connection.cursor()
    query2 = "select count(id) from parking_log where date_in='2021-02-13'"
    cursor2.execute(query2)
    result2 = cursor2.fetchall()
    count_p = result2[0]

    return render_template('undefind_carin13.html', count_p=count_p, count=count,result=result)

@app.route('/undefind_carin14')
def test_undefind_carin14():
    cursor = mysql.connection.cursor()
    query = "select * from undefind_carin where date_out='2021-02-14'"
    cursor.execute(query)
    result = cursor.fetchall()

    cursor1 = mysql.connection.cursor()
    query1 = "select count(id) from undefind_carin where date_out='2021-02-14'"
    cursor1.execute(query1)
    info = cursor1.fetchall()
    count = info[0]

    cursor2 = mysql.connection.cursor()
    query2 = "select count(id) from parking_log where date_in='2021-02-14'"
    cursor2.execute(query2)
    result2 = cursor2.fetchall()
    count_p = result2[0]

    return render_template('undefind_carin14.html', count_p=count_p, count=count,result=result)

@app.route('/undefind_carin15')
def test_undefind_carin15():
    cursor = mysql.connection.cursor()
    query = "select * from undefind_carin where date_out='2021-02-15'"
    cursor.execute(query)
    result = cursor.fetchall()

    cursor1 = mysql.connection.cursor()
    query1 = "select count(id) from undefind_carin where date_out='2021-02-15'"
    cursor1.execute(query1)
    info = cursor1.fetchall()
    count = info[0]

    cursor2 = mysql.connection.cursor()
    query2 = "select count(id) from parking_log where date_in='2021-02-15'"
    cursor2.execute(query2)
    result2 = cursor2.fetchall()
    count_p = result2[0]

    return render_template('undefind_carin15.html', count_p=count_p, count=count,result=result)

@app.route('/undefind_carin10')
def test_undefind_carin7():
    cursor = mysql.connection.cursor()
    query = "select * from undefind_carin where date_out='2021-02-10'"
    cursor.execute(query)
    result = cursor.fetchall()

    cursor1 = mysql.connection.cursor()
    query1 = "select count(id) from undefind_carin where date_out='2021-02-10'"
    cursor1.execute(query1)
    info = cursor1.fetchall()
    count = info[0]

    cursor2 = mysql.connection.cursor()
    query2 = "select count(id) from parking_log where date_in='2021-02-10'"
    cursor2.execute(query2)
    result2 = cursor2.fetchall()
    count_p = result2[0]

    return render_template('undefind_carin10.html', count_p=count_p, count=count,result=result)

@app.route('/newmember-receipt')
def newmember_receipt():
    cursor = mysql.connection.cursor()
    query = "select * from member"
    cursor.execute(query)
    result = cursor.fetchall()
    return render_template('comp/newmember-receipt.html')


@app.route('/logout', methods=["POST", "GET"])
def logout():
    mycursor = mysql.connection.cursor()
    now = datetime.now()
    logout_date = now.strftime('%Y-%m-%d %H:%M:%S')

    sql = "UPDATE login_history SET status = 'signed out', logout_date= %s WHERE user_name = %s"
    val = (logout_date, session['username'])
    mycursor.execute(sql, val)
    mysql.connection.commit()
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/invoice')
def invoice():
    rendered = render_template("reports/invoice.html")
    options = {'disable-smart-shrinking': ''}
    pdf = pdfkit.from_string(
        rendered, False, configuration=config, options=options)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline;filename=invoice.pdf'
    return response


@app.route('/receipt')
def receipt():
    if session['username'] != " ":
        cursor = mysql.connection.cursor()
        query = "select * from receipt where cashier_box = 'exit-1' ORDER BY id DESC LIMIT 1"
        cursor.execute(query)
        result = cursor.fetchone()
        tax_id = result[1]
        pos_id = result[2]

        cashier_box = result[4]
        today_date_time = result[5]
        date_now = now.strftime('%Y-%m-%d %H:%M:%S')
        license_plate= result[7]
        time_in = str(result[8])
        time_out = str(result[9])
        total_time = str(result[12])
        receipt_no = result[6]
        receieve = result[13]
        discount = result[14]
        changess = result[15]
        amount = result[16]
        fines = result[17]
    
    return render_template('comp/receipt.html' ,date_now=date_now, receipt_no=receipt_no, total_time=total_time, tax_id=tax_id ,pos_id=pos_id,today_date_time=today_date_time,cashier_box=cashier_box ,license_plate=license_plate ,amount=amount ,time_out=time_out,time_in=time_in ,discount=discount,fines=fines ,changess=changess ,receieve=receieve)


@app.route('/receipt_two')
def receipt_two():
    if session['username'] != " ":
        cursor = mysql.connection.cursor()
        query = "select * from receipt where cashier_box = 'exit-2' ORDER BY id DESC LIMIT 1"
        cursor.execute(query)
        result = cursor.fetchone()
        tax_id = result[1]
        pos_id = result[2]

        cashier_box = result[4]
        today_date_time = result[5]
        date_now = now.strftime('%Y-%m-%d %H:%M:%S')
        license_plate= result[7]
        time_in = str(result[8])
        time_out = str(result[9])
        total_time = str(result[12])
        receipt_no = result[6]
        receieve = result[13]
        discount = result[14]
        changess = result[15]
        amount = result[16]
        fines = result[17]
    
    return render_template('comp/receipt_two.html' ,date_now=date_now, receipt_no=receipt_no, total_time=total_time, tax_id=tax_id ,pos_id=pos_id,today_date_time=today_date_time,cashier_box=cashier_box ,license_plate=license_plate ,amount=amount ,time_out=time_out,time_in=time_in ,discount=discount,fines=fines ,changess=changess ,receieve=receieve)



@app.route('/slip-report')
def slip():
    return render_template('reports/slip-report.html')


@app.route('/admit-report')
def admit():
    return render_template('reports/admit-report.html')


@app.route('/inout-report')
def inout():
    rendered = render_template("reports/inout-report.html")
    options = {'disable-smart-shrinking': ''}
    pdf = pdfkit.from_string(
        rendered, False, configuration=config, options=options)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline;filename=inout-report.pdf'
    return response


@app.route('/pro-inout-report')
def proinout():
    rendered = render_template("reports/pro-inout-report.html")
    options = {'disable-smart-shrinking': ''}
    pdf = pdfkit.from_string(
        rendered, False, configuration=config, options=options)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline;filename=pro-inout-report.pdf'
    return response


@app.route('/member-report')
def memberreport():
    rendered = render_template("reports/member-report.html")
    options = {'disable-smart-shrinking': ''}
    pdf = pdfkit.from_string(
        rendered, False, configuration=config, options=options)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline;filename=member-report.pdf'
    return response


@app.route('/shift-report')
def shift():
    if session['username'] != " ":
        user = session['username']

        cursor = mysql.connection.cursor() #เวลา user login
        query = "select * from login_history where user_name = %s ORDER BY id DESC LIMIT 1"
        val = (user,)
        cursor.execute(query,val)
        result = cursor.fetchone()
        datein = result[4]

        cursor1 = mysql.connection.cursor() #รายได้
        sql = "select sum(amount) FROM receipt where cashier = %s "
        val = (user,)
        cursor1.execute(sql,val)
        info = cursor1.fetchone()
        amount = info[0]

        cursor4 = mysql.connection.cursor() #ส่วนลด
        sql4 = "select sum(discount) FROM receipt where cashier = %s "
        val = (user,)
        cursor4.execute(sql4,val)
        info4 = cursor4.fetchone()
        discount = info4[0]

        today = year+"-"+month+"-"+day

        cursor2 = mysql.connection.cursor() #รถออกจาก user คนนี้
        sql2 = "select count(id) FROM receipt where cashier = %s and date = %s "
        val = (user,today)
        cursor2.execute(sql2,val)
        info2 = cursor2.fetchone()
        count = info2[0]


        cursor3 = mysql.connection.cursor() #รถเข้าทั้งหมดวันนี้
        sql3 = "select count(id) from parking_log where date_in = %s "
        val = (today,)
        cursor3.execute(sql3,val)
        info3 = cursor3.fetchone()
        carin = info3[0]

        stale = carin - count #รถคงค้างของ user นั้นๆ

        return render_template('reports/shift-report.html', stale=stale, datein=datein, date_time=date_time, user=user, amount=amount, discount=discount, count=count,carin=carin )


def car_datatable_sql(date_start, date_end):
    sql = "select id, type, license_plate, time_in, cashier, time_out, time_total, time_promotion, time_discount, time_grand, fines, amount, discount from parking_log "

    if date_start == None and date_end != None :
        sql = "select id, type, license_plate, time_in, cashier, time_out, time_total, time_promotion, time_discount, time_grand, fines, amount, discount from parking_log where date_in <= "+"'"+date_end+"'"
    
    elif date_start != None and date_end == None :
        sql = "select id, type, license_plate, time_in, cashier, time_out, time_total, time_promotion, time_discount, time_grand, fines, amount, discount from parking_log where date_in >= "+"'"+date_start+"'"
    
    elif date_start != None and date_end != None :
        sql = "select id, type, license_plate, time_in, cashier, time_out, time_total, time_promotion, time_discount, time_grand, fines, amount, discount from parking_log where date_in BETWEEN "+"'"+date_start+"'"+" and "+"'"+date_end+"'"

    return sql 


@app.route('/report/table-car/datatable')
def table_car_datatable():
    cursor = mysql.connection.cursor()
    date_start = request.args.get('date_start')
    date_end = request.args.get('date_end')

    sql = car_datatable_sql(date_start, date_end)
    cursor.execute(sql)
    info = cursor.fetchall()
    out = []
    for element in info:
        newelement = []
        for x in element:
            newelement.append(str(x))
        out.append(newelement)
    data = jsonify({'data': out})
    return data


def out_datatable_sql(date_start, date_end):
    sql = "select id, type, license_plate, timestamp(date_in, time_in) as datetime from parking_log where licenplate_out = '' "
    
    if date_start == None and date_end != None :
        sql = "select id, type, license_plate, timestamp(date_in, time_in) as datetime from parking_log where licenplate_out = '' and date_in <= "+"'"+date_end+"'"
    
    elif date_start != None and date_end == None :
        sql = "select id, type, license_plate, timestamp(date_in, time_in) as datetime from parking_log where licenplate_out = '' and date_in >= "+"'"+date_start+"'"
    
    elif date_start != None and date_end != None :
        sql = "select id, type, license_plate, timestamp(date_in, time_in) as datetime from parking_log where licenplate_out = '' and date_in BETWEEN "+"'"+date_start+"'"+" and "+"'"+date_end+"'"

    return sql 


@app.route('/report/outcar/datatable')
def table_out_datatable():
    cursor = mysql.connection.cursor()
    date_start = request.args.get('date_start')
    date_end = request.args.get('date_end')

    sql = out_datatable_sql(date_start, date_end)
    # sql = "select id, member_type, license_plate, timestamp(date_in, time_in) as datetime from parking_log where licenplate_out = "" AND date_in = '2021-01-19' "
    cursor.execute(sql)
    info = cursor.fetchall()
    out = []
    for element in info:
        newelement = []
        for x in element:
            newelement.append(str(x))
        out.append(newelement)
    data = jsonify({'data': out})
    return data


def salestax_datatable_sql(date_start, date_end):
    sql = "select receipt.id, receipt.tax_id, member.card_no, receipt.license_plate, date(receipt.datetime_in), time(receipt.datetime_in), receipt.cashier, receipt.cashier_box, date(receipt.datetime_out), time(receipt.datetime_out), receipt.fines, receipt.amount, receipt.vat, receipt.total from receipt inner join member on receipt.id = member.id "
    
    if date_start == None and date_end != None :
        sql = "select id, type, license_plate, timestamp(date_in, time_in) as datetime from parking_log where licenplate_out = '' and date_in <= "+"'"+date_end+"'"
    
    elif date_start != None and date_end == None :
        sql = "select id, type, license_plate, timestamp(date_in, time_in) as datetime from parking_log where licenplate_out = '' and date_in >= "+"'"+date_start+"'"
    
    elif date_start != None and date_end != None :
        sql = "select id, type, license_plate, timestamp(date_in, time_in) as datetime from parking_log where licenplate_out = '' and date_in BETWEEN "+"'"+date_start+"'"+" and "+"'"+date_end+"'"

    return sql 


@app.route('/report/table-salestax/datatable')
def table_salestax_datatable():
    cursor = mysql.connection.cursor()
    date_start = request.args.get('date_start')
    date_end = request.args.get('date_end')

    sql = salestax_datatable_sql(date_start, date_end)
    cursor.execute(sql)
    info = cursor.fetchall()
    out = []
    for element in info:
        newelement = []
        for x in element:
            newelement.append(str(x))
        out.append(newelement)
    data = jsonify({'data': out})
    return data


def staff_datatable_sql(date_start, date_end):
    sql = "select id, user_name, login_date, logout_date, time(hour(login_date))+time(hour(logout_date)) as amount, discount from login_history"
    
    if date_start == None and date_end != None :
        sql = "select id, user_name, login_date, logout_date, time(hour(login_date))+time(hour(logout_date)) as amount, discount from login_history WHERE pay_date <= "+"'"+date_end+"'"
    
    elif date_start != None and date_end == None :
        sql = "select id, user_name, login_date, logout_date, time(hour(login_date))+time(hour(logout_date)) as amount, discount from login_history WHERE pay_date >= "+"'"+date_start+"'"
    
    elif date_start != None and date_end != None :
        sql = "select id, user_name, login_date, logout_date, time(hour(login_date))+time(hour(logout_date)) as amount, discount from login_histor  where pay_date BETWEEN "+"'"+date_start+"'"+" and "+"'"+date_end+"'"

    return sql 


@app.route('/report/table-staff/datatable')
def table_staff_datatable():
    cursor = mysql.connection.cursor()
    date_start = request.args.get('date_start')
    date_end = request.args.get('date_end')

    sql = staff_datatable_sql(date_start, date_end)
    cursor.execute(sql)
    info = cursor.fetchall()
    out = []
    for element in info:
        newelement = []
        for x in element:
            newelement.append(str(x))
        out.append(newelement)
    data = jsonify({'data': out})
    return data


def member_income_datatable_sql(date_start, date_end):
    sql = "select id,first_name, license_plate,member_receipt_no, pay_date, expiry_date ,amount_package ,cashier  from member"
    
    if date_start == None and date_end != None :
        sql = "select id,concat(first_name, " ", last_name) as name, license_plate,member_receipt_no, expiry_date ,amount_package ,cashier  from member WHERE pay_date <= "+"'"+date_end+"'"
    
    elif date_start != None and date_end == None :
        sql = "select id, concat(first_name, " ", last_name) as name, license_plate,member_receipt_no, expiry_date ,amount_package ,cashier from member WHERE pay_date >= "+"'"+date_start+"'"
    
    elif date_start != None and date_end != None :
        sql = "select id, concat(first_name, " ", last_name) as name, license_plate,member_receipt_no, pay_date ,expiry_date ,amount_package ,cashier from member  where pay_date BETWEEN "+"'"+date_start+"'"+" and "+"'"+date_end+"'"

    return sql    


@app.route('/report/table_member_income/datatable')
def table_member_datatable():
    date_start = request.args.get('date_start')
    date_end = request.args.get('date_end')
    
    cursor = mysql.connection.cursor()
    sql = member_income_datatable_sql(date_start, date_end)
    cursor.execute(sql)
    info = cursor.fetchall()
    out = []
    for element in info:
        newelement = []
        for x in element:
            newelement.append(str(x))
        out.append(newelement)
    data = jsonify({'data': out})
    return data


def amount_datatable_sql(date_start, date_end, member_type):
  
    sql = "select id, type, license_plate, time_in, date_in, time_out, date_out, amount, excluding_vat,vat from parking_log"
    
    if date_start != None and date_end != None and member_type != None :
        sql = "select id, type, license_plate, time_in, date_in, time_out, date_out, amount, excluding_vat,vat from parking_log  where type = "+"'"+member_type+"'"+" and date_in BETWEEN "+"'"+date_start+"'"+" and "+"'"+date_end+"'"

    elif date_start == None and date_end == None and member_type != None:
        sql = "select id, type, license_plate, time_in, date_in, time_out, date_out, amount, excluding_vat,vat from parking_log  where type = "+"'"+member_type+"'"

    elif date_start != None and date_end != None and member_type == None:
        sql = "select id, type, license_plate, time_in, date_in, time_out, date_out, amount, excluding_vat,vat from parking_log  where date_in BETWEEN "+"'"+date_start+"'"+" and "+"'"+date_end+"'"

    elif date_start == None and date_end != None and member_type == None:
        sql = "select id, type, license_plate, time_in, date_in, time_out, date_out, amount, excluding_vat,vat from parking_log WHERE date_in <= "+"'"+date_end+"'"  
    
    elif date_start != None and date_end == None and member_type == None:
        sql = "select id, type, license_plate, time_in, date_in, time_out, date_out, amount, excluding_vat,vat from parking_log WHERE date_in >= "+"'"+date_start+"'" 
    
    elif date_start != None and date_end == None and member_type != None:
        sql = "select id, type, license_plate, time_in, date_in, time_out, date_out, amount, excluding_vat,vat from parking_log WHERE type = "+"'"+member_type+"'"+" and date_in >= "+"'"+date_start+"'" 

    elif date_start == None and date_end != None and member_type != None:
        sql = "select id, type, license_plate, time_in, date_in, time_out, date_out, amount, excluding_vat,vat from parking_log WHERE type = "+"'"+member_type+"'"+" and date_in <= "+"'"+date_end+"'" 

    return sql     

@app.route('/report/table_amount/datatable')
def table_amount_datatable():
    cursor = mysql.connection.cursor() 
    date_start = request.args.get('date_start')
    date_end = request.args.get('date_end')
    member_type = request.args.get('member')

    sql = amount_datatable_sql(date_start, date_end , member_type)
    print(sql)
    cursor.execute(sql)
    info = cursor.fetchall()
    out = []
    for element in info:
        newelement = []
        for x in element:
            newelement.append(str(x))
        out.append(newelement)
    data = jsonify({'data': out})
    return data



@app.route('/background_process_test')
def background_process_test():
    control_Gate()
    print("hello")
    return ("nothing")

if __name__ == "__main__":
    app.run(debug=True , port="8000")

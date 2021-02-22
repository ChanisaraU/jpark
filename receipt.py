from db_config import mysql  # import sql

def record_receipt(TAX_ID, POS_ID, today, receipt_no, cashier_box, user,date, license_plate,discount ,fines ,changes ,receieve,time_in, time_out,total_time,amount):

    mycursor = mysql.connection.cursor()
    sql_parking = "INSERT INTO receipt(tax_id ,pos_id, today_date_time, receipt_no, cashier_box, cashier,date,license_plate,discount ,fines ,changess ,receieve,datetime_in, datetime_out,total_time,amount) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val = (TAX_ID, POS_ID, today, receipt_no, cashier_box, user, date,license_plate ,discount ,fines ,changes ,receieve,time_in, time_out,total_time,amount)
    mycursor.execute(sql_parking, val)
    mysql.connection.commit()
    mycursor.close()  

import mysql.connector


mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="car_trmp"
)

def cal_fines(fines):
    mycursor = mydb.cursor()
    sql = "update test_log set fines = %s where id = 0"
    sql_parking = "update parking_log set fines = %s where license_plate = 'กข45678'"
    val = (fines,)
    mycursor.execute(sql_parking, val)
    mydb.commit()
    mycursor.close()  


# def cal_total_amount() :
#     vat = price * 0.07
#     total_amount = price + vat
#     total_amount = '{0:.2f}'.format(float(total_amount))
#     cal_vat(vat)
#     cal_total_amount(total_amount)
#     return total_amount


def cal_discount(discount):
    mycursor = mydb.cursor()
    sql = "update test_log set discount = %s where id = 0"
    sql_parking = "update parking_log set discount = %s where license_plate = 'กข45678'"
    val = (discount,)
    mycursor.execute(sql, sql_parking, val)
    mydb.commit()
    mycursor.close()


# def cal_vat(vat):
#     mycursor = mydb.cursor()
#     sql = "update test_log set vat = %s ORDER BY date_out DESC, time_out DESC LIMIT 1"
#     sql_parking = "update parking_log set vat = %s where license_plate = 'กข45678'"
#     val = (vat,)
#     mycursor.execute(sql, sql_parking, val)
#     mydb.commit()
#     mycursor.close()


# def cal_total_amount(total_amount):
#     mycursor = mydb.cursor()
#     sql = "update test_log set total_amount = %s ORDER BY date_out DESC, time_out DESC LIMIT 1"
#     sql_parking = "update parking_log set total_amount = %s where license_plate = 'กข45678' "
#     val = (total_amount,)
#     mycursor.execute(sql, sql_parking, val)
#     mydb.commit()
#     mycursor.close()    
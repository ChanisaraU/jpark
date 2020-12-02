from db_config import mysql  # import sql

def cal_fines(fines):
    mycursor = mysql.connection.cursor()
    sql = "update test_log set fines = %s where id = 0"
    sql_parking = "update parking_log set fines = %s where license_plate = 'กข45678'"
    val = (fines,)
    mycursor.execute(sql_parking, val)
    mysql.connection.commit()
    mycursor.close()  


def cal_discount(discount):
    mycursor = mysql.connection.cursor()
    sql = "update test_log set discount = %s where id = 0"
    sql_parking = "update parking_log set discount = %s where license_plate = 'กข45678'"
    val = (discount,)
    mycursor.execute(sql_parking, val)
    mysql.connection.commit()
    mycursor.close()
    
    
def cal_receieve(receieve):
    mycursor = mysql.connection.cursor()
    sql = "update test_log set discount = %s where id = 0"
    sql_parking = "update parking_log set earn = %s where license_plate = 'กข45678'"
    val = (receieve,)
    mycursor.execute(sql_parking, val)
    mysql.connection.commit()
    mycursor.close()
        
        
def cal_changes(changes):
    mycursor = mysql.connection.cursor()
    sql = "update test_log set discount = %s where id = 0"
    sql_parking = "update parking_log set changes = %s where license_plate = 'กข45678'"
    val = (changes,)
    mycursor.execute(sql_parking, val)
    mysql.connection.commit()
    mycursor.close()

import mysql.connector
import datetime, math
from datetime import datetime,timedelta,date,time

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345",
    database="car_trmp"
    )


def get_hour(delta):
    return  delta.seconds/3600


def cal_Price():
    mycursor = mydb.cursor() 
    mycursor.execute("select date_in,time_in,date_out, TIME_FORMAT(time_out, '%T') as time_out from parking_log ORDER BY date_out DESC, time_out DESC LIMIT 1")
    myresult = mycursor.fetchall()

    for (date_in, time_in,date_out, time_out ) in myresult:
        if date_in and time_in and date_out and time_out:
            date_in = datetime.fromisoformat("{0} {1}".format(date_in, time_in))
            date_out = datetime.fromisoformat("{0} {1}".format(date_out, time_out))

            price = 0
            tmp = None
            last = False
            while(date_in < date_out and not last):
                tmp = date_in
                if date_in.hour < 4:
                    first4 = date_in.replace(hour=4, minute=0, second=0, microsecond=0)
                    first_delta = first4 - date_in if (not last) and (date_in.day != date_out.day or date_out.hour >= 4) else date_out - date_in
                    first_delta_hour = math.ceil(get_hour(first_delta))
                    if first4 <= date_out or last or date_in.day == date_out.day:
                        price += first_delta_hour * 20
                    
                    date_in = first4
                else:
                    first_mid = date_in.replace(hour=0, minute=0, second=0, microsecond=0)
                    first_mid += timedelta(days=1)
                    
                    first_delta = first_mid - date_in if (not last) and (date_in.day != date_out.day) else date_out - date_in
                    first_delta_hour = get_hour(first_delta)
                    if first_mid <= date_out or last or date_in.day == date_out.day:
                        if first_delta_hour > 4:
                            price += 60
                        elif first_delta_hour > 0.5:
                            price += 20
                    date_in = first_mid
                
                if date_in >= date_out and not last:
                    last = True
    
            discount = ''
            fines = 60
            if discount != '' and fines != '' :
                price = + price - discount + fines 
            elif discount != '' :
                price = price - discount  
            elif fines != '' :
                price = fines + price
            else:
                price  
                
        vat =  (price * 7)/100 
        formatted_vat = "{:.2f}".format(vat)
        total_amount = price + vat

        cal_vat(vat)
        cal_total_amount(total_amount)
        cal_amount(price) # สั่งอัพเดตราคา
        return price

def cal_discount(discount) :   
    mycursor = mydb.cursor() 
    sql = "update parking_log set discount = %s ORDER BY date_out DESC, time_out DESC LIMIT 1"
    val = (discount,)
    mycursor.execute(sql, val)
    mydb.commit()
    mycursor.close()        
        
def cal_fines(fines) :   
    mycursor = mydb.cursor() 
    sql = "update parking_log set fines = %s ORDER BY date_out DESC, time_out DESC LIMIT 1"
    val = (fines,)
    mycursor.execute(sql, val)
    mydb.commit()
    mycursor.close()
            
def cal_amount(price) :   
    mycursor = mydb.cursor() 
    sql = "update parking_log set amount = %s ORDER BY date_out DESC, time_out DESC LIMIT 1"
    val = (price,)
    mycursor.execute(sql, val)
    mydb.commit()
    mycursor.close()

def cal_vat(vat) :
    mycursor = mydb.cursor() 
    sql = "update parking_log set vat = %s ORDER BY date_out DESC, time_out DESC LIMIT 1"
    val = (vat,)
    mycursor.execute(sql, val)
    mydb.commit()
    mycursor.close()
    
    
def cal_total_amount(total_amount) :
    mycursor = mydb.cursor() 
    sql = "update parking_log set total_amount = %s ORDER BY date_out DESC, time_out DESC LIMIT 1"
    val = (total_amount,)
    mycursor.execute(sql, val)
    mydb.commit()
    mycursor.close()
    
print(cal_Price())    
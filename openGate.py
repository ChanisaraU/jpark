from selenium import webdriver
import os
import time

def openDoor(driver):
    open_button = driver.find_element_by_xpath('/html/body/form[2]/p[1]/input')
    open_button.click()

def Close(driver):
    open_button = driver.find_element_by_xpath('/html/body/form[2]/p[2]/input')
    open_button.click()
# USERNAME = 'abc'
# PASSWORD = '654321'
# LOGID = '20101222'


def countdown(driver): 
    t=10
    while t: 
        mins, secs = divmod(t, 60) 
        timer = '{:02d}:{:02d}'.format(mins, secs) 
        print(timer, end="\r") 
        time.sleep(1) 
        t -= 1
      
    Close(driver)

def control_Gate():
 print("H")
 driver = webdriver.Chrome('chromedriver.exe')
 driver.get('http://172.16.6.30/')

 login_button = driver.find_element_by_xpath('/html/body/fieldset/form/p[3]/input')
 login_button.click()
 # os.system("taskkill /im chrome.exe /f") //ปิดหน้าต่าง chrome
 openDoor(driver)
 countdown(driver)
 

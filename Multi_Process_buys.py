# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import staleness_of
from selenium.webdriver.chrome.options import Options

import multiprocessing
from multiprocessing import Process, Manager
from time import sleep
import sys
import sched
import random as rd 
import numpy as np

from sendNotify import send


class buy_ticket(Process):

    def __init__(self, web_name, userid, userpwd, process_id = 0, 
        chromedriver_path = r'E:\code\nsfw\FK_CP29_Buy_Ticket\chromedriver\chromedriver.exe'):
        super(buy_ticket, self).__init__()
        self.web_name = web_name
        self.userid = userid
        self.userpwd = userpwd
        self.process_id = process_id
        self.chromedriver_path = chromedriver_path # 定位到你的ChromeDriver地址
        self.driver = None
        print(f"进程 [{self.process_id}]: 开始. \n")

    def start_driver(self):
        options = Options()
        options.headless = True
        options.binary_location = r'E:\code\nsfw\FK_CP29_Buy_Ticket\chrome\chrome.exe'
        options.add_argument('--ignore-certificate-errors')
        try:
            driver = webdriver.Chrome(options = options, executable_path = self.chromedriver_path)
        except Exception as e:
            print(e)
        self.driver = driver
        driver.get(self.web_name)
        # 登录
        # 选择密码登录
        driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/div[2]/div/div/div[1]/div[1]/div/div[2]/div").click()
        # 输入用户名（手机号）
        driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/div[2]/div/div/div[2]/div/div[2]/div[1]/div[1]/div/input").send_keys(str(self.userid))
        # 输入密码
        driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/div[2]/div/div/div[2]/div/div[2]/div[2]/div[1]/div/input").send_keys(str(self.userpwd))

        login_Xpath = '/html/body/div[1]/div/div/div[1]/div[2]/div/div/div[2]/div/div[2]/button'
        driver.find_element(By.XPATH, login_Xpath).click()

        sleep(3) # 确保页面跳转

    # 定义点击按钮的函数
    def click_button(self, pay_now_button):
                pay_now_button.click()
                print(f"进程 [{self.process_id}] :开始选择日期流程! \n")

    def button(self):
        driver = self.driver
        driver.get(self.web_name)
        while True:
            try:
                sleep(1)
                # 选择门票页面
                # 选择日期和数量和vip, 默认为第一个
                # driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div/div/div[1]/div/div[2]/div[1]/div/div[2]").click()
                # 选择确认门票
                button_confirm = driver.find_element(By.XPATH, "//button[contains(text(), '立即购票')]")
                cursor_style = button_confirm.value_of_css_property("cursor")
                if cursor_style == "not-allowed":
                    raise Exception("立即购票按钮不存在或不可用")
                else:
                    button_confirm.click()

                # 定期点击按钮
                while True:
                    try:
                        sleep(1)
                        # 选择支付宝, 默认
                        # 同意协议, 默认
                        # 确认付款
                        pay_now_button = driver.find_element(By.XPATH, "//button[contains(text(), '立即付款')]")
                        self.click_button(pay_now_button)
                        # 等待页面跳转
                        WebDriverWait(driver, 1).until(staleness_of(pay_now_button))
                        print(f"进程 [{self.process_id}]: 购买成功, 退出. \n")
                        send("cp购买成功", self.web_name)
                        sys.exit(0)
                        break
                    except Exception as e:
                        # 页面未跳转
                        print(e, "暂时不可购买, 页面未跳转, 刷新页面")
                        driver.refresh()
                        pass
                sys.exit(0)
                break
            except Exception as e:
                print(e, "购买流程出错", "没有确认购买按钮或者确认按钮不可用")
                driver.refresh()
                pass

    def run(self):
        self.start_driver()
        self.button()

def start_buy_ticket(process_id, web_name, userid, userpwd, chromedriver_path):

    worker = buy_ticket(web_name, userid, userpwd, process_id)
    worker.run()
    return worker


def listening_process(process_id, buy_ticket_pool, event):
    
    while True:

        event.wait()

        (exited_process, web_name, userid, userpwd, chromedriver_path) = buy_ticket_pool.get(exited = True)

        new_process = start_buy_ticket(exited_process, web_name, userid, userpwd, chromedriver_path)

        buy_ticket_pool.replace(exited_process, new_process)

        event.clear()

    print(f"监控进程 {exited_process} 退出...")


if __name__ == "__main__":
    # Set up the buy ticket pool with numbers of url workers
    chromedriver_path = r'E:\code\nsfw\FK_CP29_Buy_Ticket\chromedriver\chromedriver.exe' # 你的ChromeDriver位置
    # 多个引号内填入多个购票地址
    # url = ["https://cp.allcpp.cn/#/ticket/detail?event=1360", "https://cp.allcpp.cn/#/ticket/detail?event=1403"]
    url = ["https://cp.allcpp.cn/#/ticket/detail?event=1360", "https://cp.allcpp.cn/#/ticket/detail?event=1403"]
    userid = '' # 购票手机号
    userpwd = '' # 购票密码
    processes_num = len(url) # 根据网页数量设置启动进程数

    buy_ticket_pool = multiprocessing.Pool(processes = processes_num)
    for i in range(len(url)):
        buy_ticket_pool.apply_async(start_buy_ticket, args=(f"Process {i}", url[i], userid, userpwd, chromedriver_path))

    # Set up the monitoring pool with processes
    monitoring_pool = multiprocessing.Pool(processes = processes_num)
    event = multiprocessing.Event()
    for i in range(processes_num):
        monitoring_pool.apply_async(listening_process, args=(f"Monitor {i}", buy_ticket_pool, event))

    # Wait for the Selenium workers to finish
    buy_ticket_pool.close()
    buy_ticket_pool.join()

    # Terminate the monitoring processes
    monitoring_pool.terminate()
    monitoring_pool.join()

'''

注意浏览器都没有设置自动关闭，如果进程因为崩溃而停止，会有备用进程跟进并继承参数；
如果进程正常停止，则代表页面成功跳转到了支付界面，需要手动扫码支付，然后手动关闭浏览器！

'''

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import staleness_of

# 创建WebDriver实例
driver = webdriver.Chrome(executable_path=r'C:\Program Files\Google\Chrome\Application\chromedriver.exe') # 定位到你的ChromeDriver地址

# 加载网页
web_names = '' #填入你购票支付界面的网址
driver.get(web_names)

Phone_Num = '' # 购票人手机号
pwd = ''  # 购票人密码

# 登录
driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/div[2]/div/div/div[1]/div[1]/div/div[2]/div").click() # 密码登录
driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/div[2]/div/div/div[2]/div/div[2]/div[1]/div[1]/div/input").send_keys(str(Phone_Num))
driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/div[2]/div/div/div[2]/div/div[2]/div[2]/div[1]/div/input").send_keys(str(pwd))


login_Xpath = '/html/body/div[1]/div/div/div[1]/div[2]/div/div/div[2]/div/div[2]/button'
driver.find_element(By.XPATH, login_Xpath).click()

from time import sleep

sleep(5)  #等待页面跳转

# 选择购票人（第一个）
driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div/div/div[3]/div[1]").click()
# 选择 支付宝
driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div/div/div[4]/div[1]").click()
sleep(2)
# 定位“立即付款”按钮
element_ID = '//*[@id="root"]/div/div[2]/div/div/button'
pay_now_button = driver.find_element(By.XPATH, element_ID)

# 定义点击按钮的函数
def click_button():
    pay_now_button.click()
    print("Clicked the button!")

# 定期点击按钮
while True:
    click_button()
    try:
        # 等待页面跳转
        WebDriverWait(driver, 0.5).until(staleness_of(pay_now_button))
        print("Page has refreshed, stopping the script.")
        break
    except:
        # 页面未跳转
        pass

# 关闭浏览器
# driver.quit()

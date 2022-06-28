import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium
from selenium.webdriver.common.keys import Keys
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--disable-notifications")
driver = webdriver.Chrome('./chromedriver.exe',chrome_options=chrome_options)

driver.get('https://www.on.bet365.ca/?_h=i6FhPo_5b_3Wczvkek1JWQ%3D%3D#/AC/B1/C1/D1002/G40/I1/Q1/F^24/')
time.sleep(5)
elements = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, """suf-CompetitionMarketGroupButton_Text""")) 
        )

print(len(elements))
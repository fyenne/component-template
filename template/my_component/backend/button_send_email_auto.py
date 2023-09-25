import streamlit as st

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time 
from selenium.webdriver.support.wait import WebDriverWait
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.chrome.options import Options
# from Screenshot import Screenshot
from datetime import datetime

def button_send_email(mode='N.Atlantic', edited_df = None):
    
    my_dir = "./" 
    options = Options()
    options.add_experimental_option("prefs", {
        "download.default_directory": my_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "profile.default_content_setting_values.automatic_downloads": True,
        # "headless":True
    })
    # options.add_argument("--headless")
 
    try:
        driver = webdriver.Chrome(
            # ChromeDriverManager().install(), 
            "D:\Installs\miniconda\chromedriver.exe",
            options=options
        )
        print('local driver seleniunm')
    except:
        driver = webdriver.Chrome(
            ChromeDriverManager().install(), 
            # "D:\Installs\miniconda\chromedriver.exe",
            options=options
        )
    driver.get('http://127.0.0.1:8502/')
    # Get the height of the webpage 
    arr = '//*[@id="tabs-bui3-tab-1"]'
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(
            (By.XPATH, arr)
            )
        )
    driver.refresh()
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(
            (By.XPATH, arr)
            )
        )
    ele = driver.find_element(By.XPATH, "//div[p[starts-with(text(),'send an email')]]")
    ele.click()
    driver.refresh()
    WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.XPATH, arr)
                )
            )
    bt = driver.find_element(By.ID, 'tabs-bui3-tab-1')
    bt.click()
    driver.maximize_window()
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") 
    import pyautogui as pg1
    pg1.scroll(1000)
    pg1.move(-900, 300)
    pg1.click()
    time.sleep(1)
    pg1.scroll(-9000)
    pg1.move(-960, -26)
    time.sleep(1)
    pg1.click()

    
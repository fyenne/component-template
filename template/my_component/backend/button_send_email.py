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


@st.cache_data(ttl=86400)
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(index = None).encode('utf-8-sig')

def button_send_email(mode='N.Atlantic', edited_df = None):
    col1, col2, col3 = st.columns([1,1,4])
    with col1:
        bt_email = st.button(f"send an email of {mode}")
    my_dir = "./" 
    options = Options()
    options.add_experimental_option("prefs", {
        "download.default_directory": my_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "profile.default_content_setting_values.automatic_downloads": True,
        # "headless":True
    })
    options.add_argument("--headless")

    date = datetime.now().strftime('%Y-%m-%d')
    save_path="D:\\samo\\bunge_freight_dashboard_ext\\dataup\\"
    image_name='selenium_screenshot.png'
    try:
        edited_df .to_csv(save_path + mode + ' open list.csv', index = None)
    except:
        pass
    subject = 'Bunge Freight Research - ' + mode + f' list {date}'
    
    if bt_email: 
        with st.spinner('in process...'):
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
            driver.maximize_window()
            height = driver.execute_script("return document.body.scrollHeight")
            width  = driver.execute_script("return document.body.scrollWidth")
            
            if mode!='N.Atlantic':
                ## 
                #? this is quite insane, before you refresh the page, the selenium cannnot click on the button!
                driver.refresh()
                arr = '//*[@id="tabs-bui3-tab-1"]'
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located(
                        (By.XPATH, arr)
                        )
                    )
                bt = driver.find_element(By.ID, 'tabs-bui3-tab-1')
                from selenium.webdriver.common.action_chains import ActionChains
                actions = ActionChains(driver)
                actions.move_to_element(bt).perform()
                bt.click() 
            driver.execute_script("document.body.style.zoom='135%'")
            try:
                driver.execute_script("document.querySelector('.css-vk3wp9.e1akgbir11').style.display = 'none'") # remove sidebar.
            except:
                pass

            height += 9099
            width += 1940
            # Set the window size to match the height of the webpage
            driver.set_window_size(width, height)
            time.sleep(5)
            screenshot_path = save_path + image_name
            driver.save_screenshot(screenshot_path)
            driver.close()
            driver.quit()
            st.balloons()
            import base64
            import sys
            sys.path.append("D:\\samo\\bunge_freight_etl\\layer_ads\\")
            from ads_email_sender_main import send_email_
            try:
                # rewrote the format of pictures.
                with open(save_path+image_name, 'rb') as f:
                    img_data = f.read()
                base64_image = base64.b64encode(img_data).decode('utf-8')
                send_email_(
                    subject = subject, 
                    receivers_ = 'gabriel.capel@bunge.com, anthony.jouve@bunge.com' , 
                    base64_image = base64_image,
                    mode = mode,
                    filename1 = save_path + mode + ' open list.csv',
                    )
                st.info('sent!...please check your email folder')
            except Exception as e:
                st.warning(str(e) + ' =====> email sender mark')
    # with col2:
    #     csv = convert_df(edited_df)
    #     st.download_button(
    #         'download openlist excel', 
    #         csv,
    #         mode + ' open list.csv',
    #         )
    
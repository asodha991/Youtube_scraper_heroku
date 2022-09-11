from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import os

class ChromeDriver:
    def getDriver(self):
        try:
            #self.driver_exe = "libraries\chromedriver.exe"
            GOOGLE_CHROME_PATH = '/app/.apt/usr/bin/google_chrome'
            CHROMEDRIVER_PATH = '/app/.chromedriver/bin/chromedriver'
            opt = webdriver.ChromeOptions()
            opt.add_argument('headless')
            opt.add_argument('--disable-gpu')
            opt.add_argument('--no-sandbox')
            opt.add_argument('--disable-dev-shm-usage')  
            opt.binary_location = os.environ.get("GOOGLE_CHROME_PATH")
            driver = webdriver.Chrome(os.environ.get("CHROMEDRIVER_PATH"), options=opt)
            return driver
        except Exception as e:
            print(e)

########################################################################################################################

    def scrollPageEnd(self,driver):
        wait = WebDriverWait(driver, 5)
        for item in range(5):
            wait.until(EC.visibility_of_element_located((By.TAG_NAME, "body"))).send_keys(Keys.END)
            time.sleep(2)

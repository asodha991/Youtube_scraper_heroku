from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

class ChromeDriver:
    def getDriver(self):
        try:
            self.driver_exe = "libraries\chromedriver.exe"
            opt = webdriver.ChromeOptions()
            opt.add_argument('headless')
            driver = webdriver.Chrome(self.driver_exe, options=opt)
            return driver
        except Exception as e:
            print(e)

########################################################################################################################

    def scrollPageEnd(self,driver):
        wait = WebDriverWait(driver, 15)
        for item in range(5):
            wait.until(EC.visibility_of_element_located((By.TAG_NAME, "body"))).send_keys(Keys.END)
            time.sleep(2)

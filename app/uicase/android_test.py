import os
from time import sleep

import unittest

from appium import webdriver

# Returns abs path relative to this file and not cwd
from appium.webdriver.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement


PATH = lambda p: os.path.abspath(
    os.path.join(os.path.dirname(__file__), p)
)


class SimpleAndroidTests():
    def setUp(self):
        self.desired_caps = {}
        self.desired_caps['platformName'] = 'Android'
        self.desired_caps['platformVersion'] = os.popen(
            f'adb shell getprop ro.build.version.release').read()
        self.desired_caps['deviceName'] = os.popen(
            f'adb shell getprop ro.product.model').read()
        self.desired_caps['noReset'] = 'true'
        self.desired_caps['autoLaunch'] = 'true'
        self.desired_caps['appPackage'] = 'com.yiche.autoeasy'
        self.desired_caps['appActivity'] = 'com.yiche.autoeasy.ADActivity'

        self.driver: WebDriver = webdriver.Remote('http://0.0.0.0:4723/wd/hub', self.desired_caps)
        print('已连接')
        # 等主页面activity出现
        home = 'com.yiche.autoeasy.MainActivity3'
        if home.startswith('com.yiche.autoeasy'):
            home = home[len('com.yiche.autoeasy'):]
        rs = self.driver.wait_activity(home, 10)
        print(f"主界面已出现:{rs}")

    def tearDown(self):
        # end the session
        sleep(3)
        self.driver.quit()

    def find_p_c(self, pid, ctext=None, cid=None, cindex=None) -> WebElement:
        if cid:
            son = f'resourceId("{pid}").childSelector(resourceId("{cid}"))'
        elif ctext:
            son = f'resourceId("{pid}").childSelector(text("{ctext}"))'
        elif cindex:
            son = f'resourceId("{pid}").childSelector(index({cindex}))'
        return self.driver.find_element_by_android_uiautomator(son)

    def find_id_text(self, id, text) -> WebElement:
        id_text = f'resourceId({id}).text({text})'
        return self.driver.find_element_by_android_uiautomator(id_text)

    def find_xpath(self, xpath):
        ele: WebElement = self.driver.find_element_by_xpath(xpath)
        return ele

    def find_id(self, res_id: str) -> WebElement:
        ele = self.driver.find_element_by_id(res_id)
        return ele

    def find_text(self, text: str) -> WebElement:
        id_text = f'text("{text}")'
        return self.driver.find_element_by_android_uiautomator(id_text)

    def test_back(self):
        self.driver.press_keycode(4)



if __name__ == '__main__':
    test = SimpleAndroidTests()
    test.setUp()
    sleep(7)
    test.find_p_c(pid='com.yiche.autoeasy:id/app_main_tab',cindex=4).click()
    test.tearDown()
5
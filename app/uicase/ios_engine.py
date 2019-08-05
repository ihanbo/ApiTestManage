import unittest
import os
from appium import webdriver
from time import sleep

from appium.webdriver.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement


class appiumSimpleTest():

    def setUp(self):
        print('开始连接服务')
        self.driver: WebDriver = webdriver.Remote(
            command_executor='http://0.0.0.0:4723/wd/hub',
            desired_capabilities={
                # 'app':app,
                'platformName': 'iOS',
                'platformVersion': '12.2',
                'deviceName': 'iPhone',
                'bundleId': 'bitauto.application',
                # 'udid': '00008020-001E11502E04002E', #xs
                'udid': '3a9b705aa4c3e42bef8dece2e8e35b581651ef35',  # 6sp
                "xcodeOrgId": "3WB4F23CG9",
                "xcodeSigningId": "iPhone Developer",
                "unicodeKeyboard": True,
                "resetKeyboard": True,
                # "autoAcceptAlerts":True,
                # "useNewWDA": True,
                # "automationName": "XCUITest",
                # "updatedWDABundleId": "com.yiche.WebDriverAgentRunner"
            }
        )
        print('服务已连接！！')

    def test_1(self):
        eles: list = self.driver.find_elements_by_ios_predicate(
            "type == 'XCUIElementTypeStaticText' AND value == '二手车'")
        eles[0].click()

    def test_2(self):
        ele: WebElement = self.driver.find_element_by_xpath(
            '//XCUIElementTypeApplication[@name="易车"]/XCUIElementTypeWindow[1]/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeScrollView/XCUIElementTypeOther/XCUIElementTypeScrollView/XCUIElementTypeOther/XCUIElementTypeTable/XCUIElementTypeScrollView/XCUIElementTypeButton[5]')
        ele.click()

    def find_by_xpath(self, xpath: str) -> WebElement:
        ele: WebElement = self.driver.find_element_by_xpath(xpath)
        return ele

    def find_by_text(self, text: str) -> WebElement:
        ele: WebElement = self.driver.find_element_by_accessibility_id(text)
        return ele

    def go_back(self):
        print('后退')
        self.driver.back()

    def tearDown(self):
        sleep(1)

    # self.driver.quit()

    def swipeUp(self, t=500, n=1):
        print(self.driver.contexts)
        '''向上滑动屏幕,从底部3/4高度滑到1/4高度'''
        l = self.driver.get_window_size()
        x1 = l['width'] * 0.5  # x坐标
        y1 = l['height'] * 0.75  # 起始y坐标
        y2 = l['height'] * 0.25  # 终点y坐标
        for i in range(n):
            self.driver.swipe(x1, y1, x1, y2, t)

    def swipRight(self, t=500, n=1):
        '''向右滑动屏幕'''
        print('右滑返回')
        l = self.driver.get_window_size()
        x1 = l['width'] * 0.25
        y1 = l['height'] * 0.5
        x2 = l['width'] * 0.75
        for i in range(n):
            self.driver.swipe(x1, y1, x2, y1, t)


if __name__ == '__main__':
    # suite = unittest.TestLoader().loadTestsFromTestCase(appiumSimpleTezt)
    # unittest.TextTestRunner(verbosity=2).run(suite)
    ios = appiumSimpleTest()
    ios.setUp()
    print('点击我的')
    sleep(2)
    ios.find_by_xpath(
        '//XCUIElementTypeApplication[@name="易车"]/XCUIElementTypeWindow[1]/XCUIElementTypeOther/XCUIElementTypeTabBar/XCUIElementTypeOther/XCUIElementTypeOther[5]').click()
    print('点击其他方式登录')
    sleep(2)
    ios.find_by_xpath('//XCUIElementTypeButton[@name="使用其他登录"]').click()
    print('点击账号登录')
    sleep(2)
    ios.find_by_text('账号登录').click()
    print('输入账号')
    sleep(2)
    ios.find_by_xpath(
        '//XCUIElementTypeApplication[@name="易车"]/XCUIElementTypeWindow[1]/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeScrollView/XCUIElementTypeScrollView/XCUIElementTypeOther/XCUIElementTypeTextField').send_keys(
        '17600360026')
    print('输入密码')
    sleep(2)
    ios.find_by_xpath(
        '//XCUIElementTypeApplication[@name="易车"]/XCUIElementTypeWindow[1]/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeScrollView/XCUIElementTypeScrollView/XCUIElementTypeOther/XCUIElementTypeSecureTextField').send_keys(
        '1313699')
    print('点击登录')
    sleep(2)
    ios.find_by_xpath('//XCUIElementTypeButton[@name="登录"]').click()
    print('完成')

    ios.tearDown()

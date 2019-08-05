import os
from time import sleep, strftime, time

import shutil
from appium.webdriver import webdriver
from appium.webdriver.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait


class BaseOperate(object):
    def __init__(self, platform: int, driver: webdriver):
        self.driver: WebDriver = driver
        self.platform = platform
        if platform != 1 and platform != 2:
            raise Exception(f'unknow platform{platform}')
        self.is_android = platform == 1

    def back(self):
        '''
        返回键
        :return:
        '''
        if self.is_android:
            self.driver.press_keycode(4)
        else:
            self.swipRight(y2=0.8)

    def enter_key(self):
        '''输入enter键'''
        if self.is_android:
            os.popen("adb shell input keyevent 66")

    def getscreen(self, **kwargs):
        u"屏幕截图,保存截图到report\screenshot目录下"
        reportName = kwargs['reportName']
        stepName = kwargs['stepName']
        st = strftime("%Y-%m-%d_%H-%M-%S")
        #         path=os.path.abspath(os.path.join(os.getcwd(), "../.."))
        path = os.path.abspath(os.path.join(os.getcwd(), ".."))  # 获取父级路径的上一级目录路径

        path = path + "/reports/%s/" % reportName
        state = os.path.exists(path)  # 判断路径是否存在
        if state:
            shutil.rmtree(path)
        os.makedirs(path)
        filename = path + "%s.png" % stepName  # 修改截图文件的存放路径为相对路径
        self.driver.get_screenshot_as_file(filename)
        print(filename)

    def find_xpath(self, xpath: str) -> WebElement:
        ele = self.driver.find_element_by_xpath(xpath)
        # ele = self.driver.find_elements_by_xpath('') #返回WebElement列表
        return ele

    def find_id(self, res_id: str) -> WebElement:
        ele = self.driver.find_element_by_id(res_id)
        return ele

    def find_text(self, text: str) -> WebElement:
        if self.is_android:
            id_text = f'text("{text}")'
            return self.driver.find_element_by_android_uiautomator(id_text)
        else:
            return self.driver.find_element_by_accessibility_id(text)

    def find_complex(self, content: str) -> WebElement:
        if self.is_android:
            return self.driver.find_element_by_android_uiautomator(content)
        else:
            return None

    def touch_tap(self, x, y, duration=50):
        u" 根据坐标点击元素"
        screen_width = self.driver.get_window_size()['width']  # 获取当前屏幕的宽
        screen_height = self.driver.get_window_size()['height']  # 获取当前屏幕的高
        a = (float(x) / screen_width) * screen_width
        x1 = int(a)
        b = (float(y) / screen_height) * screen_height
        y1 = int(b)
        self.driver.tap([(x1, y1), (x1, y1)], duration)

    def find_item(self, ele, timeout=3):
        '''用于检查页面是否存在某元素'''
        count = 0
        try:
            while count < timeout:
                source = self.driver.page_source
                if ele in source:
                    return True
                else:
                    count += 1
                    sleep(1)
            return False
        except Exception as e:
            print
            u"页面内容获取失败,程序错误或请求超时"
            self.getscreen()

    def find_by_scroll(self, ele_text):
        '''滑屏查找指定元素的方法'''
        try:
            self.driver.find_element_by_android_uiautomator(
                'new UiScrollable(new UiSelector().scrollable(true).instance(0)).getChildByText(new UiSelector().className("android.widget.TextView"), "' + ele_text + '")')
            print
            u"滑屏查找的页面元素:%s已找到" % ele_text
        except Exception as e:
            print
            u"滑屏查找的页面元素:%s没有找到,程序错误或请求超时" % ele_text
            # self.getscreen()

    def getSize(self) -> tuple:
        u"获取屏幕大小"
        x = self.driver.get_window_size()['width']
        y = self.driver.get_window_size()['height']
        return (x, y)

    # 屏幕向上滑动
    def swipeUp(self, y1=0.75, y2=0.25, t=600):
        l = self.getSize()
        x1 = int(l[0] * 0.5)  # x坐标
        y11 = int(l[1] * y1)  # 起始y坐标
        y22 = int(l[1] * y2)  # 终点y坐标
        self.driver.swipe(x1, y11, x1, y22, t)  # t 表示滑屏的时间，5代巴枪默认为600ms，7代巴枪需要根据实测调整参数

    def swipeDown(self, y1=0.25, y2=0.75, t=600):
        '''屏幕向下滑动'''
        l = self.getSize()
        x1 = int(l[0] * 0.5)  # x坐标
        y11 = int(l[1] * y1)  # 起始y坐标
        y22 = int(l[1] * y2)  # 终点y坐标
        self.driver.swipe(x1, y11, x1, y22, t)

    # 屏幕向右滑动
    def swipRight(self, x1=0.05, x2=0.75, t=600):
        '''屏幕向右滑动'''
        l = self.getSize()
        y1 = int(l[1] * 0.5)
        x11 = int(l[0] * x1)
        x22 = int(l[0] * x2)
        self.driver.swipe(x11, y1, x22, y1, t)

    # 屏幕向左滑动
    def swipLeft(self, t=600):
        '''屏幕向左滑动'''
        l = self.getSize()
        x1 = int(l[0] * 0.75)
        y1 = int(l[1] * 0.5)
        x2 = int(l[0] * 0.05)
        self.driver.swipe(x1, y1, x2, y1, t)

    # 向上滑屏，滑屏区间设置为坐标位可调
    def swipe(self, X1=0.5, Y1=0.5, Y2=0.25, t=600):  # X为横坐标的系数，Y为纵坐标的系数，t为滑屏时间，单位为ms
        '''屏幕向上滑动'''
        l = self.getSize()
        x1 = int(l[0] * X1)  # x坐标
        y1 = int(l[1] * Y1)  # 起始y坐标
        y2 = int(l[1] * Y2)  # 终点y坐标
        self.driver.swipe(x1, y1, x1, y2, t)  # t 表示滑屏的时间，5代巴枪默认为600ms

    # def long_press_text(self, ele_text, duration=2500):
    #     '''根据text元素定位来长按操作'''
    #     try:
    #         ClickElement = WebDriverWait(self.driver, timeout=10).until(
    #             EC.presence_of_element_located((By.NAME, ele_text)), message=u'元素加载超时!')
    #         elx = ClickElement.location.get('x')
    #         ely = ClickElement.location.get('y')
    #         self.driver.swipe(elx, ely, elx, ely, duration)
    #     except Exception as e:
    #         print
    #         u"页面元素:%s没有找到,程序错误或请求超时" % ele_text
    #         self.getscreen()

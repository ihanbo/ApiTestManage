import os
from time import sleep, strftime, time

import shutil
from appium.webdriver import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC, \
    expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


def log_error(param):
    print(param)
    pass


def log_info(text):
    print(text)
    pass


def log_warn(text):
    print(text)
    pass


class BaseOperate(object):
    def __init__(self, driver: webdriver):
        self.driver = driver

    def back(self):
        '''
        返回键
        :return:
        '''
        os.popen("adb shell input keyevent 4")

    def enter_key(self):
        '''输入enter键'''
        os.popen("adb shell input keyevent 66")

    def enter_key_getscreen(self):
        '''输入enter键并截屏'''
        os.popen("adb shell input keyevent 66")
        self.getscreen()

    def find_toast(self, message, timeout=7, poll_frequency=0.01):
        '''判断toast信息'''
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, message)))
            print
            element
            return True
        except:
            return False

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

    def click_by_id(self, ele_id, **kwargs):
        u"根据ID点击"
        try:
            ClickElement = WebDriverWait(self.driver, 15, 0.5).until(
                EC.presence_of_element_located((By.ID, ele_id)),
                message=u'元素加载超时!')
            ClickElement.click()
            return True, "成功", None
        except Exception as e:
            print
            u"页面元素:%s没有找到,程序错误或请求超时" % ele_id
            kwargs['stepName'] = kwargs['stepName'] + strftime("%m_%d_%H_%M_%S")
            self.getscreen(**kwargs)
            log_error(u"未找到页面元素:%s" % ele_id)
            self.driver.quit()
            return False, "未找到页面元素:{},或异常或超时：{}".format(ele_id, e.msg), kwargs['stepName']

    def click_by_class(self, ele_class, **kwargs):
        u"根据class_name点击"
        try:
            ClickElement = WebDriverWait(self.driver, 15, 0.5).until(
                EC.presence_of_element_located((By.CLASS_NAME, ele_class)), message=u'元素加载超时!')
            ClickElement.click()
        except Exception as e:
            print
            u"页面元素:%s没有找到,程序错误或请求超时" % ele_class
            self.getscreen()
            log_error(u"未找到页面元素:%s" % ele_class)
            self.driver.quit()

    def click_by_xpath(self, xp, **kwargs):
        u"根据class_name点击"
        try:
            # ClickElement = self.driver.find_element_by_xpath(xp)
            ClickElement = WebDriverWait(self.driver, 15, 0.5).until(
                EC.presence_of_element_located((By.XPATH, xp)),
                message=u'元素加载超时!')
            ClickElement.click()
            return True, "成功", None
        except Exception as e:
            print
            u"页面元素:%s没有找到,程序错误或请求超时" % xp
            kwargs['stepName'] = kwargs['stepName'] + strftime("%m_%d_%H_%M_%S")
            self.getscreen(**kwargs)
            log_error(u"未找到页面元素:%s" % xp)
            self.driver.quit()
            return False, "未找到页面元素:{}或程序错误或请求超时：{}".format(xp, e.msg), kwargs['stepName']

    def touch_tap(self, x, y, duration=50):
        u" 根据坐标点击元素"
        screen_width = self.driver.get_window_size()['width']  # 获取当前屏幕的宽
        screen_height = self.driver.get_window_size()['height']  # 获取当前屏幕的高
        a = (float(x) / screen_width) * screen_width
        x1 = int(a)
        b = (float(y) / screen_height) * screen_height
        y1 = int(b)
        self.driver.tap([(x1, y1), (x1, y1)], duration)

    def click_by_text(self, ele_text, **kwargs):
        self.driver.find_elements_by_android_uiautomator(
            "new UiSelector().text(\"%s\")" % ele_text)[0].click()

    #     def click_by_text(self,ele_text):
    #         u"根据text点击"
    #         try:
    #             ClickElement = WebDriverWait(self.driver,timeout=15).until(EC.presence_of_element_located((By.NAME,ele_text)),message=u'元素加载超时!')
    #             ClickElement.click()
    #         except Exception as e:
    #             print u"页面元素:%s没有找到,程序错误或请求超时" %ele_text
    #             self.getscreen()
    #             log_error(u"未找到页面元素:%s"%ele_text)
    #             self.driver.quit()

    def input_by_id(self, input_id, text, **kwargs):
        u"Input,根据ID，input输入内容"
        try:
            InputElement = WebDriverWait(self.driver, timeout=20).until(
                EC.presence_of_element_located((By.ID, input_id)), message=u'元素加载超时!')
            InputElement.click()
            InputElement.clear()
            InputElement.send_keys(str(text))
            return True, "输入内容" + text, None
        except Exception as e:
            print
            u"页面元素:%s没有找到,程序错误或请求超时" % input_id
            kwargs['stepName'] = kwargs['stepName'] + + strftime("%m_%d_%H_%M_%S")
            self.getscreen(**kwargs)
            log_error(u"未找到页面元素:%s" % input_id)
            self.driver.quit()
            return False, "未找到页面元素:{},或异常或超时：{}".format(input_id, e.msg), kwargs['stepName']

    def input_by_id_unclear(self, input_id, text):
        u"Input,根据ID，input输入内容"
        try:
            InputElement = WebDriverWait(self.driver, timeout=20).until(
                EC.presence_of_element_located((By.ID, input_id)), message=u'元素加载超时!')
            InputElement.send_keys(str(text))
        except Exception as e:
            print
            u"页面元素:%s没有找到,程序错误或请求超时" % input_id
            self.getscreen()
            log_error(u"未找到页面元素:%s" % input_id)
            self.driver.quit()

    def get_text(self, ele, **kwargs):
        u"根据元素ID,获取text"
        sleep(3)
        source = self.driver.page_source
        if ele in source:
            text_1 = WebDriverWait(self.driver, timeout=15).until(
                EC.presence_of_element_located((By.ID, ele)),
                message=u'元素加载超时!').get_attribute('text')
        else:
            print
            u"页面元素:%s没有找到,程序错误或请求超时" % ele
            self.getscreen()
            log_error(ele)
            self.driver.quit()
        return text_1

    def get_text1(self, xp):
        u"根据元素xpth,获取text"
        sleep(3)
        source = self.driver.page_source
        try:
            text_1 = WebDriverWait(self.driver, timeout=15).until(
                EC.presence_of_element_located((By.XPATH, xp)),
                message=u'元素加载超时!').get_attribute('text')
        except Exception as e:
            print
            u"页面元素:%s没有找到,程序错误或请求超时" % xp
            self.getscreen()
            log_error(xp)
            self.driver.quit()
        return text_1

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
            log_error(u"页面内容获取失败")

    def find_source(self):  # 方法已修改，待验证
        '''获取页面的所有页面元素'''
        try:
            source = self.driver.page_source
        except Exception as e:
            print
            u"页面内容获取失败,程序错误或请求超时"
            self.getscreen()
            log_error(u"页面内容获取失败")
        return source

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
            log_error(u"滑屏未找到页面元素:%s" % ele_text)
            # self.getscreen()

    def getSize(self):
        u"获取屏幕大小"
        x = self.driver.get_window_size()['width']
        y = self.driver.get_window_size()['height']
        return (x, y)

    # 屏幕向上滑动
    def swipeUp(self, t=600):
        l = self.getSize()
        x1 = int(l[0] * 0.5)  # x坐标
        y1 = int(l[1] * 0.75)  # 起始y坐标
        y2 = int(l[1] * 0.25)  # 终点y坐标
        self.driver.swipe(x1, y1, x1, y2, t)  # t 表示滑屏的时间，5代巴枪默认为600ms，7代巴枪需要根据实测调整参数

    # 屏幕向右滑动
    def swipRight(self, t=600):
        '''屏幕向右滑动'''
        l = self.getSize()
        x1 = int(l[0] * 0.05)
        y1 = int(l[1] * 0.5)
        x2 = int(l[0] * 0.75)
        self.driver.swipe(x1, y1, x2, y1, t)

    def swipeDown(self, t=600):
        '''屏幕向下滑动'''
        l = self.getSize()
        x1 = int(l[0] * 0.5)  # x坐标
        y1 = int(l[1] * 0.25)  # 起始y坐标
        y2 = int(l[1] * 0.75)  # 终点y坐标
        self.driver.swipe(x1, y1, x1, y2, t)

    # 屏幕向左滑动
    def swipLeft(self, t=600):
        '''屏幕向左滑动'''
        l = self.getSize()
        x1 = int(l[0] * 0.75)
        y1 = int(l[1] * 0.5)
        x2 = int(l[0] * 0.05)
        self.driver.swipe(x1, y1, x2, y1, t)

    # 点屏幕左侧向上滑动
    def swipeUp_left(self, t=1200):
        l = self.getSize()
        x1 = int(l[0] * 0.15)  # x坐标
        y1 = int(l[1] * 0.75)  # 起始y坐标
        y2 = int(l[1] * 0.50)  # 终点y坐标
        self.driver.swipe(x1, y1, x1, y2, t)  # t 表示滑屏的时间，5代巴枪默认为600ms，7代巴枪需要根据实测调整参数

    # 向下滑屏，滑屏区间的坐标位可调
    def swipeDown_Adjustable(self, X1=0.5, Y1=0.5, Y2=0.8, t=600):  # X为横坐标的系数，Y为纵坐标的系数，t为滑屏时间，单位为ms
        '''屏幕向下滑动'''
        l = self.getSize()
        x1 = int(l[0] * X1)  # x坐标
        y1 = int(l[1] * Y1)  # 起始y坐标
        y2 = int(l[1] * Y2)  # 终点y坐标
        self.driver.swipe(x1, y1, x1, y2, t)

    # 向上滑屏，滑屏区间设置为坐标位可调
    def swipeUp_Adjustable(self, X1=0.5, Y1=0.5, Y2=0.25, t=600):  # X为横坐标的系数，Y为纵坐标的系数，t为滑屏时间，单位为ms
        '''屏幕向上滑动'''
        l = self.getSize()
        x1 = int(l[0] * X1)  # x坐标
        y1 = int(l[1] * Y1)  # 起始y坐标
        y2 = int(l[1] * Y2)  # 终点y坐标
        self.driver.swipe(x1, y1, x1, y2, t)  # t 表示滑屏的时间，5代巴枪默认为600ms

    def plog(self, text):

        print
        text
        log_info(text)

    def pwlog(self, text):

        print
        text
        log_warn(text)

    def long_press_text(self, ele_text, duration=2500):
        '''根据text元素定位来长按操作'''
        try:
            ClickElement = WebDriverWait(self.driver, timeout=10).until(
                EC.presence_of_element_located((By.NAME, ele_text)), message=u'元素加载超时!')
            elx = ClickElement.location.get('x')
            ely = ClickElement.location.get('y')
            self.driver.swipe(elx, ely, elx, ely, duration)
        except Exception as e:
            print
            u"页面元素:%s没有找到,程序错误或请求超时" % ele_text
            self.getscreen()
            log_error(u"未找到页面元素:%s" % ele_text)

    def find_toast1(self, message):
        try:
            element = WebDriverWait(self.driver, timeout=3).until(
                expected_conditions.presence_of_element_located((By.PARTIAL_LINK_TEXT, message)))
            return True
        except:
            return False

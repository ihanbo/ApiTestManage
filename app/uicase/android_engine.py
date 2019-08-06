import json
import os
import threading
from time import sleep, strftime, time

from app import db
from app.models import UICaseReport

from appium import webdriver
from selenium.webdriver.remote.webelement import WebElement




class AndroidTestEngine(object):

    def __init__(self, package='com.yiche.autoeasy', launch_ac='com.yiche.autoeasy.ADActivity',
                 home_ac='.MainActivity3'):

        device = 'aaaa'
        self.desired_caps = {}
        self.desired_caps['platformName'] = 'Android'
        self.desired_caps['udid'] = device
        self.desired_caps['platformVersion'] = os.popen(
            f'adb -s {device} shell getprop ro.build.version.release').read()
        self.desired_caps['deviceName'] = os.popen(f'adb -s {device} shell getprop ro.product.model').read()
        self.desired_caps['noReset'] = 'true'
        self.desired_caps['autoLaunch'] = 'true'
        self.desired_caps['appPackage'] = package
        self.desired_caps['appActivity'] = launch_ac
        self.home_ac = home_ac
        self.driver = None

    def set_up(self) -> (bool, str):
        try:
            self.driver = webdriver.Remote('http://0.0.0.0:4723/wd/hub', self.desired_caps)
        except Exception as e:
            print('启动服务异常:  {}'.format(str(e)))
            return False, '启动服务异常:  {}'.format(str(e))
        else:
            print("appium已启动服务")
            return True, '启动服务成功'

    def back_to_home(self):
        i = 0
        while self.home_ac != self.current_activity() and i < 10:
            i += 1
            self.process_back_key()
            sleep(2)
            return

    def tearDown(self):
        '''结束服务'''
        self.driver.quit()

    def wait_home(self):
        self.wait_activity(activity=self.home_ac)

    def wait_activity(self, activity=".MainActivity3", t=10) -> bool:
        '''
        等待某界面出现，慎用，android独有
        不会抛异常，超时后返回False
        '''
        rs = self.driver.wait_activity(activity, t)
        print(f'wait_activity:结果:{rs} 当前ac:{self.driver.current_activity}')
        return rs

    def process_back_key(self):
        '''
        返回键
        :return:
        '''
        os.popen("adb shell input keyevent 4")

    def press_enter_key(self):
        '''输入enter键'''
        os.popen("adb shell input keyevent 66")

    def current_activity(self) -> str:
        '''获取当前Activity'''
        return self.driver.current_activity

    def swipeUp(self, t=500, n=1):
        '''向上滑动屏幕,从底部3/4高度滑到1/4高度'''
        l = self.driver.get_window_size()
        x1 = l['width'] * 0.5  # x坐标
        y1 = l['height'] * 0.75  # 起始y坐标
        y2 = l['height'] * 0.25  # 终点y坐标
        for i in range(n):
            self.driver.swipe(x1, y1, x1, y2, t)

    def swipeDown(self, t=500, n=1):
        '''向下滑动屏幕'''
        l = self.driver.get_window_size()
        x1 = l['width'] * 0.5  # x坐标
        y1 = l['height'] * 0.25  # 起始y坐标
        y2 = l['height'] * 0.75  # 终点y坐标
        for i in range(n):
            self.driver.swipe(x1, y1, x1, y2, t)

    def swipLeft(self, t=500, n=1):
        '''向左滑动屏幕'''
        l = self.driver.get_window_size()
        x1 = l['width'] * 0.75
        y1 = l['height'] * 0.5
        x2 = l['width'] * 0.25
        for i in range(n):
            self.driver.swipe(x1, y1, x2, y1, t)

    def swipRight(self, t=500, n=1):
        '''向右滑动屏幕'''
        l = self.driver.get_window_size()
        x1 = l['width'] * 0.25
        y1 = l['height'] * 0.5
        x2 = l['width'] * 0.75
        for i in range(n):
            self.driver.swipe(x1, y1, x2, y1, t)

    def switch_context(self, to_web: bool) -> bool:
        '''切换本地和webview环境'''
        if to_web:
            contexts = self.driver.contexts
            current_context = self.driver.current_context
            print('all contexts: ' + contexts + "   current_context:" + current_context)
            for ctx in contexts:
                if ctx.startsWith('WEB_VIEW'):
                    self.driver.switch_to.context(ctx)
                    # self.driver.switch_to.context(contexts[1])
                    return True
            return False
        else:
            # contexts = self.driver.contexts
            # self.driver.switch_to.context(contexts[0])
            self.driver.switch_to.context("NATIVE_APP")  # 这个NATIVE_APP是固定的参数
            return True

    def find_xpath(self, xpath: str) -> WebElement:
        ele = self.driver.find_element_by_xpath(xpath)
        # ele = self.driver.find_elements_by_xpath('') #返回WebElement列表
        return ele

    def find_id(self, res_id: str) -> WebElement:
        ele = self.driver.find_element_by_id(res_id)
        return ele

    def find_text(self, text: str) -> WebElement:
        id_text = f'text("{text}")'
        return self.driver.find_element_by_android_uiautomator(id_text)

    def find_uiautomator(self, content: str) -> WebElement:
        return self.driver.find_element_by_android_uiautomator(content)

    def find_parent_son(self, pid: str, cid: str, c_text: str) -> WebElement:
        if not pid:
            raise Exception('parent resource id  not set ')
        prs = f'resourceId("{pid}")'

        crs = None
        if cid and c_text:
            crs = f'resourceId("{cid}").text("{c_text}")'
        elif cid:
            prs = f'resourceId("{cid}")'
        elif c_text:
            prs = f'text("{c_text}")'
        else:
            raise Exception('child element not set id or text')

        son = f'{prs}.childSelector({crs})'
        return self.driver.find_element_by_android_uiautomator(son)

    def find_id(self, res_id: str) -> WebElement:
        ele = self.driver.find_element_by_id(res_id)
        return ele

    def find_id_text(self, res_id: str, text: str) -> WebElement:
        id_text = f'resourceId("{res_id}").text("{text}")'
        return self.driver.find_element_by_android_uiautomator(id_text)

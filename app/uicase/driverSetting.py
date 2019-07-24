import os

from appium import webdriver


class driver(object):
    def __init__(self):
        self.desired_caps = {}
        self.desired_caps['platformName'] = 'Android'
        self.desired_caps['platformVersion'] = os.popen('adb shell getprop ro.build.version.release').read()
        self.desired_caps['deviceName'] = os.popen('adb shell getprop ro.product.model').read()
        self.desired_caps['noReset'] = 'true'
        self.desired_caps['autoLaunch'] = 'true'
        self.desired_caps['appPackage'] = 'com.yiche.autoeasy'
        self.desired_caps['appActivity'] = 'com.yiche.autoeasy.ADActivity'


    def connect(self, port):
        url = 'http://0.0.0.0:%s/wd/hub' % str(port)
        global dr
        dr = webdriver.Remote(url, self.desired_caps)


def getDriver():
    return dr

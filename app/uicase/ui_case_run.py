# coding=UTF-8
import json
import os
import traceback
import unittest
from appium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from time import sleep, strftime
import threading
from app import db
from app.models import UICaseReport
from app.uicase.android_engine import AndroidTestEngine
from app.uicase.ui_action2 import BaseOperate

# 测试中的设备
running_devices: dict = {}


def try_start_test(**kwargs) -> (bool, str):
    """
    platform：平台1：安卓 2：iOS
    is_android：bool标记是否是安卓
    udid：测试设备
    single_test:单条测试single_test['case'] 、single_test['steps']
    caseset_test:用例集测试
    report_dir：目录存放地址
    test_desc：本次测试描述

    driver：测试驱动
    """
    if kwargs['single_test']:
        _test_name = kwargs['single_test']['case']['desc']
        _report_dir = kwargs['single_test']['case']['name'] + strftime("%Y-%m-%d_%H-%M-%S")
    elif kwargs['caseset_test']:
        _test_name = kwargs['caseset_test']['desc']
        _report_dir = kwargs['caseset_test']['name'] + strftime("%Y-%m-%d_%H-%M-%S")
    else:
        return False, '未发现测试用例'

    kwargs['report_dir'] = _report_dir
    kwargs['test_desc'] = _test_name

    udid = kwargs['udid']
    global running_devices
    if udid in list(running_devices.keys()):
        return False, f'该设备正在测试中：{running_devices[udid]}'

    running_devices[udid] = _test_name
    try:
        succ, desc = start_appium_test(**kwargs)
        if not succ:
            del running_devices[udid]
        return succ, desc
    except Exception as e:
        del running_devices[udid]
        return False, f'出异常了:{e}'


def start_appium_test(**kwargs):
    platform = kwargs['platform']
    if platform == 1:
        kwargs['is_android'] = True
        android_connect(**kwargs)
    elif platform == 2:
        kwargs['is_android'] = False
        ios_connect(**kwargs)
    else:
        return False, '未能识别的平台'
    return True, '启动服务成功'


def android_connect(**kwargs):
    package = kwargs.get('android_package', 'com.yiche.autoeasy')
    launch_ac = kwargs.get('android_launch', 'com.yiche.autoeasy.ADActivity')
    # home_ac = kwargs.get('', '.MainActivity3')
    device = kwargs['udid']
    desired_caps = {}
    desired_caps['platformName'] = 'Android'
    desired_caps['udid'] = device
    desired_caps['platformVersion'] = os.popen(
        f'adb -s {device} shell getprop ro.build.version.release').read()
    desired_caps['deviceName'] = os.popen(
        f'adb -s {device} shell getprop ro.product.model').read()
    desired_caps['noReset'] = 'true'
    desired_caps['autoLaunch'] = 'true'
    desired_caps['appPackage'] = package
    desired_caps['appActivity'] = launch_ac
    kwargs['driver'] = webdriver.Remote('http://0.0.0.0:4723/wd/hub', desired_caps)
    async_case_runner(**kwargs).start()


#
# def set_up(self) -> (bool, str):
#     try:
#
#     except Exception as e:
#         print('启动服务异常:  {}'.format(str(e)))
#         return False, '启动服务异常:  {}'.format(str(e))
#     else:
#         print("appium已启动服务")
#         return True, '启动服务成功'


def ios_connect(**kwargs):
    ios_bundleid = kwargs['ios_bundleid']
    udid = kwargs['udid']
    driver = webdriver.Remote(
        command_executor='http://0.0.0.0:4723/wd/hub',
        desired_capabilities={
            'platformName': 'iOS',
            'platformVersion': '12.2',
            'deviceName': 'iPhone',
            'bundleId': ios_bundleid,
            'udid': udid,
            "xcodeOrgId": "3WB4F23CG9",
            "xcodeSigningId": "iPhone Developer",
            "unicodeKeyboard": True,
            "resetKeyboard": True
        }
    )
    kwargs['driver'] = driver
    async_case_runner(**kwargs).start()


class async_case_runner(threading.Thread):

    def __init__(self, **kwargs):
        threading.Thread.__init__(self)
        self.threadID = 1111
        self.name = "ui-test-thread"

        self.udid = kwargs['udid']
        self.platform = kwargs['platform']
        self.is_android = kwargs['is_android']
        self.driver: webdriver = kwargs['driver']
        self.report_dir = kwargs['report_dir']
        self.test_desc = kwargs['test_desc']
        if kwargs['single_test']:
            self.is_single_test = True
            self.test_case = kwargs['single_test']
        elif kwargs['caseset_test']:
            self.is_single_test = False
            self.test_case = kwargs['caseset_test']
        else:
            # 找不到用例，停止驱动，删除设备
            global running_devices
            del running_devices[kwargs['udid']]
            self.driver.quit()
        self.op = BaseOperate(self.platform, self.driver)

    def run(self):  # 需要执行的case
        print('3秒后开始测试流程')
        sleep(3)
        result = {}
        result['report_dir'] = self.report_dir
        result['test_desc'] = self.test_desc
        result['succ'] = True
        result['cases'] = []

        if self.is_single_test:
            succ, report = self.test_one_case(self.test_case)
            result['succ'] = succ
            result['cases'].append(report)
        else:
            for test in self.test_case['cases']:
                succ, report = self.test_one_case[test]
                result['succ'] = succ
                result['cases'].append(report)
                if not succ:
                    break

        sleep(5)
        global running_devices
        del running_devices[self.udid]
        self.driver.quit()
        result_str = json.dumps(result)
        print(result_str)
        # case_report = UICaseReport(
        #     name=self.case['name'],
        #     desc=self.case['desc'],
        #     read_status='未读',
        #     result=result_str,
        #     report_dir=report_name,
        #     platform=self.case['platform'],
        #     project_id=self.case['project_id'],
        #     module_id=self.case['module_id'])
        # db.session.add(case_report)
        # db.session.commit()

    def test_one_case(self, test: dict):
        case = test['case']
        steps = test['steps']
        report = {'case_name': case['name'], 'case_desc': case['desc'], 'case_succ': True}

        report['case_step'] = []
        try:
            for step in steps:
                succ, desc = self.excuteLine(step)
                report['case_step'].append({
                    'succ': succ,
                    'desc': desc,
                    'pic': None if succ else self.getscreen(step['name']),
                    'stepName': step['name'],
                    'stepDesc': step['desc']
                })
                if not succ:
                    report['case_succ'] = False
                    break
                else:
                    print(f'执行完成步骤： {step["desc"]}，休眠2秒')
                    sleep(2)
        except Exception as e:
            report['case_succ'] = False
            report['case_step'].append({
                'succ': False,
                'desc': str(e),
                'pic': self.getscreen(step['name']),
                'stepName': step['name'],
                'stepDesc': step['desc']
            })
            print(f'用例{case["desc"]}的步骤{step["desc"]}出现异常：{e}')

        print(f'用例{case["desc"]}测试结束:结果{"成功" if report["case_succ"] else "失败"}')
        return report["case_succ"], report

    def excuteLine(self, step: dict):
        if step is None:
            return False, '无效行'
        print(f'执行 步骤： {step["desc"]} ,action={step["action"]}')

        ele: WebElement = None
        if step['resourceid']:
            ele = self.op.find_id(step['resourceid'])
        elif step['xpath']:
            ele = self.op.find_xpath(step['xpath'])
        elif step['text']:
            ele = self.op.find_text(step['text'])

        _action_succ = True
        if step['action'] == 'click':
            ele.click()
        elif step['action'] == 'input':
            ele.send_keys(step['extraParam'])
        elif step['action'] == 'back':
            self.op.back()
        elif step['action'] == 'swipe_down':
            self.op.swipe_down()
        elif step['action'] == 'swipe_up':
            self.op.swipe_up()
        elif step['action'] == 'swipe_left':
            self.op.swipe_left()
        elif step['action'] == 'swipe_right':
            self.op.swipe_right()
        else:
            _action_succ = False
        return _action_succ, f'成功执行：{step["desc"]}' if _action_succ else f'执行失败：{step["desc"]}，未知Action或其他'

    def getscreen(self, pic_name) -> str:
        u"屏幕截图,保存截图到report\screenshot目录下"
        try:
            path = os.path.abspath(os.path.join(os.getcwd(), ".."))  # 获取父级路径的上一级目录路径

            path = path + f"/reports/{self.report_dir}/"

            if not os.path.exists(path):
                os.makedirs(path)
                # shutil.rmtree(path) #移除目录

            filename = path + f'{pic_name + strftime("%Y-%m-%d_%H-%M-%S")}.png'  # 修改截图文件的存放路径为相对路径
            print('截图路径' + filename)
            self.driver.get_screenshot_as_file(filename)
            return filename
        except Exception as e:
            print("截图异常：" + str(e))
            return None

# def run_ui_case(cases: list):
#     engine.wait_home()
#     global engine
#     DpAppTests(engine, cases).start()
#
#
# class DpAppTests(threading.Thread):
#
#     def __init__(self, engine: AndroidTestEngine, cases: list):
#         threading.Thread.__init__(self)
#         self.threadID = 1111
#         self.name = "ui-test-thread"
#         self.engine = engine
#         self.cases = cases
#
#     def run(self):  # 需要执行的case
#
#         result = {}
#         if len(self.cases) == 1:
#             reportName = self.cases[0]['case']['name'] + strftime("%Y-%m-%d_%H-%M-%S")
#         else:
#             reportName = 'multi_ui_case_test' + strftime("%Y-%m-%d_%H-%M-%S")
#         result['reportName'] = reportName
#
#         result['cases'] = []
#
#         for case_item in self.cases:
#             case = case_item['case']
#             steps = case_item['steps']
#
#             case_report = {}
#             case_report['case_name'] = case['name']
#             case_report['case_desc'] = case['desc']
#             case_report['succ'] = True
#             case_report['step'] = []
#
#             try:
#                 for step in steps:
#                     succ, desc, pic = self.excuteLine(step, reportName)
#                     case_report['step'].append({
#                         'succ': succ,
#                         'desc': desc,
#                         'pic': pic,
#                         'stepName': step['name'],
#                         'stepDesc': step['desc']
#                     })
#                     if not succ:
#                         case_report['succ'] = False
#                         break
#             except Exception as e:
#                 print(e)
#             finally:
#                 global isRunning
#                 isRunning = False
#
#             result_str = json.dumps(result)
#             print(result_str)
#             case_report = UICaseReport(
#                 name=self.case['name'],
#                 desc=self.case['desc'],
#                 read_status='未读',
#                 result=result_str,
#                 report_dir=reportName,
#                 platform=self.case['platform'],
#                 project_id=self.case['project_id'],
#                 module_id=self.case['module_id'])
#             db.session.add(case_report)
#             db.session.commit()
#
#     def excuteLine(self, step: dict, reportName: str):
#         if step is None:
#             return False, '无效行', None
#         print('执行 desc = {0},index={1},action={2}'.format(step['desc'], self.case['id'],
#                                                           step['action']))
#         if step['action']:
#             if step['action'] == 'click':
#                 sleep(1)
#                 if step['resourceid']:
#                     return self.engine.find_id(step['resourceid'], reportName=reportName,
#                                                stepName=step['name'])
#                 elif step['xpath']:
#                     return actionOp.click_by_xpath(step['xpath'], reportName=reportName,
#                                                    stepName=step['name'])
#                 elif step['text']:
#                     return actionOp.click_by_text(step['text'], reportName=reportName,
#                                                   stepName=step['name'])
#                 else:
#                     return False, '未指定步骤:{} 中的元素'.format(step['name']), None
#             elif step['action'] == 'input':
#                 print('输入内容是{0}'.format(step['extraParam']))
#                 return actionOp.input_by_id(step['resourceid'], step['extraParam'],
#                                             reportName=reportName,
#                                             stepName=step['name'])
#                 sleep(2)
#             else:
#                 return False, '无效行', None

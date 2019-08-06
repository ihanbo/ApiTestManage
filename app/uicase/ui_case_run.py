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

isRunning = False
dr = None
actionOp = None

isRunning: bool = False  # 标记服务运行中
platform = 1  # 平台1：安卓 2：ios
driver = None


def setUp(and_package='com.yiche.autoeasy', and_launch='', ios_bundleid='bitauto.application',
          **kwargs) -> (bool, str):
    global isRunning
    if isRunning:
        return False, '用例测试进行中'

    isRunning = True
    global platform, driver
    platform = kwargs['platform']
    succ, driver, desc = connect_appium()
    isRunning = succ
    return succ, desc


def connect_appium():
    global platform
    if platform == 1:
        return False, None, '稍等片刻还没弄了'
    elif platform == 2:
        return ios_connect()
    else:
        return False, None, '未知平台'


def ios_connect():
    try:
        driver = webdriver.Remote(
            command_executor='http://0.0.0.0:4723/wd/hub',
            desired_capabilities={
                'platformName': 'iOS',
                'platformVersion': '12.2',
                'deviceName': 'iPhone',
                'bundleId': 'bitauto.application',
                # 'udid': '00008020-001E11502E04002E', #xs
                'udid': '3a9b705aa4c3e42bef8dece2e8e35b581651ef35',  # 6sp
                "xcodeOrgId": "3WB4F23CG9",
                "xcodeSigningId": "iPhone Developer",
                "unicodeKeyboard": True,
                "resetKeyboard": True
            }
        )
        return True, driver, "启动服务成功"
    except Exception as e:
        print(e)
        return False, None, "启动服务失败"


def run_ui_cases(case: dict, steps: list):
    global platform
    engine(platform, case, steps).start()


class engine(threading.Thread):

    def __init__(self, platform: int, case: dict, steps: list):
        threading.Thread.__init__(self)
        self.threadID = 1111
        self.name = "ui-test-thread"
        self.platform = platform
        self.case = case
        self.steps = steps
        global driver
        self.op = BaseOperate(platform, driver)

    def run(self):  # 需要执行的case
        print('3秒后开始测试流程')
        sleep(3)
        # self.case.get('name','not_found') + strftime("%Y-%m-%d_%H-%M-%S")
        report_name = self.case.get('name', 'not_found') + strftime("%Y-%m-%d_%H-%M-%S")
        result = {}
        result['reportName'] = report_name
        result['case_name'] = self.case['name']
        result['case_desc'] = self.case['desc']
        result['succ'] = True
        result['step'] = []

        try:
            for step in self.steps:
                succ, desc, pic = self.excuteLine(step, report_name)
                result['step'].append({
                    'succ': succ,
                    'desc': desc,
                    'pic': pic,
                    'stepName': step['name'],
                    'stepDesc': step['desc']
                })
                if not succ:
                    result['succ'] = False
                    break
                else:
                    print(f'执行完成步骤： {step["desc"]}，没有休眠2秒')
                    # sleep(2)
        except Exception as e:
            result['succ'] = False
            result['step'].append({
                'succ': False,
                'desc': str(e),
                'pic': None,
                'stepName': step['name'],
                'stepDesc': step['desc']
            })
            print(e)

        sleep(5)
        global isRunning, driver
        isRunning = False
        driver.quit()
        result_str = json.dumps(result)
        print(result_str)
        case_report = UICaseReport(
            name=self.case['name'],
            desc=self.case['desc'],
            read_status='未读',
            result=result_str,
            report_dir=report_name,
            platform=self.case['platform'],
            project_id=self.case['project_id'],
            module_id=self.case['module_id'])
        # db.session.add(case_report)
        # db.session.commit()

    def excuteLine(self, step: dict, report_name: str):
        if step is None:
            return False, '无效行', None
        print(f'执行 步骤： {step["desc"]} ,action={step["action"]}')

        ele: WebElement = None
        if step['resourceid']:
            ele = self.op.find_id(step['resourceid'])
        elif step['xpath']:
            ele = self.op.find_xpath(step['xpath'])
        elif step['text']:
            ele = self.op.find_text(step['text'])
        if not ele:
            return False, '未找到元素', None

        if step['action'] == 'click':
            ele.click()
            return True, '执行成功', None
        elif step['action'] == 'input':
            ele.send_keys(step['extraParam'])
            return True, '执行成功', None
        else:
            return False, '无效行', None

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

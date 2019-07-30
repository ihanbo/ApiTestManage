# coding=UTF-8
import json
import os
# Appium环境配置
import threading
import unittest
from time import sleep, strftime

from appium import webdriver

from app import db
from app.models import UICaseStep, UICase, UicaseStepInfo, UICaseReport
from app.uicase.driverSetting import driver, getDriver
from app.uicase.ui_action import BaseOperate

PATH = lambda p: os.path.abspath(
    os.path.join(os.path.dirname(__file__), p)
)

isRunning = False
dr = None
actionOp = None


def setUp():
    global isRunning
    if isRunning:
        return 0, '用力测试进行中'
    try:
        isRunning = True
        _connect(4723)
        global actionOp
        actionOp = BaseOperate(dr)
    except Exception as e:
        isRunning = False
        print(e)
        return 0, '启动服务失败'
    else:
        return 1, '启动服务成功'


def run_ui_case(case: dict, steps: list):
    # sleep(7) #等待app启动
    print('ok')
    DpAppTests(case, steps).start()


def _connect(port):
    url = 'http://0.0.0.0:%s/wd/hub' % str(port)
    global dr
    dr = webdriver.Remote(url, get_params())
    return 'ok'


def get_params():
    desired_caps = {}
    desired_caps['platformName'] = 'Android'
    desired_caps['platformVersion'] = os.popen('adb shell getprop ro.build.version.release').read()
    desired_caps['deviceName'] = os.popen('adb shell getprop ro.product.model').read()
    desired_caps['noReset'] = 'true'
    desired_caps['autoLaunch'] = 'true'
    desired_caps['appPackage'] = 'com.yiche.autoeasy'
    desired_caps['appActivity'] = 'com.yiche.autoeasy.ADActivity'
    return desired_caps


class DpAppTests(threading.Thread):

    def __init__(self, case: dict, steps: list):
        threading.Thread.__init__(self)
        self.threadID = 1111
        self.name = "ui-test-thread"
        self.steps = steps
        self.case = case

    def run(self):  # 需要执行的case
        result = {}
        reportName = self.case['name'] + strftime("%Y-%m-%d_%H-%M-%S")
        result['reportName'] = reportName
        result['case_name'] = self.case['name']
        result['case_desc'] = self.case['desc']
        result['succ'] = True
        result['step'] = []

        try:
            for step in self.steps:
                succ, desc, pic = self.excuteLine(step, reportName)
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
        except Exception as e:
            print(e)
        finally:
            global isRunning
            isRunning = False

        result_str = json.dumps(result)
        print(result_str)
        case_report = UICaseReport(
            name=self.case['name'],
            desc=self.case['desc'],
            read_status='未读',
            result=result_str,
            report_dir=reportName,
            platform=self.case['platform'],
            project_id=self.case['project_id'],
            module_id=self.case['module_id'])
        db.session.add(case_report)
        db.session.commit()

    def excuteLine(self, step: dict, reportName: str):
        if step is None:
            return False, '无效行', None
        print('执行 desc = {0},index={1},action={2}'.format(step['desc'], self.case['id'],
                                                          step['action']))
        global actionOp
        if step['action']:
            if step['action'] == 'click':
                print('waiting 1 sec')
                sleep(1)
                if step['resourceid']:
                    return actionOp.click_by_id(step['resourceid'], reportName=reportName,
                                                stepName=step['name'])
                elif step['xpath']:
                    return actionOp.click_by_xpath(step['xpath'], reportName=reportName,
                                                   stepName=step['name'])
                elif step['text']:
                    return actionOp.click_by_text(step['text'], reportName=reportName,
                                                  stepName=step['name'])
                else:
                    return False, '未指定步骤:{} 中的元素'.format(step['name']), None
            elif step['action'] == 'input':
                print('输入内容是{0}'.format(step['extraParam']))
                return actionOp.input_by_id(step['resourceid'], step['extraParam'],
                                            reportName=reportName,
                                            stepName=step['name'])
                sleep(2)
            else:
                return False, '无效行', None

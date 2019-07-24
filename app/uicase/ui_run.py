# coding=UTF-8
import json
import os
# Appium环境配置
import threading
import unittest
from time import sleep, strftime

from app.models import UICaseStep, UICase, UicaseStepInfo
from app.uicase.driverSetting import driver, getDriver
from app.uicase.ui_action import BaseOperate

PATH = lambda p: os.path.abspath(
    os.path.join(os.path.dirname(__file__), p)
)


class StepResult():
    """
    步骤测试结果
    """

    succ = False
    desc = ''
    picName = ''

    def __init__(self, step: UICaseStep, succ, desc, picName):
        self.succ = succ
        self.desc = desc
        self.picName = picName
        self.stepName = step['name']
        self.stepDesc = step['desc']


class DpAppTests(threading.Thread):

    def __init__(self, case: dict, steps: list):
        threading.Thread.__init__(self)
        self.threadID = 1111
        self.name = "ui-test-thread"
        self.steps = steps
        self.case = case

    def setUp(self):
        try:
            driver().connect(4723)
            self.driver = getDriver()
            self.actionOp = BaseOperate(self.driver)
        except Exception as e:
            return 0, '启动服务失败'
        else:
            return 1, '启动服务成功'

    def tearDown(self):
        # self.driver.quit()  # case执行完退出
        print('用例执行完成')

    def run(self):  # 需要执行的case
        self.waitAppStart()

        result = {}
        reportName = self.case['name'] + strftime("%Y-%m-%d_%H-%M-%S")
        result['reportName'] = reportName
        result['succ'] = True
        result['step'] = []

        for step in self.steps:
            succ, desc, pic = self.excuteLine(step, reportName)
            result['step'].append(StepResult(step, succ, desc, pic).__dict__)
            if not succ:
                result['succ'] = False
                break

        print(json.dumps(result))

    def waitAppStart(self):
        sleep(7)

    def excuteLine(self, step: dict, reportName: str):
        if step is None:
            return False, '无效行', None
        print('执行 desc = {0},index={1},action={2}'.format(step['desc'], self.case['id'], step['action']))
        if step['action'] :
            if step['action'] == 'click':
                print('waiting 1 sec')
                sleep(1)
                if step['resourceid']:
                    return self.actionOp.click_by_id(step['resourceid'], reportName=reportName,
                                                     stepName=step['name'])
                elif step['xpath']:
                    return self.actionOp.click_by_xpath(step['xpath'], reportName=reportName,
                                                        stepName=step['name'])
                elif step['text']:
                    return self.actionOp.click_by_text(step['text'], reportName=reportName,
                                                       stepName=step['name'])
                else:
                    return False, '未指定步骤:{} 中的元素'.format(step['name']), None
            elif step['action'] == 'input':
                print('输入内容是{0}'.format(step['extraParam']))
                return self.actionOp.input_by_id(step['resourceid'], step['extraParam'],
                                                 reportName=reportName,
                                                 stepName=step['name'])
                sleep(2)
            else:
                return False, '无效行', None


def run_ui(case: UICase, steps: list):
    dat = DpAppTests(list)
    dat.setUp()
    dat.test_dpApp()


def setUp():
    return None

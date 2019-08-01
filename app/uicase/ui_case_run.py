# coding=UTF-8
import json
import os
import unittest
from time import sleep, strftime
import threading
from app import db
from app.models import UICaseReport
from app.uicase.android_engine import AndroidTestEngine

isRunning = False
dr = None
actionOp = None

isRunning: bool = False  # 标记服务运行中
dr = None
engine: AndroidTestEngine = None


def setUp(package='com.yiche.autoeasy', launch_ac='com.yiche.autoeasy.ADActivity',
          home_ac='.MainActivity3') -> (bool, str):
    global isRunning, engine
    if isRunning:
        return False, '用例测试进行中'
    isRunning = True
    engine = AndroidTestEngine()
    succ, desc = engine.set_up()
    isRunning = succ
    return succ, desc


def run_ui_case(cases: list):
    engine.wait_home()
    global engine
    DpAppTests(engine, cases).start()


class DpAppTests(threading.Thread):

    def __init__(self, engine: AndroidTestEngine, cases: list):
        threading.Thread.__init__(self)
        self.threadID = 1111
        self.name = "ui-test-thread"
        self.engine = engine
        self.cases = cases

    def run(self):  # 需要执行的case

        result = {}
        if len(self.cases) == 1:
            reportName = self.cases[0]['case']['name'] + strftime("%Y-%m-%d_%H-%M-%S")
        else:
            reportName = 'multi_ui_case_test' + strftime("%Y-%m-%d_%H-%M-%S")
        result['reportName'] = reportName

        result['cases'] = []

        for case_item in self.cases:
            case = case_item['case']
            steps = case_item['steps']

            case_report = {}
            case_report['case_name'] = case['name']
            case_report['case_desc'] = case['desc']
            case_report['succ'] = True
            case_report['step'] = []

            try:
                for step in steps:
                    succ, desc, pic = self.excuteLine(step, reportName)
                    case_report['step'].append({
                        'succ': succ,
                        'desc': desc,
                        'pic': pic,
                        'stepName': step['name'],
                        'stepDesc': step['desc']
                    })
                    if not succ:
                        case_report['succ'] = False
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
        if step['action']:
            if step['action'] == 'click':
                sleep(1)
                if step['resourceid']:
                    return self.engine.find_id(step['resourceid'], reportName=reportName,
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

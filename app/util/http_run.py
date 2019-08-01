import json
import types
import time
from app.models import *
from httprunner.api import HttpRunner
from ..util.global_variable import *
from ..util.httprunner_change import *
from ..util.utils import encode_object
import importlib
from app import scheduler
from flask.json import JSONEncoder


class RunCase(object):
    def __init__(self, project_ids=None):
        self.project_ids = project_ids
        self.pro_config_data = None
        self.pro_base_url = None
        self.new_report_id = None
        self.TEST_DATA = {'testcases': [], 'project_mapping': {'functions': {}, 'variables': {}}}
        self.init_project_data()

    def init_project_data(self):
        pro_base_url = {}
        for pro_data in Project.query.all():
            if pro_data.environment_choice == 'first':
                pro_base_url['{}'.format(pro_data.id)] = json.loads(pro_data.host)
            elif pro_data.environment_choice == 'second':
                pro_base_url['{}'.format(pro_data.id)] = json.loads(pro_data.host_two)
            if pro_data.environment_choice == 'third':
                pro_base_url['{}'.format(pro_data.id)] = json.loads(pro_data.host_three)
            if pro_data.environment_choice == 'fourth':
                pro_base_url['{}'.format(pro_data.id)] = json.loads(pro_data.host_four)
        self.pro_base_url = pro_base_url
        self.pro_config(Project.query.filter_by(id=self.project_ids).first())

    def pro_config(self, project_data):
        """
        把project的配置数据解析出来
        :param project_data:
        :return:
        """
        self.TEST_DATA['project_mapping']['variables'] = {h['key']: h['value'] for h in
                                                          json.loads(project_data.variables) if h.get('key')}
        if project_data.func_file:
            self.extract_func([project_data.func_file.replace('.py', '')])

    def extract_func(self, func_list):
        """
        提取函数文件中的函数
        :param func_list: 函数文件地址list
        :return:
        """
        for f in func_list:
            func_list = importlib.reload(importlib.import_module('func_list.{}'.format(f)))
            module_functions_dict = {name: item for name, item in vars(func_list).items()
                                     if isinstance(item, types.FunctionType)}
            self.TEST_DATA['project_mapping']['functions'].update(module_functions_dict)

    def assemble_step(self, api_id=None, step_data=None, pro_base_url=None, status=False):
        """
        :param api_id:
        :param step_data:
        :param pro_base_url:
        :param status: 判断是接口调试(false)or业务用例执行(true)
        :return:
        """
        if status:
            # 为true，获取api基础信息；case只包含可改变部分所以还需要api基础信息组合成全新的用例
            api_data = ApiMsg.query.filter_by(id=step_data.api_msg_id).first()
        else:
            # 为false，基础信息和参数信息都在api里面，所以api_case = case_data，直接赋值覆盖
            api_data = ApiMsg.query.filter_by(id=api_id).first()
            step_data = api_data
            # api_data = case_data

        _data = {'name': step_data.name,
                 'request': {'method': api_data.method,
                             'files': {},
                             'data': {}}}

        _data['request']['headers'] = {h['key']: h['value'] for h in json.loads(api_data.header)
                                       if h['key']} if json.loads(api_data.header) else {}

        if api_data.status_url != '-1':
            if api_data.url.startswith('http'):
                _data['request']['url'] = api_data.url.split('?')[0]
            else:
                _data['request']['url'] = pro_base_url['{}'.format(api_data.project_id)][
                                          int(api_data.status_url)] + api_data.url.split('?')[0]
        else:
            _data['request']['url'] = api_data.url

        if step_data.up_func:
            _data['setup_hooks'] = [step_data.up_func]

        if step_data.down_func:
            _data['teardown_hooks'] = [step_data.down_func]

        if status:
            _data['times'] = step_data.time
            if json.loads(step_data.status_param)[0]:
                if json.loads(step_data.status_param)[1]:
                    _param = json.loads(step_data.param)
                else:
                    _param = json.loads(api_data.param)
            else:
                _param = None

            if json.loads(step_data.status_variables)[0]:
                if json.loads(step_data.status_variables)[1]:
                    _json_variables = step_data.json_variable
                    _variables = json.loads(step_data.variable)
                else:
                    _json_variables = api_data.json_variable
                    _variables = json.loads(api_data.variable)
            else:
                _json_variables = None
                _variables = None

            if json.loads(step_data.status_extract)[0]:
                if json.loads(step_data.status_extract)[1]:
                    _extract = step_data.extract
                else:
                    _extract = api_data.extract
            else:
                _extract = None

            if json.loads(step_data.status_validate)[0]:
                if json.loads(step_data.status_validate)[1]:
                    _validate = step_data.validate
                else:
                    _validate = api_data.validate
            else:
                _validate = None

        else:
            _param = json.loads(api_data.param)
            _json_variables = api_data.json_variable
            _variables = json.loads(api_data.variable)
            _extract = api_data.extract
            _validate = api_data.validate

        _data['request']['params'] = {param['key']: param['value'].replace('%', '&') for param in
                                      _param if param.get('key')} if _param else {}

        _data['extract'] = [{ext['key']: ext['value']} for ext in json.loads(_extract) if
                            ext.get('key')] if _extract else []

        _data['validate'] = [{val['comparator']: [val['key'], val['value']]} for val in json.loads(_validate) if
                             val.get('key')] if _validate else []

        if api_data.method == 'GET':
            pass
        # elif _variables:
        #     print(_variables)
        #     print(111)
        elif api_data.variable_type == 'text' and _variables:
            for variable in _variables:
                if variable['param_type'] == 'string' and variable.get('key'):
                    _data['request']['files'].update({variable['key']: (None, variable['value'])})
                elif variable['param_type'] == 'file' and variable.get('key'):
                    _data['request']['files'].update({variable['key']: (
                        variable['value'].split('/')[-1], open(variable['value'], 'rb'),
                        CONTENT_TYPE['.{}'.format(variable['value'].split('.')[-1])])})

        elif api_data.variable_type == 'data' and _variables:
            for variable in _variables:
                if variable['param_type'] == 'string' and variable.get('key'):
                    _data['request']['data'].update({variable['key']: variable['value']})
                elif variable['param_type'] == 'file' and variable.get('key'):
                    _data['request']['files'].update({variable['key']: (
                        variable['value'].split('/')[-1], open(variable['value'], 'rb'),
                        CONTENT_TYPE['.{}'.format(variable['value'].split('.')[-1])])})

        elif api_data.variable_type == 'json':
            if _json_variables:
                _data['request']['json'] = json.loads(_json_variables)

        return _data

    def get_api_test(self, api_ids, config_id):
        """
        接口调试时，用到的方法
        :param api_ids: 接口id列表
        :param config_id: 配置id
        :return:
        """
        scheduler.app.logger.info('本次测试的接口id：{}'.format(api_ids))
        _steps = {'teststeps': [], 'config': {'variables': {}}, 'output': ['phone']}
        _steps['config']['variables']['wait_times'] = 0

        if config_id:
            config_data = Config.query.filter_by(id=config_id).first()
            _config = json.loads(config_data.variables) if config_id else []
            _steps['config']['variables'].update({v['key']: v['value'] for v in _config if v['key']})
            self.extract_func(['{}'.format(f.replace('.py', '')) for f in json.loads(config_data.func_address)])

        _steps['teststeps'] = [self.assemble_step(api_id, None, self.pro_base_url, False) for api_id in api_ids]
        self.TEST_DATA['testcases'].append(_steps)

    def get_case_test(self, case_ids):
        """
        用例调试时，用到的方法
        :param case_ids: 用例id列表
        :return:
        """
        scheduler.app.logger.info('本次测试的用例id：{}'.format(case_ids))

        for case_id in case_ids:
            case_data = Case.query.filter_by(id=case_id).first()
            case_times = case_data.times if case_data.times else 1
            for s in range(case_times):
                _steps = {'teststeps': [], 'config': {'variables': {}, 'name': ''}}
                _steps['config']['name'] = case_data.name
                _steps['config']['variables']['wait_times'] = case_data.wait_times

                # 获取用例的配置数据
                _config = json.loads(case_data.variable) if case_data.variable else []
                _steps['config']['variables'].update({v['key']: v['value'] for v in _config if v['key']})

                self.extract_func(['{}'.format(f.replace('.py', '')) for f in json.loads(case_data.func_address)])

                for _step in CaseData.query.filter_by(case_id=case_id).order_by(CaseData.num.asc()).all():
                    if _step.status == 'true':  # 判断步骤状态，是否执行
                        _steps['teststeps'].append(self.assemble_step(None, _step, self.pro_base_url, True))
                self.TEST_DATA['testcases'].append(_steps)

    def build_report(self, jump_res, case_ids):

        new_report = Report(
            case_names=','.join([Case.query.filter_by(id=scene_id).first().name for scene_id in case_ids]),
            project_id=self.project_ids, read_status='待阅')
        db.session.add(new_report)
        db.session.commit()

        self.new_report_id = new_report.id
        with open('{}{}.txt'.format(REPORT_ADDRESS, self.new_report_id), 'w',encoding='utf-8') as f:
            f.write(jump_res)
        return self.new_report_id

    def gen_result_summary(self, jump_res, project_id, report_id):
        jump_res_dict = json.loads(jump_res)
        new_result_summary = ResultSummary(case_total = jump_res_dict['stat']['testcases']['total'],
            case_success = jump_res_dict['stat']['testcases']['success'],
            case_fail = jump_res_dict['stat']['testcases']['fail'],
            step_total = jump_res_dict['stat']['teststeps']['total'],
            step_successes = jump_res_dict['stat']['teststeps']['successes'],
            step_failures = jump_res_dict['stat']['teststeps']['failures'],
            step_errors = jump_res_dict['stat']['teststeps']['errors'],
            start_datetime = datetime.strptime(jump_res_dict['time']['start_datetime'],"%Y-%m-%d %H:%M:%S"),
            duration = jump_res_dict['time']['duration'],
            project_id = project_id,
            report_id = report_id,)
        db.session.add(new_result_summary)
        db.session.commit()
        report_summary_id = new_result_summary.id
        self.gen_result_detail(jump_res, project_id, report_id, report_summary_id)

    def gen_result_detail(self, jump_res, proid, repid, rep_sum_id):
        jump_res_dict = json.loads(jump_res)
        project_name = Project.query.filter_by(id=proid).first().name
        for index, case in enumerate(jump_res_dict['details']):
            case_name = case['name']
            case_id = Case.query.filter_by(name = case_name).first().id
            case_exec_status = case['success']
            case_time_start_at = case['time']['start_at']
            case_duration = case['time']['duration']
            case_set_id = Case.query.filter_by(id=case_id).first().case_set_id
            case_set_name = CaseSet.query.filter_by(id=case_set_id).first().name
            if case['records']:
                for casedata in case['records']:
                    case_data_name = casedata['name']
                    case_data_id = CaseData.query.filter_by(name = case_data_name).first().id
                    api_msg_id = CaseData.query.filter_by(name = case_data_name).first().api_msg_id
                    api_msg_name = ApiMsg.query.filter_by(id=api_msg_id).first().name
                    api_exec_status = casedata['status']
                    if api_exec_status == 'error':
                        response_time = float(0)
                    else:
                        response_time = float(casedata['response_time'])
                    report_id = repid
                    project_id = proid
                    result_summary_id = rep_sum_id
                    new_result_detail = ResultDetail(
                        case_id = case_id,
                        case_name = case_name,
                        case_exec_status = case_exec_status,
                        case_time_start_at = datetime.fromtimestamp(case_time_start_at),
                        case_duration = case_duration,
                        case_data_id = case_data_id,
                        case_data_name = case_data_name,
                        api_msg_id = api_msg_id,
                        api_msg_name = api_msg_name,
                        api_exec_status = api_exec_status,
                        response_time = response_time,
                        project_id = project_id,
                        project_name = project_name,
                        case_set_id = case_set_id,
                        case_set_name = case_set_name,
                        report_id = report_id,
                        result_summary_id = result_summary_id,)
                    db.session.add(new_result_detail)
        db.session.commit()

    def run_case(self):
        scheduler.app.logger.info('测试数据：{}'.format(self.TEST_DATA))
        # res = main_ate(self.TEST_DATA)
        runner = HttpRunner()
        # runner.run(self.TEST_DATA)
        jump_res = {'success': True,
                    'stat':{'testcases':{'total':0, 'success':0, 'fail':0},
                            'teststeps':{'total':0, "failures":0, 'errors':0, 'skipped':0,'expectedFailures':0, 'unexpectedSuccesses':0, 'successes':0}
                            },
                    'time':{'start_at':0, 'duration': 0, 'start_datetime':"2019-07-17 19:17:02"},
                    'platform':{},
                    'details':[]
                    }

        for index, case in enumerate(self.TEST_DATA['testcases']):
            tmp_case_dict = {'testcases':[{"config":case['config'], "teststeps":case['teststeps']}], 'project_mapping':self.TEST_DATA['project_mapping']}
            runner.run(tmp_case_dict)
            waittimes = case['config']['variables']['wait_times']
            if waittimes != 0:
                time.sleep(case['config']['variables']['wait_times'] / 1000)
            tmp_jump_res = runner._summary
            if not tmp_jump_res['success']:
                jump_res['success'] = False
            jump_res['stat']['testcases']['total'] += tmp_jump_res['stat']['testcases']['total']
            jump_res['stat']['testcases']['success'] += tmp_jump_res['stat']['testcases']['success']
            jump_res['stat']['testcases']['fail'] += tmp_jump_res['stat']['testcases']['fail']
            jump_res['stat']['teststeps']['total'] += tmp_jump_res['stat']['teststeps']['total']
            jump_res['stat']['teststeps']['failures'] += tmp_jump_res['stat']['teststeps']['failures']
            jump_res['stat']['teststeps']['errors'] += tmp_jump_res['stat']['teststeps']['errors']
            jump_res['stat']['teststeps']['skipped'] += tmp_jump_res['stat']['teststeps']['skipped']
            jump_res['stat']['teststeps']['expectedFailures'] += tmp_jump_res['stat']['teststeps']['expectedFailures']
            jump_res['stat']['teststeps']['unexpectedSuccesses'] += tmp_jump_res['stat']['teststeps']['unexpectedSuccesses']
            jump_res['stat']['teststeps']['successes'] += tmp_jump_res['stat']['teststeps']['successes']
            if index == 0:
                jump_res['time']['start_at'] = tmp_jump_res['time']['start_at']
                jump_res['time']['start_datetime'] = tmp_jump_res['time']['start_datetime']
            jump_res['time']['duration']  += tmp_jump_res['time']['duration']
            jump_res['details'] += tmp_jump_res['details']
            scheduler.app.logger.info('执行后等待时间：{}'.format(case['config']['variables']['wait_times'] / 1000))
        summary = json.dumps(jump_res, ensure_ascii=False, default=encode_object, cls=JSONEncoder)
        return summary
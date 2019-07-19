
import json
import logging
import sys
import ssl
from urllib.parse import urlparse

import xlrd


def convert_list_to_dict(origin_list):
    """ convert HAR data list to mapping
    @param (list) origin_list
        [
            {"name": "v", "value": "1"},
            {"name": "w", "value": "2"}
        ]
    @return (dict)
        {"v": "1", "w": "2"}
    """
    return {
        item["name"]: item["value"]
        for item in origin_list
    }


def load_api_log_entries(file_path, file_type):
    """
    """
    with open(file_path, "r+", encoding="utf-8") as f:
        try:
            content_json = json.loads(f.read())
            if file_type == 'har':
                if content_json["log"]["entries"]:
                    return content_json["log"]["entries"]
                else:
                    raise  KeyError ({'msg': '文件内容缺少entries节点，请检查后重新上传', 'status': 0})
            elif file_type == 'json':
                if content_json['item']:
                    return content_json['item']
                else:
                    raise KeyError ({'msg': '文件内容缺少item节点，请检查后重新上传', 'status': 0})
        #except (KeyError, TypeError):
        except (KeyError, TypeError) :
            #logging.error("api_1_0 file content error: {}".format(file_path))
            raise KeyError({'msg': '文件内容解析错误，请检查后重新上传', 'status': 0})
            #sys.exit(1)


class HarParser(object):
    IGNORE_REQUEST_HEADERS = [
        "host",
        "accept",
        "content-length",
        "connection",
        "accept-encoding",
        "accept-language",
        "origin",
        "referer",
        "cache-control",
        "pragma",
        "cookie",
        "upgrade-insecure-requests",
        ":authority",
        ":method",
        ":scheme",
        ":path"
    ]

    def __init__(self, file_path, file_type='har'):
        try:
            self.log_entries = load_api_log_entries(file_path, file_type)
            self.user_agent = None
            self.file_type = file_type
            self.testset = self.make_testset()
        except KeyError as e:
            raise Exception(e)

    def _make_har_request_url(self, testcase_dict, entry_json):
        """ parse HAR entry request url and queryString, and make testcase url and params
        """
        request_params = convert_list_to_dict(entry_json["request"].get("queryString", []))

        url = entry_json["request"].get("url")
        if not url:
            logging.exception("url missed in request.")
            sys.exit(1)
        parsed_object = urlparse(url)
        if request_params:
            testcase_dict["param"] = json.dumps(
                [{'key': k, 'value': v, 'param_type': 'string'} for k, v in request_params.items()])

        testcase_dict["status_url"] = parsed_object.netloc
        testcase_dict["url"] = parsed_object.path
        testcase_dict["name"] = parsed_object.path

    def _make_json_data(self, testcase_dict, entry_json):
        testcase_dict['name'] = entry_json['name']
        request = entry_json['request']
        testcase_dict['method'] = request.get('method', 'GET')
        uri = request['url']
        # if not entry_json['url'].startswith('http'):
        #     entry_json['url'] = 'http://' + entry_json['url']
        url = urlparse(uri['raw'])
        testcase_dict['url'] = uri['raw']
        if url.netloc:
            testcase_dict['status_url'] = url.netloc
        else:
            testcase_dict['status_url'] = url.scheme

        hed = request.get('header', None)
        if hed:
            testcase_dict['header'] = json.dumps(
                [{'key': h['key'], 'value': h['value']} for h in hed if h])
        if testcase_dict['method'] == 'GET':
            query = uri.get('query', None)
            if query:
                testcase_dict['param'] = json.dumps(
                    [{'key': h1['key'], 'value': h1['value'], 'param_type': 'string'} for h1 in
                     query if h1])
        elif testcase_dict['method'] == 'POST':
            postParams: dict = request['body']
            mode = postParams.get('mode', None)
            if mode is 'data':
                testcase_dict['variable'] = json.dumps(
                    [{'key': h1['key'], 'value': h1['value'], 'param_type': 'string'} for h1 in
                     entry_json['data'] if h1])
            elif 'raw' in postParams:
                testcase_dict['variable_type'] = 'json'
                testcase_dict['json_variable'] = postParams['raw']

    def _make_har_request_headers(self, testcase_dict, entry_json):
        """ parse HAR entry request headers, and make testcase headers.
        """
        testcase_headers = []
        for header in entry_json["request"].get("header", []):
            if header["name"].lower() in self.IGNORE_REQUEST_HEADERS:
                continue
            if header["name"].lower() == "user-agent":
                if not self.user_agent:
                    self.user_agent = header["value"]
                continue
            testcase_headers.append({'key': header["name"], 'value': header["value"]})

        testcase_dict["header"] = json.dumps(testcase_headers)

    def _make_har_request_data(self, testcase_dict, entry_json):
        """ parse HAR entry request data, and make testcase request data
        """
        method = entry_json["request"].get("method")
        if not method:
            logging.exception("method missed in request.")
            sys.exit(1)

        testcase_dict["method"] = method
        if method in ["POST", "PUT"]:
            mimeType = entry_json["request"].get("postData", {}).get("mimeType")

            # Note that text and params fields are mutually exclusive.
            params = entry_json["request"].get("postData", {}).get("params", [])
            text = entry_json["request"].get("postData", {}).get("text")
            if text:
                post_data = text
            else:
                post_data = convert_list_to_dict(params)

            request_data_key = "data"
            if not mimeType:
                pass
            elif mimeType.startswith("application/json"):
                post_data = json.loads(post_data)
                request_data_key = "json"
            elif mimeType.startswith("application/x-www-form-urlencoded"):
                # post_data = utils.x_www_form_urlencoded(post_data)
                pass
            else:
                # TODO: make compatible with more mimeType
                pass
            testcase_dict["variable_type"] = request_data_key
            if request_data_key == 'json':
                testcase_dict["json_variable"] = json.dumps(post_data)
            else:
                testcase_dict["variable"] = json.dumps([
                    {'key': k, 'value': v, 'param_type': 'string'} for k, v in post_data.items()])

    def make_testcase(self, entry_json):
        """ extract info from entry dict and make testcase
        """
        testcase_dict = {
            "url": '',
            "name": "待定",
            "header": '[]',
            "method": 'POST',
            "variable_type": 'data',
            "variable": '[]',
            "extract": '[]',
            "validate": '[]',
            "param": '[]',
        }
        if self.file_type == 'har':
            self._make_har_request_url(testcase_dict, entry_json)
            self._make_har_request_headers(testcase_dict, entry_json)
            self._make_har_request_data(testcase_dict, entry_json)
            return testcase_dict
        elif self.file_type == 'json':
            self._make_json_data(testcase_dict, entry_json)
            return testcase_dict

    def make_testcases(self):
        """ extract info from HAR log entries list and make testcase list
        """
        testcases = []
        for entry_json in self.log_entries:
            try:
                case = self.make_testcase(entry_json)
                testcases.append(case)
            except Exception as e:
                print("Couldn't parse!!" + str(e))

        return testcases

    def make_testset(self):
        """ Extract info from HAR file and prepare for testcase
        """
        logging.debug("Extract info from HAR file and prepare for testcase.")
        testset = self.make_testcases()
        # config = self.make_config()
        # testset.insert(0, config)
        return testset


class CaseStepTmp():
    caseStepId = ''
    caseStepname = ''
    caseStepId = ''
    caseStepDesc = ''
    resourceid = ''
    xPath = ''
    text = ''
    action = ''
    param = ''


class CaseTmp():
    caseName = ''
    caseDesc = ''
    platform = ''
    caseSteps = []


class Excelparser:
    '''excel格式uicase解析'''

    def __init__(self, file_path):
        ''''''
        self.excelFile = xlrd.open_workbook(file_path)
        self.cases = self.parse()

    def data(self):
        return self.cases

    def parse(self):
        cases = []
        if not self.excelFile:
            print('未找到指定文件')
        for sheet in self.excelFile.sheets():
            '''遍历每一个sheet'''
            case = CaseTmp()
            case.caseName = str(sheet.cell_value(0, 1))
            case.caseDesc = str(sheet.cell_value(1, 1))
            case.platform = str(sheet.cell_value(2, 1))
            for r in range(4, sheet.nrows):
                caseStep = CaseStepTmp()
                caseStep.caseStepname = str(sheet.cell_value(r, 3))
                caseStep.caseStepDesc = str(sheet.cell_value(r, 4))
                caseStep.resourceid = str(sheet.cell_value(r, 5)).strip()
                caseStep.xPath = str(sheet.cell_value(r, 6)).strip()
                caseStep.text = float2Str(sheet.cell_value(r, 7))
                caseStep.action = str(sheet.cell_value(r, 8)).strip()
                caseStep.param = float2Str(sheet.cell_value(r, 9))
                case.caseSteps.append(caseStep)
            cases.append(case)
        return cases


def float2Str(param):
    if isinstance(param, float):
        return str('%d' % param)
    return param


if __name__ == '__main__':
    har_parser = HarParser('test.har')
    print(har_parser.testset)

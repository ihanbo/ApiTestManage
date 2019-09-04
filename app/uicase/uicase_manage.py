import os
from time import strftime

from flask import jsonify, request, Response, make_response

from app.api_1_0 import api, login_required
from app.models import *
from app.uicase import ui_case_run
from app.util.case_change.core import Excelparser
from ..util.utils import *


@api.route('/uicases/add', methods=['POST'])
@login_required
def add_uicase():
    """ 接口信息增加、编辑 """
    data = request.json
    project_name = data.get('projectName')
    module_id = data.get('moduleId')

    caseId = data.get('caseId')
    caseName = data.get('caseName')
    desc = data.get('desc')
    platform = data.get('platform')
    steps = data.get('steps')

    if not project_name:
        return jsonify({'msg': '项目不能为空', 'status': 0})
    if not module_id:
        return jsonify({'msg': '模块不能为空', 'status': 0})
    if not caseName:
        return jsonify({'msg': 'case名称不能为空', 'status': 0})
    if not platform:
        return jsonify({'msg': '操作平台不能为空', 'status': 0})
    if not steps:
        return jsonify({'msg': '步骤不能为空', 'status': 0})

    project_id = UI_Project.query.filter_by(name=project_name).first().id
    num = auto_num(data.get('num'), UICase, module_id=module_id)

    if caseId:
        old_data = UICase.query.filter_by(id=caseId).first()
        old_num = old_data.num
        if UICase.query.filter_by(name=caseName,
                                  module_id=module_id).first() and caseName != old_data.name:
            return jsonify({'msg': '名字重复', 'status': 0})

        list_data = UI_CaseSort.query.filter_by(id=module_id).first().ui_cases.all()
        num_sort(num, old_num, list_data, old_data)
        old_data.project_id = project_id
        old_data.module_id = module_id
        old_data.name = caseName
        old_data.desc = desc
        old_data.platform = platform

        db.session.commit()
        updateUICaseInfo(caseId, steps)
        return jsonify({'msg': '修改成功', 'status': 1, 'caseId': caseId, 'num': num})
    else:
        if UICase.query.filter_by(name=caseName, module_id=module_id).first():
            return jsonify({'msg': '名字重复', 'status': 0})
        else:
            new_cases = UICase(num=num,
                               name=caseName,
                               desc=desc,
                               platform=platform,
                               project_id=project_id,
                               module_id=module_id)
            db.session.add(new_cases)
            db.session.commit()
            updateUICaseInfo(new_cases.id, steps)
            return jsonify(
                {'msg': '新建成功', 'status': 1, 'caseId': new_cases.id, 'num': new_cases.num})

# 导入case信息，报错录屏内容到数据库，直接运行录屏内容
@api.route('/uicases/import', methods=['POST'])
@login_required
def import_uicase():
    """ 导入case信息 """
    data = request.json
    project_name = data.get('projectName')
    module_id = data.get('moduleId')
    caseId = data.get('caseId')
    caseName = data.get('caseName')
    desc = data.get('desc')
    platform = data.get('platform')
    contentText = data.get('contentText')

    if not project_name:
        return jsonify({'msg': '项目不能为空', 'status': 0})
    if not module_id:
        return jsonify({'msg': '模块不能为空', 'status': 0})
    if not caseName:
        return jsonify({'msg': 'case名称不能为空', 'status': 0})
    if not platform:
        return jsonify({'msg': '操作平台不能为空', 'status': 0})
    if not contentText:
        return jsonify({'msg': '录屏内容不能为空', 'status': 0})

    project_id = UI_Project.query.filter_by(name=project_name).first().id
    num = auto_num(data.get('num'), UICase, module_id=module_id)

    if caseId:
        old_data = UICase.query.filter_by(id=caseId).first()
        old_num = old_data.num
        if UICase.query.filter_by(name=caseName,
                                  module_id=module_id).first() and caseName != old_data.name:
            return jsonify({'msg': '名字重复', 'status': 0})

        list_data = UI_CaseSort.query.filter_by(id=module_id).first().ui_cases.all()
        num_sort(num, old_num, list_data, old_data)
        old_data.project_id = project_id
        old_data.module_id = module_id
        old_data.name = caseName
        old_data.desc = desc
        old_data.platform = platform

        db.session.commit()
        # updateUICaseInfo(caseId, steps)
        updateUiCaseImportInfo(caseId, contentText)
        return jsonify({'msg': '修改成功', 'status': 1, 'caseId': caseId, 'num': num})
    else:
        if UICase.query.filter_by(name=caseName, module_id=module_id).first():
            return jsonify({'msg': '名字重复', 'status': 0})
        else:
            new_cases = UICase(num=num,
                               name=caseName,
                               desc=desc,
                               platform=platform,
                               project_id=project_id,
                               module_id=module_id)
            db.session.add(new_cases)
            db.session.commit()

            updateUiCaseImportInfo(new_cases.id, contentText)
            # updateUICaseInfo(new_cases.id, steps)
            return jsonify(
                {'msg': '新建成功', 'status': 1, 'caseId': new_cases.id, 'num': new_cases.num})


def updateUiCaseImportInfo(id, contentText):
    for d in UicaseStepInfo.query.filter_by(ui_case_id=id).all():
        db.session.delete(d)
    importInfo = UicaseStepInfo( ui_case_id=id, num=0, contentText=contentText, ui_type=1 )
    db.session.add(importInfo)
    db.session.commit()


def updateUICaseInfo(id, steps):
    for d in UicaseStepInfo.query.filter_by(ui_case_id=id).all():
        db.session.delete(d)

    num = 0
    for s in steps:
        info = UicaseStepInfo(ui_case_step_id=s.get('id'), ui_case_id=id, num=num)
        db.session.add(info)
        db.session.commit()
        num += 1


@api.route('/uicases/list', methods=['POST'])
def list_uicase():
    """ 查接口信息 """
    data = request.json
    module_id = data.get('moduleId')
    project_name = data.get('projectName')
    case_name = data.get('caseStepName')
    platform = data.get('platform')
    page = data.get('page') if data.get('page') else 1
    per_page = data.get('sizePage') if data.get('sizePage') else 20
    if not project_name:
        return jsonify({'msg': '请选择项目', 'status': 0})
    if not platform:
        return jsonify({'msg': '请先选择操作系统'.format(project_name), 'status': 0})

    if case_name:
        if module_id:
            case_data = UICase.query.filter_by(module_id=module_id, platform=platform).filter(
                UICase.name.like('%{}%'.format(case_name)))
        else:
            case_data = UICase.query.filter_by(platform=platform).filter(
                UICase.name.like('%{}%'.format(case_name)))
        # total = len(case_data)
        if not case_data:
            return jsonify({'msg': '没有该用例信息', 'status': 0})
    elif not module_id:
        case_data = UICase.query.filter_by(platform=platform)
    else:
        case_data = UICase.query.filter_by(module_id=module_id, platform=platform)
    pagination = case_data.order_by(UICase.id.desc()).paginate(page, per_page=per_page,
                                                               error_out=False)
    case_data = pagination.items
    total = pagination.total
    _api = [{'id': c.id,
             'num': c.num,
             'name': c.name,
             'desc': c.desc,
             'type': UicaseStepInfo.query.filter_by(ui_case_id=c.id).first().ui_type,
             'c_steps': len(UicaseStepInfo.query.filter_by(ui_case_id=c.id).all())}
            for c in case_data]
    return jsonify({'data': _api, 'total': total, 'status': 1})


@api.route('/uicases/delStep', methods=['POST'])
def del_step_in_uicase():
    """ 删除case中的step"""
    data = request.json
    case_id = data.get('id')
    _data = UicaseStepInfo.query.filter_by(id=case_id).first()
    db.session.delete(_data)
    return jsonify({'msg': '删除成功', 'status': 1})


@api.route('/uicases/delete', methods=['POST'])
def del_uicases():
    """ 删除case"""
    data = request.json
    case_id = data.get('id')
    _data = UICase.query.filter_by(id=case_id).first()

    # project_id = UI_Module.query.filter_by(id=_data.module_id).first().project_id
    # if current_user.id != UI_Project.query.filter_by(id=project_id).first().user_id:
    #     return jsonify({'msg': '不能删除别人项目下的case', 'status': 0})

    # 同步删除接口信息下对应用例下的步骤信息
    for d in UicaseStepInfo.query.filter_by(ui_case_id=case_id).all():
        db.session.delete(d)

    db.session.delete(_data)

    return jsonify({'msg': '删除成功', 'status': 1})


@api.route('/uicases/editAndCopy', methods=['POST'])
def edit_uicases():
    """ 编辑case"""
    data = request.json
    case_id = data.get('id')
    type = data.get('type')
    if type == 0:
        _edit = UICase.query.filter_by(id=case_id).first()
        _steps = UicaseStepInfo.query.filter_by(ui_case_id=case_id).all()
        _steps_data = []
        for s in _steps:
            c = UICaseStep.query.filter_by(casesort_id=_edit.casesort_id, platform=_edit.platform,
                                           id=s.ui_case_step_id).first()
            _steps_data.append({'id': c.id,
                                'num': c.num,
                                'name': c.name,
                                'desc': c.desc})

        platform = Platform.query.filter_by(id=_edit.platform).first()
        _data = {'name': _edit.name,
                 'num': _edit.num,
                 'desc': _edit.desc,
                 'id': _edit.id,
                 'platform': platform.to_dict(),
                 'steps': _steps_data}
        return jsonify({'data': _data, 'status': 1})
    elif type == 1:
        _edit = UICase.query.filter_by(id=case_id).first()
        platform = Platform.query.filter_by(id=_edit.platform).first()
        _data = {'name': _edit.name,
                 'num': _edit.num,
                 'desc': _edit.desc,
                 'id': _edit.id,
                 'platform': platform.to_dict(),
                 'contentText': UicaseStepInfo.query.filter_by(ui_case_id=case_id).first().contentText}
        return jsonify({'data': _data, 'status': 1})
    else:
        return jsonify({'msg': '参数错误，请联系管理员查看解决', 'status': 0})


@api.route('/uicases/run_ui_case', methods=['POST'])
def run_ui_cases():
    """ run case"""
    data = request.json
    case_id = data.get('id')
    type = data.get('type')
    if type == 0 :
        _udid = data.get('udid', '00008020-001E11502E04002E')
        _device_name = data.get('device_name', '苹果设备')
        _case = UICase.query.filter_by(id=case_id).first()
        _project: UI_Project = UI_Project.query.filter_by(id=_case.project_id).first()
        _steps = UicaseStepInfo.query.filter_by(ui_case_id=case_id).all()
        _steps_data = []
        for s in _steps:
            c: UICaseStep = UICaseStep.query.filter_by(casesort_id=_case.casesort_id,
                                                       platform=_case.platform,
                                                       id=s.ui_case_step_id).first()
            st = {}
            st.update(c.__dict__)
            st['action'] = c.ui_action.action
            _steps_data.append(st)

        if _steps_data is None:
            return jsonify({'msg': '未找到用例信息', 'status': 0})

        # return jsonify({'msg': 'ok', 'status': 1})
        succ, desc = ui_case_run.try_start_test(platform=_case.platform,
                                                module_id=_case.module_id,
                                                project_id=_case.project_id,
                                                device_name=_device_name,
                                                udid=_udid,
                                                func_file=_project.func_file,
                                                test_time=strftime("%Y-%m-%d_%H-%M-%S"),
                                                android_launch=_project.android_launch,
                                                android_package=_project.android_package,
                                                single_test={'case': _case.__dict__,
                                                             'steps': _steps_data},
                                                ios_bundle_id=_project.ios_bundle_id)
        return jsonify({'msg': desc, 'status': 1 if succ else 0})
    elif type == 1:
        _udid = data.get('udid', '00008020-001E11502E04002E')
        _device_name = data.get('device_name', '苹果设备')
        _case = UICase.query.filter_by(id=case_id).first()
        _project: UI_Project = UI_Project.query.filter_by(id=_case.project_id).first()
        _step = UicaseStepInfo.query.filter_by(ui_case_id=case_id).first()
        # 录屏内容contentText
        if  _step:
            contentText = _step.contentText
            if contentText is None:
                return jsonify({'msg': '未找到用例信息', 'status': 0})
            succ, desc = ui_case_run.try_start_test(platform=_case.platform,
                                                    module_id=_case.module_id,
                                                    project_id=_case.project_id,
                                                    device_name=_device_name,
                                                    udid=_udid,
                                                    func_file=_project.func_file,
                                                    test_time=strftime("%Y-%m-%d_%H-%M-%S"),
                                                    android_launch=_project.android_launch,
                                                    android_package=_project.android_package,
                                                    content_test={
                                                        'case': _case.__dict__,
                                                        'contentText': contentText},
                                                    ios_bundle_id=_project.ios_bundle_id)
            return jsonify({'msg': desc, 'status': 1 if succ else 0})
        else:
            return jsonify({'msg': '未找到用例信息', 'status': 0})
    else:
        return jsonify({'msg': '参数错误，请联系管理员解决', 'status': 0})


@api.route('/uicases/get_devices', methods=['POST', 'GET'])
def get_devices():
    """ 获取连接设备信息 """
    data = request.json
    platform = data.get('platform')
    is_free = data.get('is_free')
    if platform == 1:
        _devs = get_android_devices(is_free)
    elif platform == 2:
        _devs = get_ios_devices(is_free)
    elif platform == 3:
        _devs_and = get_android_devices(is_free)
        _devs_ios = get_ios_devices(is_free)
        _devs = {'android': _devs_and, 'ios': _devs_ios}
    else:
        return jsonify({'msg': '未识别的平台', 'status': 0})
    return jsonify({'msg': '获取成功', 'data': _devs, 'status': 1})


def get_android_devices(free: bool) -> list:
    """
    :param free: 是否空闲
    :return:[{decice:xxx,name:xxx,state:xxx}]
    """
    rs: str = os.popen(
        'adb devices').read()
    result = []
    if rs:
        _ss: list = rs.split('\n')[1:-2]
        rs = map(lambda item: item[:item.index('\t')], _ss)
        _ss = list(rs)
        if free:
            if ui_case_run.running_devices:
                tmp = list(ui_case_run.running_devices.keys())
                _ss = [x for x in _ss if x not in tmp]
        for device in _ss:
            model = os.popen(f'adb -s {device} shell getprop ro.product.model').read()
            state = '空闲' if free else ui_case_run.running_devices.get(device, '空闲')
            result.append({'device': device, 'name': model[:-1], 'state': state})

    return result


def get_ios_devices(free: bool) -> list:
    """
    :param free: 是否空闲
    :return:
    """
    rs: str = os.popen(
        'idevice_id -l').read()
    if rs:
        _ss: list = rs.split('\n')
        _ss = _ss[:-1]

        if free:
            if ui_case_run.running_devices:
                runing_device = ui_case_run.running_devices.keys()
                _ss = [x for x in _ss if x not in runing_device]
        mm = map(lambda device: {'device': device, 'name': '苹果设备',
                                 'state': '空闲' if free else ui_case_run.running_devices.get(device,
                                                                                            '空闲')},
                 _ss)
        return list(mm)
    return []


def importSteps(case_id, caseSteps, project_id, module_id, platform_id):
    for d in UicaseStepInfo.query.filter_by(ui_case_id=case_id).all():
        db.session.delete(d)

    num = auto_num(0, UICaseStep, module_id=module_id)
    numInCase = 0
    for step in caseSteps:
        new_case_step = UICaseStep(num=num,
                                   name=step.caseStepname,
                                   desc=step.caseStepDesc,
                                   xpath=step.xPath,
                                   resourceid=step.resourceid,
                                   text=step.text,
                                   action=UIAction.query.filter_by(action=step.action).first().id,
                                   extraParam=step.param,
                                   platform=platform_id,
                                   project_id=project_id,
                                   module_id=module_id)
        db.session.add(new_case_step)
        db.session.commit()

        info = UicaseStepInfo(ui_case_step_id=new_case_step.id, ui_case_id=case_id, num=numInCase)
        db.session.add(info)
        db.session.commit()
        num += 1
        numInCase += 1


@api.route('/uicases/image', methods=['GET'])
def get_image():
    # mdict = {
    #     'jpeg': 'image/jpeg',
    #     'jpg': 'image/jpeg',
    #     'png': 'image/png',
    #     'gif': 'image/gif'
    # }
    # mime = mdict[((uri.split('/')[1]).split('.')[1])]

    path = os.path.abspath(os.path.join(os.getcwd(), ".."))  # 获取父级路径的上一级目录路径
    path = path + "/reports/1.png"
    with open(path, 'rb') as f:
        image = make_response(f.read())
        resp = Response(image, mimetype="image/png")
        return resp
    return jsonify({'msg': 'ooooooooooo', 'status': 0})


@api.route('/uicases/importCases', methods=['POST'])
def import_uicases():
    """ 导入case，目前仅支持excel"""
    data = request.json
    project_name = data.get('projectName')
    module_id = data.get('moduleId')
    if not module_id and not project_name:
        return jsonify({'msg': '项目和模块不能为空', 'status': 0})
    project_data = UI_Project.query.filter_by(name=project_name).first()

    import_api_address = data.get('importApiAddress')

    excel = Excelparser(import_api_address).data()
    num = auto_num(0, UICase, module_id=module_id)
    for caseImport in excel:
        oldCase = UICase.query.filter_by(name=caseImport.caseName).first()
        if oldCase:
            return jsonify({'msg': 'case已存在', 'status': 0})
        platform = Platform.query.filter_by(p_name=caseImport.platform).first()
        new_cases = UICase(num=num,
                           name=caseImport.caseName,
                           desc=caseImport.caseDesc,
                           platform=platform.id,
                           project_id=project_data.id,
                           module_id=module_id)
        db.session.add(new_cases)
        db.session.commit()
        num += 1
        importSteps(new_cases.id, caseImport.caseSteps, project_data.id, module_id, platform.id)

    if not import_api_address:
        return jsonify({'msg': '请上传文件', 'status': 0})
    return jsonify({'msg': '导入成功', 'status': 1})

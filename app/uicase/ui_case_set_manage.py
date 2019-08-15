import os
from time import strftime

from flask import jsonify, request, Response, make_response

from app.api_1_0 import api, login_required
from app.models import *
from app.uicase import ui_case_run
from app.util.case_change.core import Excelparser
from ..util.utils import *


@api.route('/uicase_set/add', methods=['POST'])
@login_required
def add_uicase_set():
    """ caseset增加、编辑 """
    data = request.json
    project_name = data.get('projectName')
    caseSetId = data.get('caseSetId')
    caseSetName = data.get('caseSetName')
    caseSetDesc = data.get('caseSetDesc')
    platform = data.get('platform')
    steps = data.get('steps')

    if not project_name:
        return jsonify({'msg': '项目不能为空', 'status': 0})
    if not caseSetName:
        return jsonify({'msg': '名称不能为空', 'status': 0})
    if not platform:
        return jsonify({'msg': '操作系统不能为空', 'status': 0})
    if not steps:
        return jsonify({'msg': '步骤不能为空', 'status': 0})

    project_id = UI_Project.query.filter_by(name=project_name).first().id
    num = auto_num(data.get('num'), UI_CaseSet, project_id=project_id)

    if caseSetId:
        old_data = UI_CaseSet.query.filter_by(id=caseSetId).first()
        old_num = old_data.num
        if UI_CaseSet.query.filter_by(name=caseSetName).first() and caseSetName != old_data.name:
            return jsonify({'msg': '名字重复', 'status': 0})

        old_data.project_id = project_id
        old_data.name = caseSetName
        old_data.desc = caseSetDesc
        old_data.platform = platform
        db.session.commit()

        updateUICaseInfo(caseSetId, steps)
        return jsonify({'msg': '修改成功', 'status': 1, 'caseId': caseSetId, 'num': num})
    else:
        if UI_CaseSet.query.filter_by(name=caseSetName).first():
            return jsonify({'msg': '名字重复', 'status': 0})
        else:
            new_cases = UI_CaseSet(num=num,
                                   name=caseSetName,
                                   desc=caseSetDesc,
                                   platform=platform,
                                   project_id=project_id)
            db.session.add(new_cases)
            db.session.commit()
            updateUICaseInfo(new_cases.id, steps)
            return jsonify(
                {'msg': '新建成功', 'status': 1, 'caseId': new_cases.id, 'num': new_cases.num})


def updateUICaseInfo(id, steps):
    """ case步骤 """
    for d in UI_Case_CaseSet.query.filter_by(caseset_id=id).all():
        db.session.delete(d)

    num = 0
    for s in steps:
        info = UI_Case_CaseSet(case_id=s.get('id'), caseset_id=id, num=num)
        db.session.add(info)
        db.session.commit()
        num += 1


@api.route('/uicase_set/list', methods=['POST'])
def list_uicase_set():
    """ 查接口信息 """
    data = request.json
    project_name = data.get('projectName')
    case_set_name = data.get('caseSetName')
    platform = data.get('platform')
    page = data.get('page') if data.get('page') else 1
    per_page = data.get('sizePage') if data.get('sizePage') else 20

    project_id = UI_Project.query.filter_by(name=project_name).first().id
    if not project_name or not project_id:
        return jsonify({'msg': '请先选择项目', 'status': 0})
    if not platform:
        return jsonify({'msg': '请先选择操作系统'.format(project_name), 'status': 0})

    if case_set_name:
        case_data = UI_CaseSet.query.filter_by(project_id=project_id, platform=platform).filter(
            UI_CaseSet.name.like('%{}%'.format(case_set_name)))
        # total = len(case_data)
        if not case_data:
            return jsonify({'msg': '没有该用例集', 'status': 0})
    else:
        case_data = UI_CaseSet.query.filter_by(project_id=project_id, platform=platform)
    pagination = case_data.order_by(UI_CaseSet.num.asc()).paginate(page, per_page=per_page,
                                                                   error_out=False)
    case_data = pagination.items
    total = pagination.total
    _api = [{'id': c.id,
             'num': c.num,
             'name': c.name,
             'desc': c.desc,
             'c_steps': len(UI_Case_CaseSet.query.filter_by(caseset_id=c.id).all())}
            for c in case_data]
    return jsonify({'data': _api, 'total': total, 'status': 1})


@api.route('/uicase_set/delCase', methods=['POST'])
def del_case_step_in_caseset():
    """ 删除caseset中的case"""
    data = request.json
    _id = data.get('id')
    _data = UI_Case_CaseSet.query.filter_by(id=_id).first()
    db.session.delete(_data)
    return jsonify({'msg': '删除成功', 'status': 1})


@api.route('/uicase_set/delete', methods=['POST'])
def del_uicaseset():
    """ 删除caseset"""
    data = request.json
    _id = data.get('id')
    _data = UI_CaseSet.query.filter_by(id=_id).first()

    project_id = UI_Module.query.filter_by(id=_data.module_id).first().project_id
    # if current_user.id != UI_Project.query.filter_by(id=project_id).first().user_id:
    #     return jsonify({'msg': '不能删除别人项目下的case', 'status': 0})

    # 同步删除接口信息下对应用例下的步骤信息
    for d in UI_Case_CaseSet.query.filter_by(caseset_id=_id).all():
        db.session.delete(d)
    db.session.delete(_data)

    return jsonify({'msg': '删除成功', 'status': 1})


@api.route('/uicase_set/editAndCopy', methods=['POST'])
def edit_uicaseset():
    """ 编辑caseset"""
    data = request.json
    caseSet_id = data.get('id')
    _edit = UI_CaseSet.query.filter_by(id=caseSet_id).first()
    _case_caseset = UI_Case_CaseSet.query.filter_by(caseset_id=caseSet_id).all()
    _cases_data = []
    for s in _case_caseset:
        c = UICase.query.filter_by(project_id=_edit.project_id, platform=_edit.platform,
                                   id=s.case_id).first()
        _cases_data.append({'id': c.id,
                            'num': c.num,
                            'name': c.name,
                            'desc': c.desc})

    platform = Platform.query.filter_by(id=_edit.platform).first()
    _data = {'name': _edit.name,
             'num': _edit.num,
             'desc': _edit.desc,
             'id': _edit.id,
             'num': _edit.num,
             'platform': platform.to_dict(),
             # 'steps': json.loads(json.dumps(_steps_data, default=info2dic))}
             'steps': _cases_data}
    return jsonify({'data': _data, 'status': 1})


@api.route('/uicase_set/run_caseset', methods=['POST'])
def run_ui_caseset():
    """ run case"""
    data = request.json
    caseset_id = data.get('id')
    _caseset: UI_CaseSet = UI_CaseSet.query.filter_by(id=caseset_id).first()
    _project: UI_Project = UI_Project.query.filter_by(id=_caseset.project_id).first()
    _caseset_cases = UI_Case_CaseSet.query.filter_by(caseset_id=caseset_id).all()
    _cases_data = []
    for s in _caseset_cases:
        casedata = assemble_case_with_step(s.case_id)
        # c: UICase = UICase.query.filter_by(platform=_caseset.platform,
        #                                            id=s.case_id).first()
        _cases_data.append(casedata)

    if not _cases_data:
        return jsonify({'msg': '未找到用例', 'status': 0})
    caseset_test = {'name': _caseset.name, 'desc': _caseset.desc, 'cases': _cases_data}

    succ, desc = ui_case_run.try_start_test(platform=_caseset.platform,
                                   udid=data.get('udid'),
                                   android_launch=_project.android_launch,
                                   android_package=_project.android_package,
                                   ios_bundle_id=_project.ios_bundle_id,
                                   caseset_test=caseset_test)

    # if succ:
    #     ui_case_run.run_ui_cases(_case.__dict__, _steps_data)
    return jsonify({'msg': desc, 'status': 1 if succ else 0})


def assemble_case_with_step(case_id) -> dict:
    _case = UICase.query.filter_by(id=case_id).first()
    _steps = UicaseStepInfo.query.filter_by(ui_case_id=case_id).all()
    _steps_data = []
    for s in _steps:
        c: UICaseStep = UICaseStep.query.filter_by(module_id=_case.module_id,
                                                   platform=_case.platform,
                                                   id=s.ui_case_step_id).first()
        st = {}
        st.update(c.__dict__)
        st['action'] = c.ui_action.action
        _steps_data.append(st)
    return {'case': _case, 'steps': _steps_data}
#
#

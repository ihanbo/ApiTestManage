import json

from flask import jsonify, request
from flask_login import current_user

from app.api_1_0 import api
from app.models import *
from app.util.custom_decorator import login_required
from app.util.utils import auto_num, num_sort


@api.route('/uicasestep/add', methods=['POST'])
@login_required
def add_uicase_step():
    """ 接口信息增加、编辑 """
    data = request.json
    project_name = data.get('projectName')
    module_id = data.get('moduleId')

    caseStepId = data.get('caseStepId')
    caseStepName = data.get('caseStepName')
    desc = data.get('desc')
    platform = data.get('platform')

    xpath = data.get('xpath')
    resourceid = data.get('resourceid')
    text = data.get('text')
    ui_selector = data.get('ui_selector')

    action_id = data.get('action_id')
    action_name = data.get('action_name')
    extraParam = data.get('extraParam')

    if not project_name:
        return jsonify({'msg': '项目不能为空', 'status': 0})
    if not module_id:
        return jsonify({'msg': '模块不能为空', 'status': 0})
    if not caseStepName:
        return jsonify({'msg': '名称不能为空', 'status': 0})
    if not platform:
        return jsonify({'msg': '操作系统不能为空', 'status': 0})
    if action_name == 'click' or action_name == 'input':
        if not resourceid and not xpath and not text and not ui_selector:
            return jsonify({'msg': '元素id，元素路径，元素文本至少填写一种', 'status': 0})
    if not action_id:
        return jsonify({'msg': '元素行为必须填写', 'status': 0})

    project_id = UI_Project.query.filter_by(name=project_name).first().id
    num = auto_num(data.get('num'), UICaseStep, module_id=module_id)

    if caseStepId:
        old_data = UICaseStep.query.filter_by(id=caseStepId).first()
        old_num = old_data.num
        if UICaseStep.query.filter_by(name=caseStepName,
                                      module_id=module_id).first() and caseStepName != old_data.name:
            return jsonify({'msg': '名字重复', 'status': 0})

        list_data = UI_Module.query.filter_by(id=module_id).first().ui_case_steps.all()
        num_sort(num, old_num, list_data, old_data)
        old_data.project_id = project_id
        old_data.module_id = module_id
        old_data.name = caseStepName
        old_data.desc = desc
        old_data.extraParam = extraParam
        old_data.platform = platform
        old_data.xpath = xpath
        old_data.resourceid = resourceid
        old_data.text = text
        old_data.ui_selector = ui_selector
        old_data.action = action_id

        db.session.commit()
        return jsonify({'msg': '修改成功', 'status': 1, 'caseStepId': caseStepId, 'num': num})
    else:
        if UICaseStep.query.filter_by(name=caseStepName, module_id=module_id).first():
            return jsonify({'msg': '名字重复', 'status': 0})
        else:
            new_cases = UICaseStep(num=num,
                                   name=caseStepName,
                                   desc=desc,
                                   xpath=xpath,
                                   resourceid=resourceid,
                                   text=text,
                                   ui_selector=ui_selector,
                                   action=action_id,
                                   extraParam=extraParam,
                                   platform=platform,
                                   project_id=project_id,
                                   module_id=module_id)
            db.session.add(new_cases)
            db.session.commit()
            return jsonify(
                {'msg': '新建成功', 'status': 1, 'caseStepId': new_cases.id, 'num': new_cases.num})


@api.route('/uicasestep/delete', methods=['POST'])
@login_required
def del_uicase_step():
    """ 删除case """
    data = request.json
    case_step_id = data.get('id')
    _data = UICaseStep.query.filter_by(id=case_step_id).first()

    project_id = UI_Module.query.filter_by(id=_data.module_id).first().project_id
    # if current_user.id != UI_Project.query.filter_by(id=project_id).first().user_id:
    #     return jsonify({'msg': '不能删除别人项目下的接口', 'status': 0})

    # 同步删除接口信息下对应用例下的步骤信息
    for d in UicaseStepInfo.query.filter_by(ui_case_step_id=case_step_id).all():
        db.session.delete(d)

    db.session.delete(_data)

    return jsonify({'msg': '删除成功', 'status': 1})


@api.route('/uicasestep/list', methods=['POST'])
def list_uicase_step():
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
    if not module_id:
        return jsonify({'msg': '请先创建{}项目下的模块'.format(project_name), 'status': 0})
    if not platform:
        return jsonify({'msg': '请先选择操作平台'.format(project_name), 'status': 0})

    if case_name:
        case_data = UICaseStep.query.filter_by(module_id=module_id, platform=platform).filter(
            UICaseStep.name.like('%{}%'.format(case_name)))
        # total = len(case_data)
        if not case_data:
            return jsonify({'msg': '没有该接口信息', 'status': 0})
    else:
        case_data = UICaseStep.query.filter_by(module_id=module_id, platform=platform)
    pagination = case_data.order_by(UICaseStep.id.desc()).paginate(page, per_page=per_page,
                                                                   error_out=False)
    case_data = pagination.items
    total = pagination.total
    _api = [{'id': c.id,
             'num': c.num,
             'name': c.name,
             'desc': c.desc,
             'xpath': c.xpath,
             'resourceid': c.resourceid,
             'text': c.text,
             'action': c.action,
             'created_time': c.created_time,
             'update_time': c.update_time,
             'extraParam': c.extraParam, }
            for c in case_data]
    return jsonify({'data': _api, 'total': total, 'status': 1})


@api.route('/action/list', methods=['GET'])
def list_action():
    _data = UIAction.query.order_by(UIAction.id.asc()).all()
    plats = [{'id': c.id,
              'action': c.action,
              'action_name': c.action_name} for c in _data]
    return jsonify({'data': plats, 'status': 1})


@api.route('/uicasestep/editAndCopy', methods=['POST'])
@login_required
def edit_ui_case_step():
    """ 返回待编辑或复制的接口信息 """
    data = request.json
    case_id = data.get('id')
    _edit = UICaseStep.query.filter_by(id=case_id).first()
    platform = Platform.query.filter_by(id=_edit.platform).first()
    action = UIAction.query.filter_by(id=_edit.action).first()
    _data = {'name': _edit.name,
             'num': _edit.num,
             'desc': _edit.desc,
             'xpath': _edit.xpath,
             'text': _edit.text,
             'set_up': _edit.set_up,
             'tear_down': _edit.tear_down,
             'resourceid': _edit.resourceid,
             'ui_selector': _edit.ui_selector,
             'platform': platform.to_dict(),
             'action': action.action_to_dict(),
             'extraParam': _edit.extraParam}
    return jsonify({'data': _data, 'status': 1})

# 查询步骤信息 2019-11-20
@api.route('/uicasestep/queryUIcaseStep', methods=['POST'])
@login_required
def query_UIcase_Step():
    data = request.json
    module_id = data.get('moduleId')
    project_name = data.get('projectName')
    platform_id = data.get('platformId')
    page = data.get('page') if data.get('page') else 1
    per_page = data.get('sizePage') if data.get('sizePage') else 20

    porject_id = UI_Project.query.filter_by(name=project_name).first().id
    caseStep_data = UICaseStep.query.filter_by(module_id=module_id, platform=platform_id,project_id=porject_id)
    pagination = caseStep_data.order_by(UICaseStep.id.desc()).paginate(page, per_page=per_page,
                                                                   error_out=False)
    caseStep_data = pagination.items
    total = pagination.total
    # action信息
    action_data = UIAction.query.order_by(UIAction.id.asc()).all()
    _step = [{'id': c.id,
                 'num': c.num,
                 'name': c.name,
                 'desc': c.desc,
                 'xpath': c.xpath,
                 'resourceid': c.resourceid,
                 'text': c.text,
                 'action': UIAction.query.filter_by(id=c.action).first().action_name,
                 'action_id':c.action,
                 'created_time': c.created_time,
                 'update_time': c.update_time,
                 'extraParam': c.extraParam,
                 'expected_value': c.expected_value,
                 'isSet': False}
                for c in caseStep_data]
    return jsonify({'data': _step, 'total': total, 'status': 1})

# 删除步骤信息  2019-11-21
@api.route('/uicasestep/deleteUIcaseStep', methods=['POST'])
@login_required
def delete_UIcase_Step():
    data = request.json
    module_id = data.get('moduleId')
    project_name = data.get('projectName')
    platform_id = data.get('platformId')
    caseStep_id = data.get('caseStepId')
    # 获取项目id
    porject_id = UI_Project.query.filter_by(name=project_name).first().id

    _data = UICaseStep.query.filter_by(id=caseStep_id).first()

    if(_data):
        db.session.delete(_data)
        return jsonify({'msg': '删除成功', 'status': 1})
    else:
        return jsonify({'msg': '删除失败', 'status': 0})


# 添加步骤信息  2019-11-21
@api.route('/uicasestep/addUIcaseStep', methods=['POST'])
@login_required
def add_UIcase_Step():
    data = request.json
    id = data.get('id')
    name = data.get('name')
    xpath = data.get('xpath')
    action = data.get('action')
    extra_param = data.get('extraParam')
    expected_value = data.get('expected_value')
    module_id = data.get('moduleId')
    project_name = data.get('projectName')
    platform_id = data.get('platformId')

    # 获取项目id
    project_id = UI_Project.query.filter_by(name=project_name).first().id
    action_id = UIAction.query.filter_by(action_name = action).first().id
    num = auto_num(data.get('num'), UICaseStep, module_id=module_id,platform=platform_id,project_id=project_id)

    # 如果存在，就修改原步骤信息
    if id:
        old_data = UICaseStep.query.filter_by(id=id).first()
        old_num = old_data.num
        if UICaseStep.query.filter_by(name=name,module_id=module_id,platform=platform_id, project_id=project_id).first() and name != old_data.name:
            return jsonify({'msg': '名称重复，请重新输入', 'status': 0})
        # list_data = UI_Module.query.filter_by(id=module_id).first().ui_case_steps.all()
        # num_sort(num, old_num, list_data, old_data)
        old_data.project_id = project_id
        old_data.module_id = module_id
        old_data.name = name
        old_data.extraParam = extra_param
        old_data.platform = platform_id
        old_data.xpath = xpath
        old_data.action = action_id
        old_data.expected_value = expected_value

        db.session.commit()
        return jsonify({'msg': '修改成功', 'status': 1})
    else:
        if(UICaseStep.query.filter_by(module_id=module_id, platform=platform_id, project_id=project_id,name=name).first()):
            return jsonify({'msg': '名称重复，请重新输入', 'status': 0})
        new_caseStep = UICaseStep(num=num,
                               name=name,
                               xpath=xpath,
                               action=action_id,
                               extraParam=extra_param,
                               platform=platform_id,
                               project_id=project_id,
                               module_id=module_id,
                               expected_value=expected_value)
        db.session.add(new_caseStep)
        db.session.commit()
        return jsonify({'msg': '保存成功', 'status': 1})


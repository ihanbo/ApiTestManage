import json

from flask import jsonify, request
from flask_login import current_user

from app.api_1_0 import api
from app.models import *
from app.util.custom_decorator import login_required
from app.util.utils import auto_num, num_sort


@api.route('/uicase/add', methods=['POST'])
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

    xpath = data.get('xpath')
    resourceid = data.get('resourceid')
    text = data.get('text')

    action = data.get('action')
    extraParam = data.get('extraParam')

    if not project_name:
        return jsonify({'msg': '项目不能为空', 'status': 0})
    if not module_id:
        return jsonify({'msg': '模块不能为空', 'status': 0})
    if not caseName:
        return jsonify({'msg': '名称不能为空', 'status': 0})
    if not platform:
        return jsonify({'msg': '操作系统不能为空', 'status': 0})
    if not resourceid and not xpath and not text:
        return jsonify({'msg': '元素id，元素路径，元素文本至少填写一种', 'status': 0})
    if not action:
        return jsonify({'msg': '元素行为必须填写', 'status': 0})

    project_id = Project.query.filter_by(name=project_name).first().id
    num = auto_num(data.get('num'), UICase, module_id=module_id)

    if caseId:
        old_data = UICase.query.filter_by(id=caseId).first()
        old_num = old_data.num
        if UICase.query.filter_by(name=caseName, module_id=module_id).first() and caseName != old_data.name:
            return jsonify({'msg': '名字重复', 'status': 0})

        list_data = Module.query.filter_by(id=module_id).first().ui_cases.all()
        num_sort(num, old_num, list_data, old_data)
        old_data.project_id = project_id
        old_data.module_id = module_id
        old_data.name = caseName
        old_data.desc = desc
        old_data.extract = extraParam
        old_data.platform = platform
        old_data.xpath = xpath
        old_data.resourceid = resourceid
        old_data.text = text
        old_data.action = action

        db.session.commit()
        return jsonify({'msg': '修改成功', 'status': 1, 'api_msg_id': caseId, 'num': num})
    else:
        if UICase.query.filter_by(name=caseName, module_id=module_id).first():
            return jsonify({'msg': '名字重复', 'status': 0})
        else:
            new_cases = UICase(num=num,
                               name=caseName,
                               desc=desc,
                               xpath=xpath,
                               resourceid=resourceid,
                               text=text,
                               action=action,
                               extraParam=extraParam,
                               platform=platform,
                               project_id=project_id,
                               module_id=module_id)
            db.session.add(new_cases)
            db.session.commit()
            return jsonify({'msg': '新建成功', 'status': 1, 'case_id': new_cases.id, 'num': new_cases.num})


@api.route('/uicase/delete', methods=['POST'])
@login_required
def del_uicase():
    """ 删除case """
    data = request.json
    case_id = data.get('id')
    _data = UICase.query.filter_by(id=case_id).first()

    project_id = Module.query.filter_by(id=_data.module_id).first().project_id
    if current_user.id != Project.query.filter_by(id=project_id).first().user_id:
        return jsonify({'msg': '不能删除别人项目下的接口', 'status': 0})

    # # 同步删除接口信息下对应用例下的步骤信息
    # for d in UICase.query.filter_by(id=case_id).all():
    #     db.session.delete(d)

    db.session.delete(_data)

    return jsonify({'msg': '删除成功', 'status': 1})


@api.route('/uicase/list', methods=['POST'])
def list_uicase():
    """ 查接口信息 """
    data = request.json
    module_id = data.get('moduleId')
    project_name = data.get('projectName')
    case_name = data.get('caseName')
    platform = data.get('platform')
    page = data.get('page') if data.get('page') else 1
    per_page = data.get('sizePage') if data.get('sizePage') else 20
    if not project_name:
        return jsonify({'msg': '请选择项目', 'status': 0})
    if not module_id:
        return jsonify({'msg': '请先创建{}项目下的模块'.format(project_name), 'status': 0})
    if not platform:
        return jsonify({'msg': '请先选择操作系统'.format(project_name), 'status': 0})

    if case_name:
        case_data = UICase.query.filter_by(module_id=module_id, platform=platform).filter(
            UICase.name.like('%{}%'.format(case_name)))
        # total = len(case_data)
        if not case_data:
            return jsonify({'msg': '没有该接口信息', 'status': 0})
    else:
        case_data = UICase.query.filter_by(module_id=module_id, platform=platform)
    pagination = case_data.order_by(UICase.num.asc()).paginate(page, per_page=per_page, error_out=False)
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
    print(len(_data))
    plats = [{'id': c.id,
              'action': c.action,
              'action_name': c.action_name} for c in _data]
    return jsonify({'data': plats, 'status': 1})




@api.route('/uicase/editAndCopy', methods=['POST'])
@login_required
def edit_ui_case():
    """ 返回待编辑或复制的接口信息 """
    data = request.json
    case_id = data.get('id')
    _edit = UICase.query.filter_by(id=case_id).first()
    _data = {'name': _edit.name,
             'num': _edit.num,
             'desc': _edit.desc,
             'xpath': _edit.xpath,
             'text': _edit.text,
             'platform': Platform.filter_by(id=_edit.platform).first(),
             'resourceid': _edit.resourceid,
             'action': UIAction.filter_by(id=_edit.action).first(),
             'extraParam': _edit.extraParam}
    return jsonify({'data': _data, 'status': 1})

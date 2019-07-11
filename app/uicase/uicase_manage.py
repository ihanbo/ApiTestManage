from flask import jsonify, request
from app.api_1_0 import api, login_required
from app.models import *
from flask_login import current_user
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
        return jsonify({'msg': '名称不能为空', 'status': 0})
    if not platform:
        return jsonify({'msg': '操作系统不能为空', 'status': 0})
    if not steps:
        return jsonify({'msg': '步骤不能为空', 'status': 0})

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
            return jsonify({'msg': '新建成功', 'status': 1, 'caseId': new_cases.id, 'num': new_cases.num})


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

    project_id = Module.query.filter_by(id=_data.module_id).first().project_id
    if current_user.id != Project.query.filter_by(id=project_id).first().user_id:
        return jsonify({'msg': '不能删除别人项目下的case', 'status': 0})

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
    _edit = UICase.query.filter_by(id=case_id).first()
    _steps = UicaseStepInfo.query.filter_by(ui_case_id=case_id).all()
    _steps_data = []
    for s in _steps:
        c = UICaseStep.query.filter_by(module_id=_edit.module_id, platform=_edit.platform, id=s.ui_case_step_id).first()
        _steps_data.append({'id': c.id,
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
             'steps': _steps_data}
    return jsonify({'data': _data, 'status': 1})


@api.route('/uicases/importCases', methods=['POST'])
def import_uicases():
    """ 导入case，目前仅支持excel"""
    data = request.json
    project_name = data.get('projectName')
    module_id = data.get('moduleId')
    if not module_id and not project_name:
        return jsonify({'msg': '项目和模块不能为空', 'status': 0})
    project_data = Project.query.filter_by(name=project_name).first()

    import_api_address = data.get('importApiAddress')
    if not import_api_address:
        return jsonify({'msg': '请上传文件', 'status': 0})
    return jsonify({'msg': '导入成功', 'status': 1})

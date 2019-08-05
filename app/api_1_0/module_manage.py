from flask import jsonify, request
from flask_login import current_user
from ..util.http_run import RunCase, os

from app.models import *
from . import api, login_required
from ..util.utils import *


@api.route('/module/find', methods=['POST'])
@login_required
def find_model():
    """ 查找接口模块 """
    data = request.json
    page = data.get('page') if data.get('page') else 1
    per_page = data.get('sizePage') if data.get('sizePage') else 10
    project_name = data.get('projectName')
    if not project_name:
        return jsonify({'msg': '请先创建属于自己的项目', 'status': 0})

    all_module = Project.query.filter_by(name=project_name).first().modules
    pagination = all_module.paginate(page, per_page=per_page, error_out=False)
    my_module = pagination.items
    total = pagination.total
    my_module = [{'name': c.name, 'moduleId': c.id, 'num': c.num, 'choice': c.environment_choice, 'is_execute': c.is_execute} for c in my_module]

    # 查询出所有的接口模块是为了接口录入的时候可以选所有的模块p
    _all_module = [{'name': s.name, 'moduleId': s.id, 'num': s.num, 'choice': s.environment_choice, 'is_execute': s.is_execute} for s in all_module.all()]
    return jsonify({'data': my_module, 'total': total, 'status': 1, 'all_module': _all_module})


@api.route('/module/run', methods=['POST'])
@login_required
def run_module():
    data = request.json
    module_id = data.get('id')
    project_name = data.get('projectName')
    reportStatus = True
    api_ids = []
    if module_id:
        apiids = db.session.query(ApiMsg.id).filter_by(module_id=module_id).all()
        if len(apiids) == 0:
            return jsonify({'msg': '该用例下没有可执行的接口，请添加后重新运行', 'status': 1})
        for api in apiids:
            api_ids.append(api[0])
    project_id = db.session.query(Project.id).filter_by(name=project_name).first()
    d = RunCase(project_id[0])
    d.get_api_test(api_ids, None)
    jump_res = d.run_case()
    if reportStatus:
        # d.build_report(jump_res, case_ids)
        report_id = d.build_report(jump_res, api_ids)
        d.gen_result_summary(jump_res, project_id, report_id)
    res = json.loads(jump_res)

    return jsonify({{'msg': '运行完成，请查看运行结果', 'data': res, 'status': 0}})


@api.route('/module/addModuleEnvironment', methods=['POST'])
@login_required
def add_model_environment():
    """接口模块增加保存环境信息"""
    data = request.json
    choice = data.get('choice')
    moduleId = data.get('moduleId')
    if moduleId:
        old_data = Module.query.filter_by(id=moduleId).first()
        old_data.environment_choice = choice
        db.session.commit()
        return jsonify({'msg': '修改成功', 'status': 1})
    else:
        return jsonify({'msg': '修改失败', 'status': 0})


@api.route('/module/add', methods=['POST'])
@login_required
def add_model():
    """ 接口模块增加、编辑 """
    data = request.json
    project_name = data.get('projectName')
    if not project_name:
        return jsonify({'msg': '项目名称为空，请检查后重新创建模块', 'status': 0})
    name = data.get('name')
    if not name:
        return jsonify({'msg': '接口分类名称不能为空', 'status': 0})

    ids = data.get('id')
    project_id = Project.query.filter_by(name=project_name).first().id
    num = auto_num(data.get('num'), Module, project_id=project_id)
    if ids:
        old_data = Module.query.filter_by(id=ids).first()
        old_num = old_data.num
        list_data = Project.query.filter_by(name=project_name).first().modules.all()
        if Module.query.filter_by(name=name, project_id=project_id).first() and name != old_data.name:
            return jsonify({'msg': '接口分类名称重复', 'status': 0})

        num_sort(num, old_num, list_data, old_data)
        old_data.name = name
        old_data.project_id = project_id
        db.session.commit()
        return jsonify({'msg': '修改成功', 'status': 1})
    else:
        if Module.query.filter_by(name=name, project_id=project_id).first():
            return jsonify({'msg': '接口分类名称重复', 'status': 0})
        else:
            new_model = Module(name=name, project_id=project_id, num=num)
            db.session.add(new_model)
            db.session.commit()
            return jsonify({'msg': '新建成功', 'status': 1})


@api.route('/module/edit', methods=['POST'])
@login_required
def edit_model():
    """ 返回待编辑模块信息 """
    data = request.json
    model_id = data.get('id')
    _edit = Module.query.filter_by(id=model_id).first()
    _data = {'gatherName': _edit.name, 'num': _edit.num}

    return jsonify({'data': _data, 'status': 1})


@api.route('/module/del', methods=['POST'])
@login_required
def del_model():
    """ 删除模块 """
    data = request.json
    ids = data.get('id')
    _edit = Module.query.filter_by(id=ids).first()
    if current_user.id != Project.query.filter_by(id=_edit.project_id).first().user_id:
        return jsonify({'msg': '不能删除别人项目下的接口分类', 'status': 0})
    # 删除模块，即删除模块的相关全部信息
    # if _edit.api_msg.all():
    #     return jsonify({'msg': '请先删除模块下的接口用例', 'status': 0})
    if _edit.ui_cases.all():
        return jsonify({'msg': '请先删除模块下的UI用例', 'status': 0})
    db.session.delete(_edit)
    return jsonify({'msg': '删除成功', 'status': 1})


@api.route('/module/stick', methods=['POST'])
@login_required
def stick_module():
    """ 置顶模块 """
    data = request.json
    module_id = data.get('id')
    project_name = data.get('projectName')
    old_data = Module.query.filter_by(id=module_id).first()
    old_num = old_data.num
    list_data = Project.query.filter_by(name=project_name).first().modules.all()
    num_sort(1, old_num, list_data, old_data)
    db.session.commit()
    return jsonify({'msg': '置顶完成', 'status': 1})

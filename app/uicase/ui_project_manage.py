import json

from flask import jsonify, request

from app.api_1_0 import api
from app.models import *
from ..util.custom_decorator import login_required
from flask_login import current_user


@api.route('/proGather/ui_list')
@login_required
def get_pro_gather_ui():
    """ 获取基本信息 """
    # if current_user.id == 4:
    _pros = UI_Project.query.order_by(
        'CASE WHEN user_id={} THEN 0 END DESC'.format(current_user.id)).all()
    my_pros = _pros[0]
    pro = {}
    pro_and_id = []
    for p in _pros:
        # pro_and_id[p.name] = p.id
        pro_and_id.append({'name': p.name, 'id': p.id, 'android_package': p.android_package,
                           'android_launch': p.android_launch, 'ios_bundle_id': p.ios_bundle_id})
        # 获取每个项目下的接口模块
        pro[p.name] = [{'name': m.name, 'moduleId': m.id} for m in p.modules]

    if my_pros:
        my_pros = {'pro_name': my_pros.name, 'model_list': pro[my_pros.name]}

    return jsonify(
        {'data': pro, 'status': 1, 'user_pro': my_pros, 'pro_and_id': pro_and_id})


@api.route('/project/find_ui', methods=['POST'])
@login_required
def find_project_ui():
    """ 查找项目 """
    data = request.json
    project_name = data.get('projectName')
    # a = db.session.execute(r'''
    # SELECT * FROM "project" WHERE name='测试平台';
    # ''')
    # print(a.first())
    page = data.get('page') if data.get('page') else 1
    per_page = data.get('sizePage') if data.get('sizePage') else 10
    user_data = [{'user_id': u.id, 'user_name': u.name} for u in User.query.all()]
    if project_name:
        _data = UI_Project.query.filter(UI_Project.name.like('%{}%'.format(project_name))).all()
        total = len(_data)
        if not _data:
            return jsonify({'msg': '没有该项目', 'status': 0})
    else:
        pagination = UI_Project.query.order_by(UI_Project.id.asc()).paginate(page,
                                                                             per_page=per_page,
                                                                             error_out=False)
        _data = pagination.items
        total = pagination.total
    project = [
        {'id': p.id, 'name': p.name, 'principal': '管理员', 'android_package': p.android_package,
         'android_launch': p.android_launch, 'ios_bundle_id': p.ios_bundle_id} for p in
        _data]
    return jsonify({'data': project, 'total': total, 'status': 1, 'userData': user_data})


@api.route('/project/add_ui', methods=['POST'])
@login_required
def add_project_ui():
    """ 项目增加、编辑 """
    data = request.json
    project_name = data.get('projectName')
    if not project_name:
        return jsonify({'msg': '项目名称不能为空', 'status': 0})
    user_id = data.get('userId')
    if not user_id:
        return jsonify({'msg': '请选择负责人', 'status': 0})
    principal = data.get('principal', '管理员')
    ids = data.get('id')
    header = data.get('header')
    variable = data.get('variable')
    func_file = data.get('funcFile')
    android_package = data.get('android_package')
    ios_bundle_id = data.get('ios_bundle_id')
    android_launch = data.get('android_launch')

    if ids:  # 表示修改操作
        old_project_data = UI_Project.query.filter_by(id=ids).first()
        if UI_Project.query.filter_by(
                name=project_name).first() and project_name != old_project_data.name:
            return jsonify({'msg': '项目名字重复', 'status': 0})
        else:
            old_project_data.name = project_name
            old_project_data.user_id = user_id
            old_project_data.headers = header
            old_project_data.variables = variable
            old_project_data.func_file = func_file
            old_project_data.android_package = android_package
            old_project_data.android_launch = android_launch
            old_project_data.ios_bundle_id = ios_bundle_id
            db.session.commit()
            return jsonify({'msg': '修改成功', 'status': 1})
    else:
        if UI_Project.query.filter_by(name=project_name).first():
            return jsonify({'msg': '项目名字重复', 'status': 0})
        else:
            new_project = UI_Project(name=project_name,
                                     user_id=user_id,
                                     func_file=func_file,
                                     principal=principal,
                                     variables=variable,
                                     android_package=android_package,
                                     android_launch=android_launch,
                                     ios_bundle_id=ios_bundle_id)
            db.session.add(new_project)
            db.session.commit()
            return jsonify({'msg': '新建成功', 'status': 1})


@api.route('/project/edit_ui', methods=['POST'])
@login_required
def edit_project_ui():
    """ 返回待编辑项目信息 """
    data = request.json
    pro_id = data.get('id')
    _edit = UI_Project.query.filter_by(id=pro_id).first()
    if _edit.variables:
        _data = {'pro_name': _edit.name,
                 'user_id': _edit.user_id,
                 'principal': _edit.principal,
                 'func_file': _edit.func_file,
                 'android_package': _edit.android_package,
                 'android_launch': _edit.android_launch,
                 'ios_bundle_id': _edit.ios_bundle_id,
                 'variables': json.loads(_edit.variables)}
    else:
        _data = {'pro_name': _edit.name,
                 'user_id': _edit.user_id,
                 'principal': _edit.principal,
                 'func_file': _edit.func_file,
                 'android_package': _edit.android_package,
                 'android_launch': _edit.android_launch,
                 'ios_bundle_id': _edit.ios_bundle_id,
                 'variables': []}
    return jsonify({'data': _data, 'status': 1})


@api.route('/project/del_ui', methods=['POST'])
@login_required
def del_project_ui():
    """ 删除项目 """
    data = request.json
    ids = data.get('id')
    pro_data = UI_Project.query.filter_by(id=ids).first()
    db.session.delete(pro_data)
    return jsonify({'msg': '删除成功', 'status': 1})

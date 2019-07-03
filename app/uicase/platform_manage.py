from flask import request, jsonify

from app import db
from app.api_1_0 import api
from app.models import Platform


@api.route('/platform/add', methods=['POST'])
def add_plat():
    '''添加平台
    '''
    data = request.json
    platformName = data.get('platformName')
    if not platformName:
        return jsonify({'msg': '平台名称不能为空', 'status': 0})
    if Platform.query.filter_by(p_name=platformName).first():
        return jsonify({'msg': '平台名字重复', 'status': 0})
    else:
        new_platform = Platform(p_name=platformName)
        db.session.add(new_platform)
        db.session.commit()
        return jsonify({'msg': '添加成功', 'status': 1})


@api.route('/platform/delete', methods=['POST'])
def del_plat():
    '''删除平台
    '''
    data = request.json
    ids = data.get('id')
    plat_data = Platform.query.filter_by(id=ids).first()
    db.session.delete(plat_data)
    return jsonify({'msg': '删除成功', 'status': 1})


@api.route('/platform/list', methods=['GET'])
def find_all_plat():
    '''查询平台
    '''
    _data = Platform.query.order_by(Platform.id.asc()).all()
    print(len(_data))
    plats = [{'id': c.id,
              'name': c.p_name} for c in _data]
    return jsonify({'data': plats, 'status': 1})

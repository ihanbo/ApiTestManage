import json
import copy
from flask import jsonify, request
from . import api, login_required
from app.models import *
from app import scheduler

# @api.route('/resultSummary/list', methods=['POST'])
# def get_result_summary():
#     _data = ResultSummary.query.order_by(ResultSummary.id.desc()).all()
#     return jsonify({'data': _data, 'status': 1})

@api.route('/resultSummary/find', methods=['POST'])
def find_result_summary():
    data = request.json
    project_name = data.get('projectName')

    proid = Project.query.filter_by(name=project_name).first().id
    #_data = ResultSummary.query.filter_by()

    page = data.get('page') if data.get('page') else 1
    per_page = data.get('sizePage') if data.get('sizePage') else 10

    if not project_name:
        return jsonify({'msg': '请选择项目', 'status': 0})

    resultSummary = ResultSummary.query.filter_by(project_id=proid).order_by(ResultSummary.id.desc())
    scheduler.app.logger.info('返回数据：{}'.format(resultSummary))
    pagination = resultSummary.order_by(ResultSummary.id.desc().paginate(page, per_page=per_page, error_out=False))
    resultSummary = pagination.item
    total = pagination.total
    _data = [{'id': c.id, 'caseTotal': c.case_total, 'caseSuccess': c.case_success, 'caseFail': c.case_fail, 'stepTotal': c.step_total,
                      'stepSuccesses': c.step_successes, 'stepFailures':c.step_failures, 'step_errors':c.step_errors, 'startDatetime':c.start_datetime,
                      'projectId':c.project_id, 'reportId':c.report_id}
             for c in resultSummary]
    return jsonify({'data': _data, 'total': total, 'status': 1})
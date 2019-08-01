import json
import copy
from flask import jsonify, request
from . import api, login_required
from app.models import *

@api.route('/resultSummary/find', methods=['POST'])
@login_required
def find_result_summary():
    data = request.json
    project_name = data.get('projectName')
    project_id = Project.query.filter_by(name=project_name).first().id

    page = data.get('page') if data.get('page') else 1
    per_page = data.get('sizePage') if data.get('sizePage') else 10

    if not project_name:
        return jsonify({'msg': '请选择项目', 'status': 0})

    summary_data = ResultSummary.query.filter_by(project_id=project_id)
    pagination = summary_data.order_by(ResultSummary.id.desc()).paginate(page, per_page=per_page, error_out=False)
    summary = pagination.items
    total = pagination.total
    _data = [{'id': c.id, 'caseTotal': c.case_total, 'caseSuccess': c.case_success, 'caseFail': c.case_fail, 'caseSuccessRate':"{:.2%}".format(c.case_success / c.case_total), \
              'stepTotal': c.step_total, 'stepSuccesses': c.step_successes, 'stepFailures':c.step_failures, 'step_errors':c.step_errors, 'stepSuccessRate':"{:.2%}".format(c.step_successes / c.step_total), \
              'startDatetime':str(c.start_datetime),'duration':c.duration, 'projectId':c.project_id, 'projetName':project_name, 'reportId':c.report_id}
             for c in summary]
    return jsonify({'data': _data, 'total': total, 'status': 1})
from flask import jsonify, request
from . import api,login_required
from app.models import *

@api.route('/resultDetail/find', methods=['POST'])
def find_result_detail():
    data = request.json
    project_name = data.get('projectName')
    project_id = Project.query.filter_by(name=project_name).first().id

    page = data.get('page') if data.get('page') else 1
    per_page = data.get('sizePage') if data.get('sizePage') else 10

    if not project_name:
        return jsonify({'msg': '请选择项目', 'status': 0})

    detail_data = ResultDetail.query.filter_by(project_id=project_id)
    pagination = detail_data.order_by(ResultDetail.id.desc()).paginate(page, per_page=per_page, error_out=False)
    detail = pagination.items
    total = pagination.total
    _data = [{'caseId': c.case_id, 'caseName': c.case_name, 'caseExecStatus': c.case_exec_status, 'caseDuration': c.case_duration, 'caseDataId':c.case_data_id, \
              'caseDataName': c.case_data_name, 'apiMsgId': c.api_msg_id, 'apiMsgName':c.api_msg_name, 'apiExecStatus':c.api_exec_status, 'responseTime':c.response_time, \
              'projectId':c.project_id,'projectName':project_name, 'reportId':c.report_id, 'resultSummaryId':c.result_summary_id}
             for c in detail]
    return jsonify({'data': _data, 'total': total, 'status': 1})
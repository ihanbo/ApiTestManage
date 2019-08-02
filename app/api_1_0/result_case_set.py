from flask import jsonify, request
from . import api,login_required
from app.models import *
from sqlalchemy import func

@api.route('/resultCaseSet/find', methods=['POST'])
@login_required
def find_result_case_set():
    data = request.json
    project_name = data.get('projectName')
    project_id = Project.query.filter_by(name=project_name).first().id
    report_id = data.get('reportId')
    case_set_id = data.get('caseSetId')

    case_set_name = CaseSet.query.filter_by(project_id=project_id, id=case_set_id).first().name
    case_time_start_at = ResultDetail.query.filter_by(project_id=project_id, report_id=report_id, case_set_id=case_set_id).order_by(ResultDetail.case_time_start_at.asc()).first().case_time_start_at
    str_case_time_start_at = case_time_start_at.strftime("%Y-%m-%d %H:%M:%S")
    case_time_duration = db.session.query(func.sum(func.distinct(ResultDetail.case_duration))).filter_by(project_id=project_id, report_id=report_id, case_set_id=case_set_id).all()[0][0]
    case_total = db.session.query(func.distinct(ResultDetail.case_id)).filter_by(project_id=project_id, report_id=report_id, case_set_id=case_set_id).count()
    case_data_total = ResultDetail.query.filter_by(project_id=project_id, report_id=report_id, case_set_id=case_set_id).count()
    case_success = db.session.query(ResultDetail.case_id).filter_by(project_id=project_id, report_id=report_id, case_set_id=case_set_id, case_exec_status = 1).distinct().all()
    case_success= len(case_success)
    case_faile = db.session.query(ResultDetail.case_id).filter_by(project_id=project_id,report_id=report_id,case_set_id=case_set_id,case_exec_status=0).distinct().all()
    case_faile = len(case_faile)

    detail_data = ResultDetail.query.with_entities(ResultDetail.case_id,ResultDetail.case_name, ResultDetail.case_exec_status).filter_by(project_id=project_id,report_id=report_id,case_set_id=case_set_id).distinct().all()

    _data = {'caseTimeStartAt':str_case_time_start_at,
             'caseTimeDuration':case_time_duration,
             'caseTotal':case_total,
             'caseSuccess':case_success,
             'caseFaile':case_faile,
             'caseDataTotal': case_data_total,
             'caseSetId': case_set_id,
             'caseSetName': case_set_name,
             'caselist':[{'caseId':c.case_id, 'caseName': c.case_name, 'caseExecStatus': c.case_exec_status, } for c in detail_data]}

    return jsonify({'data': _data, 'total': len(detail_data), 'status': 1})

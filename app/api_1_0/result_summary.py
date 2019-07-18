import json
import copy
from flask import jsonify, request
from . import api, login_required
from app.models import *
from ..util.http_run import RunCase
from ..util.global_variable import *
from ..util.report.report import render_html_report
from app import scheduler

@api.route('/resultsummary/list', methods=['POST'])
@login_required
def get_result_summary():
    _data = ResultSummary.query.order_by(ResultSummary.id.desc()).all()
    return jsonify({'data': _data, 'status': 1})

@api.route('/resultsummary/find', methods=['POST'])
@login_required
def find_result_summary():
    data = request.json
    project_name = data.get('projectName')
    pro_id = Project.query.filter_by(name=project_name).first().id
    _data = ResultSummary.query.order_by(ResultSummary.id.desc()).all()
    return jsonify({'data': _data, 'status': 1})
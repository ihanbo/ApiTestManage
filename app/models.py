# encoding: utf-8
from collections import OrderedDict
from datetime import datetime

from flask import current_app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import check_password_hash, generate_password_hash

from . import db, login_manager

roles_permissions = db.Table('roles_permissions',
                             db.Column('role_id', db.Integer, db.ForeignKey('role.id')),
                             db.Column('permission_id', db.Integer, db.ForeignKey('permission.id')))


class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True, comment='主键，自增')
    name = db.Column(db.String(30), unique=True, comment='角色名称')
    users = db.relationship('User', back_populates='role')
    permission = db.relationship('Permission', secondary=roles_permissions, back_populates='role')

    @staticmethod
    def init_role():
        roles_permissions_map = OrderedDict()
        roles_permissions_map[u'测试人员'] = ['COMMON']
        roles_permissions_map[u'管理员'] = ['COMMON', 'ADMINISTER']
        for role_name in roles_permissions_map:
            role = Role.query.filter_by(name=role_name).first()
            if role is None:
                role = Role(name=role_name)
                db.session.add(role)
                role.permission = []
            for permission_name in roles_permissions_map[role_name]:
                permission = Permission.query.filter_by(name=permission_name).first()
                if permission is None:
                    permission = Permission(name=permission_name)
                    db.session.add(permission)
                role.permission.append(permission)
                db.session.commit()
        print('Role and permission created successfully')


class Permission(db.Model):
    __tablename__ = 'permission'
    id = db.Column(db.Integer, primary_key=True, comment='主键，自增')
    name = db.Column(db.String(30), unique=True, comment='权限名称')
    role = db.relationship('Role', secondary=roles_permissions, back_populates='permission')


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, comment='主键，自增')
    account = db.Column(db.String(64), unique=True, index=True, comment='账号')
    password_hash = db.Column(db.String(128), comment='密码')
    name = db.Column(db.String(64), comment='姓名')
    status = db.Column(db.Integer, comment='状态，1为启用，2为冻结')
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), comment='所属的角色id')
    role = db.relationship('Role', back_populates='users')
    created_time = db.Column(db.DateTime, index=True, default=datetime.now)
    update_time = db.Column(db.DateTime, index=True, default=datetime.now, onupdate=datetime.now)

    @staticmethod
    def init_user():
        user = User.query.filter_by(name='管理员').first()
        if user:
            print('The administrator account already exists')
            print('--' * 30)
            return
        else:
            user = User(name=u'管理员', account='admin', password='123456', status=1, role_id=2)
            db.session.add(user)
            db.session.commit()
            print('Administrator account created successfully')
            print('--' * 30)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_reset_token(self, expiration=360000):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def can(self, permission_name):
        permission = Permission.query.filter_by(name=permission_name).first()
        return permission is not None and self.role is not None and permission in self.role.permission


class Project(db.Model):
    __tablename__ = 'project'
    id = db.Column(db.Integer(), primary_key=True, comment='主键，自增')
    user_id = db.Column(db.Integer(), nullable=True, comment='所属的用户id')
    name = db.Column(db.String(64), nullable=True, unique=True, comment='项目名称')
    host = db.Column(db.String(1024), nullable=True, comment='测试环境')
    host_two = db.Column(db.String(1024), comment='开发环境')
    host_three = db.Column(db.String(1024), comment='线上环境')
    host_four = db.Column(db.String(1024), comment='备用环境')
    environment_choice = db.Column(db.String(16), comment='环境选择，first为测试，以此类推')
    principal = db.Column(db.String(16), nullable=True)
    variables = db.Column(db.String(2048), comment='项目的公共变量')
    headers = db.Column(db.String(1024), comment='项目的公共头部信息')
    func_file = db.Column(db.String(64), comment='函数文件')
    modules = db.relationship('Module', order_by='Module.num.asc()', lazy='dynamic')
    configs = db.relationship('Config', order_by='Config.num.asc()', lazy='dynamic')
    case_sets = db.relationship('CaseSet', order_by='CaseSet.num.asc()', lazy='dynamic')
    created_time = db.Column(db.DateTime, index=True, default=datetime.now, comment='创建时间')
    update_time = db.Column(db.DateTime, index=True, default=datetime.now, onupdate=datetime.now)
    is_execute = db.Column(db.Integer(), nullable=True, default=0, comment='是否执行过：1已执行、0未执行')
    report_id = db.Column(db.Integer(), nullable=True, comment='生成的报告id')


class Module(db.Model):
    __tablename__ = 'module'
    id = db.Column(db.Integer(), primary_key=True, comment='主键，自增')
    name = db.Column(db.String(64), nullable=True, comment='接口模块')
    num = db.Column(db.Integer(), nullable=True, comment='模块序号')
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), comment='所属的项目id')
    api_msg = db.relationship('ApiMsg', order_by='ApiMsg.num.asc()', lazy='dynamic')
    environment_choice = db.Column(db.String(16), default='first', comment='环境选择，first为测试，以此类推')
    is_execute = db.Column(db.Integer(), nullable=True, default=0, comment='是否执行过：1已执行、0未执行')
    created_time = db.Column(db.DateTime, index=True, default=datetime.now, comment='创建时间')
    update_time = db.Column(db.DateTime, index=True, default=datetime.now, onupdate=datetime.now)


class Config(db.Model):
    __tablename__ = 'config'
    id = db.Column(db.Integer(), primary_key=True, comment='主键，自增')
    num = db.Column(db.Integer(), nullable=True, comment='配置序号')
    name = db.Column(db.String(128), comment='配置名称')
    variables = db.Column(db.String(21000), comment='配置参数')
    func_address = db.Column(db.String(128), comment='配置函数')
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), comment='所属的项目id')
    created_time = db.Column(db.DateTime, index=True, default=datetime.now, comment='创建时间')
    update_time = db.Column(db.DateTime, index=True, default=datetime.now, onupdate=datetime.now)


class CaseSet(db.Model):
    __tablename__ = 'case_set'
    id = db.Column(db.Integer(), primary_key=True, comment='主键，自增')
    num = db.Column(db.Integer(), nullable=True, comment='用例集合序号')
    name = db.Column(db.String(256), nullable=True, comment='用例集名称')
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), comment='所属的项目id')
    cases = db.relationship('Case', order_by='Case.num.asc()', lazy='dynamic')
    environment_choice = db.Column(db.String(16), comment='环境选择，first为测试，以此类推')
    created_time = db.Column(db.DateTime, index=True, default=datetime.now, comment='创建时间')
    update_time = db.Column(db.DateTime, index=True, default=datetime.now, onupdate=datetime.now)
    is_execute = db.Column(db.Integer(), nullable=True, default=0, comment='是否执行过：1已执行、0未执行')
    report_id = db.Column(db.Integer(), nullable=True, comment='生成的报告id')


class Case(db.Model):
    __tablename__ = 'case'
    id = db.Column(db.Integer(), primary_key=True, comment='主键，自增')
    num = db.Column(db.Integer(), nullable=True, comment='用例序号')
    name = db.Column(db.String(128), nullable=True, comment='用例名称')
    desc = db.Column(db.String(256), comment='用例描述')
    func_address = db.Column(db.String(256), comment='用例需要引用的函数')
    variable = db.Column(db.Text(), comment='用例公共参数')
    times = db.Column(db.Integer(), nullable=True, comment='执行次数')
    wait_times = db.Column(db.Integer(), nullable=True, comment='等待时间')
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), comment='所属的项目id')
    case_set_id = db.Column(db.Integer, db.ForeignKey('case_set.id'), comment='所属的用例集id')
    created_time = db.Column(db.DateTime, index=True, default=datetime.now, comment='创建时间')
    update_time = db.Column(db.DateTime, index=True, default=datetime.now, onupdate=datetime.now)
    charge_name = db.Column(db.String(128), nullable=True, comment='测试负责人')


class ApiMsg(db.Model):
    __tablename__ = 'api_msg'
    id = db.Column(db.Integer(), primary_key=True, comment='主键，自增')
    num = db.Column(db.Integer(), nullable=True, comment='接口序号')
    name = db.Column(db.String(128), nullable=True, comment='接口名称')
    desc = db.Column(db.String(256), nullable=True, comment='接口描述')
    variable_type = db.Column(db.String(32), nullable=True, comment='参数类型选择')
    status_url = db.Column(db.String(32), nullable=True, comment='基础url,序号对应项目的环境')
    up_func = db.Column(db.String(128), comment='接口执行前的函数')
    down_func = db.Column(db.String(128), comment='接口执行后的函数')
    method = db.Column(db.String(32), nullable=True, comment='请求方式')
    variable = db.Column(db.Text(), comment='form-data形式的参数')
    json_variable = db.Column(db.Text(), comment='json形式的参数')
    param = db.Column(db.Text(), comment='url上面所带的参数')
    url = db.Column(db.String(256), nullable=True, comment='接口地址')
    extract = db.Column(db.String(2048), comment='提取信息')
    validate = db.Column(db.String(2048), comment='断言信息')
    header = db.Column(db.String(2048), comment='头部信息')
    # encrypt = db.Column(db.Boolean, nullable=False, default=False, comment='是否需要加密解密操作')
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'), comment='所属的接口模块id')
    project_id = db.Column(db.Integer, nullable=True, comment='所属的项目id')
    created_time = db.Column(db.DateTime, index=True, default=datetime.now)
    update_time = db.Column(db.DateTime, index=True, default=datetime.now, onupdate=datetime.now)
    charge_name = db.Column(db.String(128), nullable=True, comment='测试负责人')
    is_execute = db.Column(db.Integer(), nullable=True, default=0, comment='是否执行过：1已执行、0未执行')
    save_result = db.Column(db.String(), nullable=True, comment='保存结果信息')


class CaseData(db.Model):
    __tablename__ = 'case_data'
    id = db.Column(db.Integer(), primary_key=True, comment='主键，自增')
    num = db.Column(db.Integer(), nullable=True, comment='步骤序号，执行顺序按序号来')
    status = db.Column(db.String(16), comment='状态，true表示执行，false表示不执行')
    name = db.Column(db.String(128), comment='步骤名称')
    up_func = db.Column(db.String(256), comment='步骤执行前的函数')
    down_func = db.Column(db.String(256), comment='步骤执行后的函数')
    time = db.Column(db.Integer(), default=1, comment='执行次数')
    param = db.Column(db.Text(), default=u'[]')
    status_param = db.Column(db.String(64), default=u'[true, true]')
    variable = db.Column(db.Text())
    json_variable = db.Column(db.Text())
    status_variables = db.Column(db.String(64))
    extract = db.Column(db.String(2048))
    status_extract = db.Column(db.String(64))
    validate = db.Column(db.String(2048))
    status_validate = db.Column(db.String(64))
    case_id = db.Column(db.Integer, db.ForeignKey('case.id'))
    api_msg_id = db.Column(db.Integer, db.ForeignKey('api_msg.id'))
    created_time = db.Column(db.DateTime, index=True, default=datetime.now)
    update_time = db.Column(db.DateTime, index=True, default=datetime.now, onupdate=datetime.now)


class Report(db.Model):
    __tablename__ = 'report'
    id = db.Column(db.Integer(), primary_key=True, comment='主键，自增')
    case_names = db.Column(db.String(128), nullable=True, comment='用例的名称集合')
    read_status = db.Column(db.String(16), nullable=True, comment='阅读状态')
    project_id = db.Column(db.String(16), nullable=True)
    create_time = db.Column(db.DateTime(), index=True, default=datetime.now)


class ResultSummary(db.Model):
    __tablename__ = 'result_summary'
    id = db.Column(db.Integer(), primary_key=True, comment='主键，自增')
    case_total = db.Column(db.Integer(), nullable=True, comment='用例总数')
    case_success = db.Column(db.Integer(), nullable=True, comment='成功用例数')
    case_fail = db.Column(db.Integer(), nullable=True, comment='失败用例数')
    start_datetime = db.Column(db.DateTime, index=True, default=datetime.now, comment='用例开始时间')
    duration = db.Column(db.Float(), nullable=True, comment="用例持续时间")
    step_total = db.Column(db.Integer(), nullable=True, comment='步骤总数')
    step_successes = db.Column(db.Integer(), nullable=True, comment='成功步骤数')
    step_failures = db.Column(db.Integer(), nullable=True, comment='失败步骤数')
    step_errors = db.Column(db.Integer(), nullable=True, comment='错误步骤数')
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), comment='所属的项目id')
    report_id = db.Column(db.Integer, db.ForeignKey('report.id'), comment='报告id')
    created_time = db.Column(db.DateTime, index=True, default=datetime.now)
    update_time = db.Column(db.DateTime, index=True, default=datetime.now, onupdate=datetime.now)


class ResultDetail(db.Model):
    __tablename__ = 'result_detail'
    id = db.Column(db.Integer(), primary_key=True, comment='主键，自增')
    case_id = db.Column(db.ForeignKey('case.id'), comment='用例id')
    case_name = db.Column(db.String(128), nullable=True, comment='用例名称')
    case_exec_status = db.Column(db.Boolean, nullable=True, default=True, comment='用例执行状态')
    case_time_start_at = db.Column(db.DateTime, index=True, default=datetime.now, comment='用例开始时间')
    case_duration = db.Column(db.Float(), nullable=True, comment="用例持续时间")
    case_data_id = db.Column(db.Integer(), db.ForeignKey('case_data.id'), comment='用例步骤id')
    case_data_name = db.Column(db.String(128), nullable=True, comment='用例步骤名称')
    api_msg_id = db.Column(db.Integer, db.ForeignKey('api_msg.id'))
    api_msg_name = db.Column(db.String(128), nullable=True, comment='接口名称')
    api_exec_status = db.Column(db.String(128), nullable=True, default=True, comment='接口执行状态')
    response_time = db.Column(db.Float(), nullable=True, comment="接口响应时间")
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), comment='所属的项目id')
    project_name = db.Column(db.String(64), nullable=True, comment='项目名称')
    case_set_id = db.Column(db.Integer, db.ForeignKey('case_set.id'), comment='所属的用例集id')
    case_set_name = db.Column(db.String(256), nullable=True, comment='用例集名称')
    report_id = db.Column(db.Integer, db.ForeignKey('report.id'), comment='报告id')
    result_summary_id = db.Column(db.ForeignKey('result_summary.id'), comment='报告id')
    created_time = db.Column(db.DateTime, index=True, default=datetime.now)
    update_time = db.Column(db.DateTime, index=True, default=datetime.now, onupdate=datetime.now)


class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True, comment='主键，自增')
    num = db.Column(db.Integer(), comment='任务序号')
    task_name = db.Column(db.String(64), comment='任务名称')
    task_config_time = db.Column(db.String(256), nullable=True, comment='cron表达式')
    set_id = db.Column(db.String(2048))
    case_id = db.Column(db.String(2048))
    task_type = db.Column(db.String(16))
    task_to_email_address = db.Column(db.String(256), comment='收件人邮箱')
    task_send_email_address = db.Column(db.String(256), comment='发件人邮箱')
    email_password = db.Column(db.String(256), comment='发件人邮箱密码')
    status = db.Column(db.String(16), default=u'创建', comment='任务的运行状态，默认是创建')
    project_id = db.Column(db.String(16), nullable=True)
    created_time = db.Column(db.DateTime(), default=datetime.now, comment='任务的创建时间')
    update_time = db.Column(db.DateTime, index=True, default=datetime.now, onupdate=datetime.now)


class Platform(db.Model):
    __tablename__ = 'platform'
    id = db.Column(db.Integer, primary_key=True, comment='主键，自增')
    p_name = db.Column(db.String(64), comment='应用平台类型', unique=True)

    def to_dict(self):
        '''将对象转换为字典数据'''
        p_dict = {
            "id": self.id,
            "p_name": self.p_name
        }
        return p_dict


class UIAction(db.Model):
    __tablename__ = 'ui_action'
    id = db.Column(db.Integer, primary_key=True, comment='主键，自增')
    action = db.Column(db.String(64), comment='行为', unique=True)
    action_name = db.Column(db.String(64), comment='行为名称')

    def action_to_dict(self):
        '''将对象转换为字典数据'''
        a_dict = {
            "id": self.id,
            "action": self.action,
            "action_name": self.action_name
        }
        return a_dict

    @staticmethod
    def init_action():
        action1 = UIAction.query.filter_by(action=u'click').first()
        if action1 is None:
            a1 = UIAction(action=u'click', action_name=u'点击')
            db.session.add(a1)
            db.session.commit()
        action2 = UIAction.query.filter_by(action=u'input').first()
        if action2 is None:
            a2 = UIAction(action=u'input', action_name=u'输入')
            db.session.add(a2)
            db.session.commit()

        action3 = UIAction.query.filter_by(action=u'clear').first()
        if action3 is None:
            a3 = UIAction(action=u'clear', action_name=u'清除(输入框)')
            db.session.add(a3)
            db.session.commit()

        action4 = UIAction.query.filter_by(action=u'back').first()
        if action4 is None:
            a4 = UIAction(action=u'back', action_name=u'后退')
            db.session.add(a4)
            db.session.commit()
        action5 = UIAction.query.filter_by(action=u'swipe_down').first()
        if action5 is None:
            a5 = UIAction(action=u'swipe_down', action_name=u'下滑')
            db.session.add(a5)
            db.session.commit()

        action6 = UIAction.query.filter_by(action=u'swipe_up').first()
        if action6 is None:
            a6 = UIAction(action=u'swipe_up', action_name=u'上滑')
            db.session.add(a6)
            db.session.commit()

        action7 = UIAction.query.filter_by(action=u'swipe_right').first()
        if action7 is None:
            a7 = UIAction(action=u'swipe_right', action_name=u'右滑')
            db.session.add(a7)
            db.session.commit()
        action8 = UIAction.query.filter_by(action=u'swipe_left').first()
        if action8 is None:
            a8 = UIAction(action=u'swipe_left', action_name=u'左滑')
            db.session.add(a8)
            db.session.commit()
        print('default action was created successfully')
        print('--' * 30)


class UicaseStepInfo(db.Model):
    __tablename__ = 'ui_case_step_info'
    id = db.Column(db.Integer(), primary_key=True, comment='主键，自增')
    ui_case_step_id = db.Column(db.Integer, db.ForeignKey('ui_case_step.id'), comment='步骤id')
    num = db.Column(db.Integer(), nullable=True, comment='case中step序号')
    ui_case_id = db.Column(db.Integer, db.ForeignKey('ui_case.id'), comment='caseid')
    ui_type = db.Column(db.Integer(), nullable=True, default=0, comment='0为正常操作步骤，1为录屏')
    contentText = db.Column(db.String(5120), comment='录屏内容' )

def info2dic(c):
    return {'id': c.id,
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


class UICaseStep(db.Model):
    __tablename__ = 'ui_case_step'
    id = db.Column(db.Integer(), primary_key=True, comment='主键，自增')
    num = db.Column(db.Integer(), nullable=True, comment='case序号')
    name = db.Column(db.String(256), nullable=True, comment='名称')
    desc = db.Column(db.String(256), nullable=True, comment='描述')
    xpath = db.Column(db.String(), comment='定位元素路径')
    resourceid = db.Column(db.String(), comment='定位元素id')
    text = db.Column(db.String(1024), comment='定位元素文本')
    set_up = db.Column(db.String(1024), comment='前置处理')
    tear_down = db.Column(db.String(1024), comment='后置处理')
    ui_selector = db.Column(db.String(1024), comment='复合定位元素')
    expected_value = db.Column(db.String(1024), comment='预期值')
    action = db.Column(db.Integer, db.ForeignKey('ui_action.id'), comment='case行为')
    ui_action = db.relationship('UIAction')
    extraParam = db.Column(db.String(1024), comment='描述')
    platform = db.Column(db.Integer, db.ForeignKey('platform.id'), comment='对应操作系统')
    module_id = db.Column(db.Integer, db.ForeignKey('ui_module.id'), comment='所属的接口模块id')
    casesort_id = db.Column(db.Integer, db.ForeignKey('ui_casesort.id'), comment='所属的接口模块id')
    project_id = db.Column(db.Integer, nullable=True, comment='所属的项目id')
    created_time = db.Column(db.DateTime, index=True, default=datetime.now)
    update_time = db.Column(db.DateTime, index=True, default=datetime.now, onupdate=datetime.now)


class UI_Project(db.Model):
    __tablename__ = 'ui_project'
    id = db.Column(db.Integer(), primary_key=True, comment='主键，自增')
    user_id = db.Column(db.Integer(), nullable=True, comment='所属的用户id')
    principal = db.Column(db.String(16), nullable=True, comment='所属的用户名称')
    name = db.Column(db.String(64), nullable=True, unique=True, comment='项目名称')
    variables = db.Column(db.String(2048), comment='项目的公共变量')
    func_file = db.Column(db.String(64), comment='函数文件')
    android_package = db.Column(db.String(128), comment='安卓包名')
    android_launch = db.Column(db.String(256), comment='安卓启动activity')
    ios_bundle_id = db.Column(db.String(128), comment='iOS项目bundleid')
    modules = db.relationship('UI_Module', order_by='UI_Module.num.asc()', lazy='dynamic')
    casesort = db.relationship('UI_CaseSort', order_by='UI_CaseSort.id.desc()', lazy='dynamic')
    case_sets = db.relationship('UI_CaseSet', order_by='UI_CaseSet.num.asc()', lazy='dynamic')
    created_time = db.Column(db.DateTime, index=True, default=datetime.now, comment='创建时间')
    update_time = db.Column(db.DateTime, index=True, default=datetime.now, onupdate=datetime.now)

# uicase分类信息
class UI_CaseSort(db.Model):
    __tablename__ = 'ui_casesort'
    id = db.Column(db.Integer(), primary_key=True, comment='主键，自增')
    name = db.Column(db.String(64), nullable=True, comment='接口模块')
    num = db.Column(db.Integer(), nullable=True, comment='模块序号')
    project_id = db.Column(db.Integer, db.ForeignKey('ui_project.id'), comment='所属的项目id')
    ui_cases = db.relationship('UICase', order_by='UICase.num.asc()', lazy='dynamic')
    ui_case_steps = db.relationship('UICaseStep', order_by='UICaseStep.num.asc()', lazy='dynamic')
    created_time = db.Column(db.DateTime, index=True, default=datetime.now, comment='创建时间')
    update_time = db.Column(db.DateTime, index=True, default=datetime.now, onupdate=datetime.now)

# 步骤分类
class UI_Module(db.Model):
    __tablename__ = 'ui_module'
    id = db.Column(db.Integer(), primary_key=True, comment='主键，自增')
    name = db.Column(db.String(64), nullable=True, comment='接口模块')
    num = db.Column(db.Integer(), nullable=True, comment='模块序号')
    project_id = db.Column(db.Integer, db.ForeignKey('ui_project.id'), comment='所属的项目id')
    ui_cases = db.relationship('UICase', order_by='UICase.num.asc()', lazy='dynamic')
    ui_case_steps = db.relationship('UICaseStep', order_by='UICaseStep.num.asc()', lazy='dynamic')
    created_time = db.Column(db.DateTime, index=True, default=datetime.now, comment='创建时间')
    update_time = db.Column(db.DateTime, index=True, default=datetime.now, onupdate=datetime.now)


class UICase(db.Model):
    __tablename__ = 'ui_case'
    id = db.Column(db.Integer(), primary_key=True, comment='主键，自增')
    project_id = db.Column(db.Integer, nullable=True, comment='所属的项目id')
    module_id = db.Column(db.Integer, db.ForeignKey('ui_module.id'), comment='所属的接口模块id')
    casesort_id = db.Column(db.Integer, db.ForeignKey('ui_casesort.id'), comment='所属的接口模块id')
    platform = db.Column(db.Integer, db.ForeignKey('platform.id'), comment='对应操作系统')
    # caseset_id = db.Column(db.Integer, db.ForeignKey('ui_case_set.id'), comment='对应用例集')
    name = db.Column(db.String(256), nullable=True, comment='名称')
    num = db.Column(db.Integer(), nullable=True, comment='case序号')
    desc = db.Column(db.String(256), nullable=True, comment='描述')


class UI_Case_CaseSet(db.Model):
    """caseset和case中间表多对多"""
    __tablename__ = 'ui_case_caseset'
    id = db.Column(db.Integer(), primary_key=True, comment='主键，自增')
    case_id = db.Column(db.Integer, db.ForeignKey('ui_case.id'), comment='步骤id')
    num = db.Column(db.Integer(), nullable=True, comment='caseset中的顺序')
    caseset_id = db.Column(db.Integer, db.ForeignKey('ui_case_set.id'), comment='caseid')


class UI_CaseSet(db.Model):
    __tablename__ = 'ui_case_set'
    id = db.Column(db.Integer(), primary_key=True, comment='主键，自增')
    platform = db.Column(db.Integer, db.ForeignKey('platform.id'), comment='对应操作系统')
    num = db.Column(db.Integer(), nullable=True, comment='用例集合序号')
    name = db.Column(db.String(256), nullable=True, comment='用例集名称：英文')
    desc = db.Column(db.String(256), nullable=True, comment='用例集描述：中文')
    project_id = db.Column(db.Integer, db.ForeignKey('ui_project.id'), comment='所属的项目id')
    created_time = db.Column(db.DateTime, index=True, default=datetime.now, comment='创建时间')
    update_time = db.Column(db.DateTime, index=True, default=datetime.now, onupdate=datetime.now)
    set_type = db.Column(db.Integer(), nullable=True, comment='用例集类别 0正常步骤用例集，1录屏用例集')
    service_id = db.Column(db.Integer, db.ForeignKey('ui_casesort.id'), comment='业务类型id')


class UICaseReport(db.Model):
    __tablename__ = 'ui_case_report'
    id = db.Column(db.Integer(), primary_key=True, comment='主键，自增')
    project_id = db.Column(db.Integer, nullable=True, comment='所属的项目id')
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'), comment='所属的接口模块id')
    platform = db.Column(db.Integer, db.ForeignKey('platform.id'), comment='对应操作系统')
    read_status = db.Column(db.String(16), nullable=True, comment='阅读状态')
    name = db.Column(db.String(256), nullable=True, comment='名称')
    desc = db.Column(db.String(256), nullable=True, comment='描述')
    report_dir = db.Column(db.String(256), nullable=True, comment='报告存储目录')
    result = db.Column(db.String(), nullable=True, comment='json结果数据')
    create_time = db.Column(db.DateTime(), index=True, default=datetime.now)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

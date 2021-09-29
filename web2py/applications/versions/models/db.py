# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------
# AppConfig configuration made easy. Look inside private/appconfig.ini
# Auth is for authenticaiton and access control
# -------------------------------------------------------------------------
import datetime

from gluon.contrib.appconfig import AppConfig
from gluon.tools import Auth

# -------------------------------------------------------------------------
# This scaffolding model makes your app work on Google App Engine too
# File is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

if request.global_settings.web2py_version < "2.15.5":
    raise HTTP(500, "Requires web2py 2.15.5 or newer")

# -------------------------------------------------------------------------
# if SSL/HTTPS is properly configured and you want all HTTP requests to
# be redirected to HTTPS, uncomment the line below:
# -------------------------------------------------------------------------
# request.requires_https()

# -------------------------------------------------------------------------
# once in production, remove reload=True to gain full speed
# -------------------------------------------------------------------------
configuration = AppConfig(reload=True)

if not request.env.web2py_runtime_gae:
    # ---------------------------------------------------------------------
    # if NOT running on Google App Engine use SQLite or other DB
    # ---------------------------------------------------------------------
    db = DAL(configuration.get('db.uri'),
             pool_size=configuration.get('db.pool_size'),
             migrate_enabled=configuration.get('db.migrate'),
             check_reserved=['all'])
else:
    # ---------------------------------------------------------------------
    # connect to Google BigTable (optional 'google:datastore://namespace')
    # ---------------------------------------------------------------------
    db = DAL('google:datastore+ndb')
    # ---------------------------------------------------------------------
    # store sessions and tickets there
    # ---------------------------------------------------------------------
    session.connect(request, response, db=db)
    # ---------------------------------------------------------------------
    # or store session in Memcache, Redis, etc.
    # from gluon.contrib.memdb import MEMDB
    # from google.appengine.api.memcache import Client
    # session.connect(request, response, db = MEMDB(Client()))
    # ---------------------------------------------------------------------

# -------------------------------------------------------------------------
# by default give a view/generic.extension to all actions from localhost
# none otherwise. a pattern can be 'controller/function.extension'
# -------------------------------------------------------------------------
response.generic_patterns = []
if request.is_local and not configuration.get('app.production'):
    response.generic_patterns.append('*')

# -------------------------------------------------------------------------
# choose a style for forms
# -------------------------------------------------------------------------
response.formstyle = 'bootstrap4_inline'
response.form_label_separator = ''

# -------------------------------------------------------------------------
# (optional) optimize handling of static files
# -------------------------------------------------------------------------
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

# -------------------------------------------------------------------------
# (optional) static assets folder versioning
# -------------------------------------------------------------------------
# response.static_version = '0.0.0'

# -------------------------------------------------------------------------
# Here is sample code if you need for
# - email capabilities
# - authentication (registration, login, logout, ... )
# - authorization (role based authorization)
# - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
# - old style crud actions
# (more options discussed in gluon/tools.py)
# -------------------------------------------------------------------------

# host names must be a list of allowed host names (glob syntax allowed)
auth = Auth(db, host_names=configuration.get('host.names'))

# -------------------------------------------------------------------------
# create all tables needed by auth, maybe add a list of extra fields
# -------------------------------------------------------------------------
auth.settings.extra_fields['auth_user'] = []
auth.define_tables(username=False, signature=False)

# -------------------------------------------------------------------------
# configure email
# -------------------------------------------------------------------------
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else configuration.get('smtp.server')
mail.settings.sender = configuration.get('smtp.sender')
mail.settings.login = configuration.get('smtp.login')
mail.settings.tls = configuration.get('smtp.tls') or False
mail.settings.ssl = configuration.get('smtp.ssl') or False

# -------------------------------------------------------------------------
# configure auth policy
# -------------------------------------------------------------------------
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

# -------------------------------------------------------------------------  
# read more at http://dev.w3.org/html5/markup/meta.name.html               
# -------------------------------------------------------------------------
response.meta.author = configuration.get('app.author')
response.meta.description = configuration.get('app.description')
response.meta.keywords = configuration.get('app.keywords')
response.meta.generator = configuration.get('app.generator')
response.show_toolbar = configuration.get('app.toolbar')

# -------------------------------------------------------------------------
# your http://google.com/analytics id                                      
# -------------------------------------------------------------------------
response.google_analytics_id = configuration.get('google.analytics_id')

# -------------------------------------------------------------------------
# maybe use the scheduler
# -------------------------------------------------------------------------
if configuration.get('scheduler.enabled'):
    from gluon.scheduler import Scheduler

    scheduler = Scheduler(db, heartbeat=configuration.get('scheduler.heartbeat'))

# -------------------------------------------------------------------------
# Define your tables below (or better in another model file) for example
#
# >>> db.define_table('mytable', Field('myfield', 'string'))
#
# Fields can be 'string','text','password','integer','double','boolean'
#       'date','time','datetime','blob','upload', 'reference TABLENAME'
# There is an implicit 'id integer autoincrement' field
# Consult manual for more options, validators, etc.
#
# More API examples for controllers:
#
# >>> db.mytable.insert(myfield='value')
# >>> rows = db(db.mytable.myfield == 'value').select(db.mytable.ALL)
# >>> for row in rows: print row.id, row.myfield
# -------------------------------------------------------------------------

# -------------------------------------------------------------------------
# after defining tables, uncomment below to enable auditing
# -------------------------------------------------------------------------
# auth.enable_record_versioning(db)
db.define_table('projects',
                Field('name', 'string', length=50, required=True, label='Проект', comment='Имя проекта'),
                Field('description', 'text', label='Описание', comment='Описание проекта'), format='%(name)s')
db.define_table('environments',
                Field('project', 'reference projects', label='Проект', comment='Имя проекта'),
                Field('name', 'string', length=50, required=True, label='Полигон', comment='Наименование полигона'),
                Field('address', 'text', label='Адрес', comment='Адрес полигона'),
                Field('responsible', 'text', label='Ответственный', comment='ФИО ответственного'),
                format=lambda r: db.projects[r.project].name + ':' + r.name)
db.define_table('applicationtypes',
                Field('apptype', 'string', length=100, required=True, notnull=True, unique=True, label='Тип приложения',
                      comment='Тип приложения'),
                Field('info', 'text'), format='%(type)s')
db.define_table('applicitionstatuses',
                Field('name', 'string', length=100, required=True, notnull=True, unique=True, label='Статус',
                      comment='Актуальный статус'),
                Field('info', 'text'), format='%(name)s')
db.define_table('products',
                Field('name', 'string', length=20, required=True, notnull=True, unique=True, label='Продукт',
                      comment='Продукт'),
                Field('info', 'text'),
                Field('responsible', 'text', label='Ответственный', comment='Ответственный за продукт'))
db.define_table('applications',
                Field('name', 'string', length=200, required=True, unique=True, notnull=True, label='Приложение',
                      comment='Имя приложения'),
                Field('apptype', 'reference applicationtypes', required=True, notnull=True, label='Тип',
                      comment='Тип приложения'),
                Field('product', 'reference products', default=None, label='Продукт',
                      comment='Продукт, к которому относится приложение. Опционален.'),
                Field('status', 'reference applicitionstatuses', required=True, notnull=True), format='%(name)s')
db.define_table('versions',
                Field('application', 'reference applications', required=True),
                Field('appversion', 'string', length=100, required=True, notnull=True, label='Версия',
                      comment='Версия приложения'),
                Field('info', 'text', label='Комментарий'), format='%(version)s')
db.define_table('releases',
                Field('tag', 'string', length=20, required=True, notnull=True, unique=True, label='Тэг',
                      comment='Номер релиза'),
                Field('released_at', 'date', required=True, notnull=True, label='Выпущен в',
                      comment='Дата выпуска релиза', default=datetime.datetime.now().date),
                Field('info', 'text'), format='%(tag)s')
db.define_table('apprelease',
                Field('tag', 'reference releases', length=20, required=True, notnull=True, label='Релиз',
                      comment='Тэг релиза'),
                Field('application', 'reference applications', required=True, notnull=True, label='Приложение',
                      comment='Имя приложения'),
                Field('appversion', 'reference versions', required=True, notnull=True, label='Версия',
                      comment='Версия приложения'), format='%(tag)s')
db.define_table('installed',
                Field('environment', 'reference environments', required=True, notnull=True, label='Полигон',
                      comment="Полигон развертывания"),
                Field('appversion', 'reference versions', required=True, notnull=True, label='Версия',
                      comment='Установленная версия'),
                Field('reported_at', 'date', required=True, notnull=True, default=datetime.datetime.now().date,
                      label='Дата', comment='Дата получения информации'),
                format='%(version)s')

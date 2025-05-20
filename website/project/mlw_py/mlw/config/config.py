import os

class Config():
    # BASE SETTINGS
    BASE_URL = '/mlw'
    MAINTAINER_NAME = ''
    CACHE_SERVICE_HOST = 'cache-services'
    CACHE_URL = f'http://{CACHE_SERVICE_HOST}/cache'
    CACHE_SLEEP_TIME = 10

    # MAINTENANCE_MODE = True
    MAINTENANCE_MODE = False
    MAINTENANCE_MODE_WHITELIST = {
        '/logout', 
        '/login',
        '/static',
        '/favicon.ico'
    }

    # SECRET_KEY = os.urandom(16)
    SECRET_KEY = b'\xaa6\xfe\xd7\r\xef\xe6K\xde\x18\x9f\xb4\x8c\xc6\xfa\x17'

    # DB
    DB_TYPE = 'mysql+pymysql://'
    DB_HOST = 'mariadb'
    DB_DATABASE = 'mlw'
    DB_USER = 'admin'
    DB_PASSWORD = 'root'

    # Redis
    REDIS_HOST = 'redis'
    REDIS_PORT = 6379
    REDIS_DB = 0
    CACHE_DEFAULT_TIMEOUT = 1800
    
    # LDAP
    LDAP_HOST = ''
    LDAP_PORT = ''
    LDAP_DOMAIN = ''
    LDAP_SYSTEM_USER = ''
    LDAP_SYSTEM_AUTH = ''
    
    # PATH
    TRANSLATION_DIR = os.path.join('rep', 'translation')
    APP_SOURCE_IN_DIR = os.path.join(TRANSLATION_DIR, 'source-in')
    APP_SOURCE_OUT_DIR = os.path.join(TRANSLATION_DIR, 'source-out')
    APP_EXCEL_IN_DIR = os.path.join(TRANSLATION_DIR, 'excel-in')
    APP_EXCEL_OUT_DIR = os.path.join(TRANSLATION_DIR, 'excel-out')
    APP_DOWNLOAD_DIR = os.path.join(TRANSLATION_DIR, 'download')
    APP_UPLOAD_DIR = os.path.join(TRANSLATION_DIR, 'Upload')
    APP_SVN_DIR = os.path.join(TRANSLATION_DIR, 'svn')
    WIN_SETUP_ALL_HEADER_FILE = os.path.join('rep', 'header')
    CACHE_FILE_DIR = os.path.join(TRANSLATION_DIR, 'cache')
    LOG_DIR = 'log'
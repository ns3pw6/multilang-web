import os

class Config():
    # BASE SETTINGS
    BASE_URL = ''
    MAINTAINER_NAME = 'yanhuang'

    # SECRET_KEY = os.urandom(16)
    SECRET_KEY = b'\xaeS%\xca\xab=Il8\x17\xc2\xad\x0c4\xdat'

    # DB
    DB_TYPE = 'mysql+pymysql://'
    DB_HOST = 'mariadb'
    DB_DATABASE = 'mlw'
    DB_USER = 'admin'
    DB_PASSWORD = 'root'
    
    # PATH
    WORK_DIRECTORY = os.getcwd()
    TRANSLATION_DIR = os.path.join(WORK_DIRECTORY, 'data')
    APP_SOURCE_IN_DIR = os.path.join(TRANSLATION_DIR, 'source-in')
    APP_SOURCE_OUT_DIR = os.path.join(TRANSLATION_DIR, 'source-out')
    APP_EXCEL_IN_DIR = os.path.join(TRANSLATION_DIR, 'excel-in')
    APP_EXCEL_OUT_DIR = os.path.join(TRANSLATION_DIR, 'excel-out')
    CACHE_FILE_DIR = os.path.join(TRANSLATION_DIR, 'cache')
    LOG_DIR = 'log'
    
    LANGUAGE_LIST = ['en-US', 'zh-TW', 'zh-CN', 'de-DE', 'ja-JP', 'it-IT', 
                     'fr-FR', 'nl-NL', 'ru-RU', 'ko-KR', 'pl', 'cs', 
                     'sv', 'da', 'no', 'fi', 'pt', 'es', 'hu', 'tr', 
                     'es-latino', 'th']
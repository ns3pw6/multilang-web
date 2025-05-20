PATTERNS = {
    'webUI_json': r'([\w]+)\s*=\s*(\{.*\})\s*;',
    'win': {
        'xaml': r'[\s]*<[\s]*sys:String[\s]+x:Key=[\s]*\"([\w]+)\"(?:[.]*xml:space=\"preserve\")?[\s\S]*?>([\s\S]*?)<\/sys:String>',
        'isl': r'(\w+)=([^\n]*)',
        'rc': r'(?:[\s]+)(IDS_[\w_]+)(?:[\s]+)"((?:[^"\\]|\\.)*)"',
    },
    'normal': {
        1: r"(?m)^(?!\s*//)([\w\.]+)\s*=\s*'((?:[^'\\]|\\.)*)'",
        3: r'"([^"]+)"\s*=\s*"([^"]+)"\s*;',
        4: r'<string name="([\w]+)">"(.*?)"</string>',
        5: r'"([^"]+)"\s*=\s*"([^"]+)"\s*;',
        7: r'(\w+)\s*=\s*(.*)'
    }
}

WEBUI_JSON_APPS = [
    "test",
]

WIN_SETUP_PATTERNS = {
    'en-US': r'LANGUAGE LANG_ENGLISH, SUBLANG_ENGLISH_US(.*?)#endif\s+//[\s]*英文[\s]*\(美國\)[\s]*resources',
    'zh-TW': r'LANGUAGE LANG_CHINESE, SUBLANG_CHINESE_TRADITIONAL(.*?)#endif\s+//[\s]*中文[\s]*\(繁體，台灣\)[\s]*resources',
    'zh-CN': r'LANGUAGE LANG_CHINESE, SUBLANG_CHINESE_SIMPLIFIED(.*?)#endif\s+//[\s]*中文[\s]*\(簡體，中華人民共和國\)[\s]*resources',
    'de-DE': r'LANGUAGE LANG_GERMAN, SUBLANG_GERMAN(.*?)#endif\s+//[\s]*德文[\s]*\(德國\)[\s]*resources',
    'ja-JP': r'LANGUAGE LANG_JAPANESE, SUBLANG_DEFAULT(.*?)#endif\s+//[\s]*日文[\s]*\(日本\)[\s]*resources',
    'it-IT': r'LANGUAGE LANG_ITALIAN, SUBLANG_ITALIAN(.*?)#endif\s+//[\s]*義大利文[\s]*\(義大利\)[\s]*resources',
    'fr-FR': r'LANGUAGE LANG_FRENCH, SUBLANG_FRENCH(.*?)#endif\s+//[\s]*法文[\s]*\(法國\)[\s]*resources',
    'nl-NL': r'LANGUAGE LANG_DUTCH, SUBLANG_DUTCH(.*?)#endif\s+//[\s]*荷蘭文[\s]*\(荷蘭\)[\s]*resources',
    'ru-RU': r'LANGUAGE LANG_RUSSIAN, SUBLANG_DEFAULT(.*?)#endif\s+//[\s]*俄文[\s]*\(俄羅斯\)[\s]*resources',
    'ko-KR': r'LANGUAGE LANG_KOREAN, SUBLANG_DEFAULT(.*?)#endif\s+//[\s]*韓文[\s]*\(韓國\)[\s]*resources',
    'pl': r'LANGUAGE LANG_POLISH, SUBLANG_DEFAULT(.*?)#endif\s+//[\s]*波蘭文[\s]*\(波蘭\)[\s]*resources',
    'cs': r'LANGUAGE LANG_CZECH, SUBLANG_DEFAULT(.*?)#endif\s+//[\s]*捷克文[\s]*\(捷克共和國\)[\s]*resources',
    'sv': r'LANGUAGE LANG_SWEDISH, SUBLANG_SWEDISH(.*?)#endif\s+//[\s]*瑞典文[\s]*\(瑞典\)[\s]*resources',
    'da': r'LANGUAGE LANG_DANISH, SUBLANG_DEFAULT(.*?)#endif\s+//[\s]*丹麥文[\s]*\(丹麥\)[\s]*resources',
    'no': r'LANGUAGE LANG_NORWEGIAN, SUBLANG_NORWEGIAN_BOKMAL(.*?)#endif\s+//[\s]*挪威文、巴克摩[\s]*\(挪威\)[\s]*resources',
    'fi': r'LANGUAGE LANG_FINNISH, SUBLANG_DEFAULT(.*?)#endif\s+//[\s]*芬蘭文[\s]*\(芬蘭\)[\s]*resources',
    'pt': r'LANGUAGE LANG_PORTUGUESE, SUBLANG_PORTUGUESE(.*?)#endif\s+//[\s]*葡萄牙文[\s]*\(葡萄牙\)[\s]*resources',
    'es': r'LANGUAGE LANG_SPANISH, SUBLANG_SPANISH_MODERN(.*?)#endif\s+//[\s]*西班牙文[\s]*\(西班牙，國際排序\)[\s]*resources',
    'hu': r'LANGUAGE LANG_HUNGARIAN, SUBLANG_DEFAULT(.*?)#endif\s+//[\s]*匈牙利文[\s]*\(匈牙利\)[\s]*resources',
    'tr': r'LANGUAGE LANG_TURKISH, SUBLANG_DEFAULT(.*?)#endif\s+//[\s]*土耳其文[\s]*\(土耳其\)[\s]*resources',
}

LANGUAGE_LIST = ['en-US', 'zh-TW', 'zh-CN', 'de-DE', 'ja-JP', 'it-IT', 
                 'fr-FR', 'nl-NL', 'ru-RU', 'ko-KR', 'pl', 'cs', 
                 'sv', 'da', 'no', 'fi', 'pt', 'es', 'hu', 'tr', 
                 'es-latino', 'th']

LANGUAGE_ENCODINGS = {
    'zh-TW': 'BIG5',       # Traditional Chinese
    'zh-CN': 'GB2312',     # Simplified Chinese
    'de-DE': 'ISO-8859-9', # German
    'tr': 'ISO-8859-9',    # Turkish
    'pt': 'ISO-8859-9',    # Portuguese (Portugal)
    'no': 'ISO-8859-9',    # Norwegian (Norsk)
    'it-IT': 'ISO-8859-9', # Italian
    'fr-FR': 'ISO-8859-9', # French
    'nl-NL': 'ISO-8859-9', # Dutch
    'pl': 'ISO-8859-9',    # Polish
    'cs': 'ISO-8859-9',    # Czech
    'sv': 'ISO-8859-9',    # Swedish (Svenska)
    'da': 'ISO-8859-9',    # Danish (Dansk)
    'fi': 'ISO-8859-9',    # Finnish (Suomi)
    'es': 'ISO-8859-9',    # Spanish
    'hu': 'ISO-8859-9',    # Hungarian
    'ru-RU': 'KOI8-R',     # Russian
    'ja-JP': 'Shift_JIS',  # Japanese
    'ko-KR': 'euc-kr',     # Korean
    'es-latino': 'UTF-8',  # Latin American Spanish (considered as 'ISO-8859-9')
    'th': 'UTF-8'          # Thai (UTF-8 as default or as common choice)
}

LANGUAGE_DATA = {
    'en-US': {
      'mac_dir': ['en.lproj', 'en-US.lproj'],
      'win_setup_all': 'English.isl',
      'chrome_dir': 'en',
      'android_dir': 'values',
    },
    'zh-TW': {
        'mac_dir': ['zh-Hant.lproj', 'zh-Hant-TW.lproj'],
        'win_setup_all': 'ChineseTrad.isl',
        'chrome_dir': 'zh-TW',
        'android_dir': 'values-zh-rTW',
        'win_xaml': 'zh-TW',
    },
    'zh-CN': {
        'mac_dir': ['zh-Hans.lproj', 'zh-Hans-CN.lproj'],
        'win_setup_all': 'ChineseSimp.isl',
        'chrome_dir': 'zh-CN',
        'android_dir': 'values-zh-rCN',
        'win_xaml': 'zh-CN',
    },
    'de-DE': {
        'mac_dir': ['de.lproj'],
        'win_setup_all': 'German.isl',
        'chrome_dir': 'de',
        'android_dir': 'values-de',
        'win_xaml': 'de-DE',
    },
    'ja-JP': {
        'mac_dir': ['ja.lproj'],
        'win_setup_all': 'Japanese.isl',
        'chrome_dir': 'ja',
        'android_dir': 'values-ja',
        'win_xaml': 'ja-JP',
    },
    'it-IT': {
        'mac_dir': ['it.lproj'],
        'win_setup_all': 'Italian.isl',
        'chrome_dir': 'it',
        'android_dir': 'values-it',
        'win_xaml': 'it-IT',
    },
    'fr-FR': {
        'mac_dir': ['fr.lproj'],
        'win_setup_all': 'French.isl',
        'chrome_dir': 'fr',
        'android_dir': 'values-fr',
        'win_xaml': 'fr-FR',
    },
    'nl-NL': {
        'mac_dir': ['nl.lproj'],
        'win_setup_all': 'Dutch.isl',
        'chrome_dir': 'nl',
        'android_dir': 'values-nl',
        'win_xaml': 'nl-NL',
    },
    'ru-RU': {
        'mac_dir': ['ru.lproj'],
        'win_setup_all': 'Russian.isl',
        'chrome_dir': 'ru',
        'android_dir': 'values-ru',
        'win_xaml': 'ru-RU',
    },
    'ko-KR': {
        'mac_dir': ['ko.lproj'],
        'win_setup_all': 'Korean.isl',
        'chrome_dir': 'ko',
        'android_dir': 'values-ko',
        'win_xaml': 'ko-KR',
    },
    'pl': {
        'mac_dir': ['pl.lproj'],
        'win_setup_all': 'Polish.isl',
        'chrome_dir': 'pl',
        'android_dir': 'values-pl',
        'win_xaml': 'pl-pl',
    },
    'cs': {
        'mac_dir': ['cs.lproj'],
        'win_setup_all': 'Czech.isl',
        'chrome_dir': 'cs',
        'android_dir': 'values-cs',
        'win_xaml': 'cs-cz',
    },
    'sv': {
        'mac_dir': ['sv.lproj'],
        'win_setup_all': 'Swedish.isl',
        'chrome_dir': 'sv',
        'android_dir': 'values-sv',
        'win_xaml': 'sv-se',
    },
    'da': {
        'mac_dir': ['da.lproj'],
        'win_setup_all': 'Danish.isl',
        'chrome_dir': 'da',
        'android_dir': 'values-da',
        'win_xaml': 'da-dk',
    },
    'no': {
        'mac_dir': ['nb.lproj'],  # Note: 'nb' for Norwegian Bokmål
        'win_setup_all': 'Norwegian.isl',
        'chrome_dir': 'no',
        'android_dir': 'values-no',
        'win_xaml': 'nb-no',
    },
    'fi': {
        'mac_dir': ['fi.lproj'],
        'win_setup_all': 'Finnish.isl',
        'chrome_dir': 'fi',
        'android_dir': 'values-fi',
        'win_xaml': 'fi-fi',
    },
    'pt': {
        'mac_dir': ['pt.lproj'],
        'win_setup_all': 'Portuguese.isl',
        'chrome_dir': 'pt_PT',
        'android_dir': 'values-pt',
        'win_xaml': 'pt-pt',
    },
    'es': {
        'mac_dir': ['es.lproj'],
        'win_setup_all': 'Spanish.isl',
        'chrome_dir': 'es',
        'android_dir': 'values-es-rES',
        'win_xaml': 'es-es',
    },
    'hu': {
        'mac_dir': ['hu.lproj'],
        'win_setup_all': 'Hungarian.isl',
        'chrome_dir': 'hu',
        'android_dir': 'values-hu-rHU',
        'win_xaml': 'hu-hu',
    },
    'tr': {
        'mac_dir': ['tr.lproj'],
        'win_setup_all': 'Turkish.isl',
        'chrome_dir': 'tr',
        'android_dir': 'values-tr-rTR',
        'win_xaml': 'tr-tr',
    },
    'es-latino': {
        'mac_dir': ['es-419.lproj'],
        'win_setup_all': 'es-latino.isl',
        'chrome_dir': 'es_419',
        'android_dir': 'values-es-rUS',
        'win_xaml': 'es-latino',
    },
    'th': {
        'mac_dir': ['th.lproj'],
        'win_setup_all': 'th.isl',
        'chrome_dir': 'th',
        'android_dir': 'values-th',
        'win_xaml': 'th',
    },
}
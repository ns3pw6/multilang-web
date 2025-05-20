from flask import jsonify, Response
from collections import Counter
import re

def validate_language_data(data: dict) -> None | Response:
    """Validate the language data."""
    required_fields = ['tag', 'en', 'zh']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({'msg': f'Missing required fields: {", ".join(missing_fields)}'}), 400
    
    return None

def process_special_char(str: str) -> list:
    """Process special characters in a string."""
    pattern_filter = {
        'lb': '\n',
        'tab': '\t',
        'ADM_var': r'(\{(\d+)\})',
        'other': r'(\|([^|]+)\|)|(%s)|(%@)'
    }
    
    num_line_break = str.count(pattern_filter['lb'])
    num_tan = str.count(pattern_filter['tab'])

    match_var = re.findall(pattern_filter["ADM_var"], str)
    num_var = [m[0] for m in match_var if m[0]]
    num_var.sort()

    match_other = re.findall(pattern_filter["other"], str)
    match_other = len([m[0] for m in match_other if m[0]])

    return {
        'line_break': num_line_break,
        'tab': num_tan,
        'ADM_var': num_var,
        'other': match_other
    }
    
def compare_special_char(en, other):
    missing = {}
    extra = {}

    for key, value in en.items():
        if key == 'ADM_var':
            missing_vars = __compare_var_counts(value, other[key])
            extra_vars = __compare_var_counts(other[key], value)
            missing[key] = missing_vars
            extra[key] = extra_vars
        else:
            missing[key] = value - other[key]
            extra[key] = other[key] - value

    diff_parts = __generate_response(missing, False) + __generate_response(extra, True)
    return ', '.join(diff_parts)

def __compare_var_counts(main, secondary):
    missing_vars = []
    main_counts = Counter(main)
    secondary_counts = Counter(secondary)

    for var, count in main_counts.items():
        diff = count - secondary_counts.get(var, 0)
        if diff > 0:
            missing_vars.extend([var] * diff)

    return missing_vars

def __generate_response(arr, is_extra=False):
    messages = []
    key_mapping = {
        'line_break': '換行符號',
        'tab': 'Tab符號',
        'ADM_var': '變數',
        'other': '其他特殊符號'
    }

    for key, value in arr.items():
        if not value:
            continue

        postfix = None
        if isinstance(value, int):
            if value <= 0:
                continue
            postfix = f"{value}個"
        elif isinstance(value, list):
            postfix = ', '.join(value)

        prefix = "多餘" if is_extra else "缺少"
        label = key_mapping.get(key, key)
        messages.append(f"{prefix}{label}: {postfix}")

    return messages

def check_app_string_format(result_set, languages):
    strings = __parse_result_set(result_set, languages)
    analysis = __analyze_special_characters(strings)

    return analysis

def __parse_result_set(result_set, languages):
    strings = {}
    lang_tags = list(languages.keys())

    for row in result_set:
        strings[row.str_id] = {}
        for lang_tag in lang_tags:
            lang_tag = lang_tag.strip('` ')
            strings[row.str_id][lang_tag] = getattr(row, lang_tag)

    return strings

def __analyze_special_characters(strings):
    result = {}

    for str_id, translations in strings.items():
        en_string = translations.get('en-US', '')

        en_special_char = process_special_char(en_string)
        has_error = False
        errors = {}

        for lang_tag, content in translations.items():
            if lang_tag == 'en-US' or not content:
                continue

            tmp_special_char = process_special_char(content)
            if en_special_char != tmp_special_char:
                has_error = True
                errors[lang_tag] = {
                    'error_msg': compare_special_char(en_special_char, tmp_special_char),
                    'string': content
                }

        if has_error:
            result[str_id] = errors
            result[str_id]['en-US'] = en_string

    return result
import re
import json
import pandas as pd
from server import logger
from model.separator import SeparatorModel
from model.dbModel import Separator
from utility.file_utils import detect_file_encoding, read_header
from config.parser_config import PATTERNS, WEBUI_JSON_APPS, WIN_SETUP_PATTERNS
from typing import Tuple, Dict
from openpyxl import load_workbook

class ParserService(object):
    
    def __init__(self) -> None:
        self.result = {}
        self.webUI_json = set(WEBUI_JSON_APPS)
        self.normal_pattern = PATTERNS['normal']
        self.webUI_json_pattern = PATTERNS['webUI_json']
        self.win_pattern = PATTERNS['win']
        self.win_setup_all_pattern = WIN_SETUP_PATTERNS

    def __remove_trailing_commas(self, content: str) -> str:
        """Remove trailing commas from JSON-like content."""
        return re.sub(r',(\s*[}\]])', r'\1', content)

    def __normalize_escape_sequences(self, data: str, revert: bool = False) -> str:
        """Normalize escape sequences in the given string."""
        replacements = {
            '\\"': '\\&#34',
            '\\': '&#92',
        }
        if revert:
            replacements = dict(reversed(list(replacements.items())))
        for old, new in replacements.items():
            if revert:
                data = data.replace(new, old)
            else:
                data = data.replace(old, new)
        return data
    
    def __strip_json_comments(self, content: str) -> str:
        """Remove comments from JSON-like content."""
        http_placeholder = '__HTTP_PLACEHOLDER__'
        https_placeholder = '__HTTPS_PLACEHOLDER__'
        
        content = content.replace('http://', http_placeholder)
        content = content.replace('https://', https_placeholder)
        content = re.sub(r'//.*', '', content)
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        content = content.replace(http_placeholder, 'http://')
        content = content.replace(https_placeholder, 'https://')
        
        return content
    
    def __convert_to_json(self, data: str) -> str:
        """Convert string to valid JSON format."""
        data = self.__strip_json_comments(data)
        data = self.__remove_trailing_commas(data)
        data = self.__normalize_escape_sequences(data)
        
        return data
    
    def __flatten_dict(self, data: Dict, separator: str, parent_key: str = '') -> Dict:
        """Flatten a nested dictionary."""
        items = {}
        for key, value in data.items():
            new_key = f"{parent_key}{separator}{key}" if parent_key else key
            if isinstance(value, dict):
                items.update(self.__flatten_dict(value, separator, new_key))
            else:
                items[new_key] = self.__normalize_escape_sequences(value, revert=True)
        return items

    def __parse_webUI_json(self, platform_id: int, source_file: str) -> Dict:
        """
        Parse WebUI JSON files with specific formatting.

        Args:
            platform_id (int): ID of the platform for separator retrieval.
            source_file (str): Path to the WebUI JSON file to be parsed.

        Returns:
            dict: Parsed and flattened content or error message.
        """
        try:
            with open(source_file, 'r') as f:
                content = f.read()
            
            file_format = source_file.rsplit('.', 1)[-1]
            sep_model = SeparatorModel()
            sep_id = sep_model.get_sep_type(platform_id, file_format)
            separator = Separator.query.filter_by(sep_id = sep_id).first().type
            pattern = re.compile(self.webUI_json_pattern, re.DOTALL)
            match = pattern.search(content)

            if match:
                prefix = match.group(1)
                json_data = self.__convert_to_json(match.group(2))
                parsed_json = json.loads(json_data, strict=False)
                self.result = self.__flatten_dict(parsed_json, separator, prefix)

        except FileNotFoundError:
            logger.error(f"File {source_file} not found.")
            self.result = {'parse_error_msg': f"File not found: {source_file}"}
        except json.JSONDecodeError as json_err:
            logger.error(f"JSON decoding error in file {source_file}: {json_err}")
            self.result = {'parse_error_msg': f"JSON decoding error: {json_err}"}
        except Exception as e:
            logger.exception(f"Unexpected error processing file {source_file}: {e}")
            self.result = {'parse_error_msg': f"Unexpected error: {e}"}
        
        return self.result
    
    def __parse_Win(self, source_file: str) -> Dict:
        """
        Parse Windows-specific file formats (xaml, isl, rc).

        Args:
            source_file (str): Path to the Windows-specific file to be parsed.

        Returns:
            dict: Parsed content or error message.

        Raises:
            ValueError: If the file encoding cannot be recognized.
        """
        try:
            encoding = detect_file_encoding(source_file)
            with open(source_file, 'r', encoding=encoding) as f:
                content = f.read()
        except UnicodeDecodeError:
            logger.error(f"Unable to recognize the encoding of file: {source_file}")
            raise ValueError("File encoding format is not recognized")

        try:
            # Determine file format and apply appropriate parsing strategy
            file_format = source_file[source_file.rfind('.') + 1:]
            if file_format == 'xaml':
                pattern = re.compile(self.win_pattern['xaml'], re.DOTALL)
                matches = pattern.findall(content)
                self.result = {match[0]: match[1] for match in matches}
            elif file_format == 'isl':
                pattern = re.compile(r'\[Messages\](.*?)(?=\[\]|\Z)', re.DOTALL)
                exclude_LangOptions = pattern.search(content).group(1)
                pattern = re.compile(self.win_pattern['isl'], re.DOTALL)
                matches = pattern.findall(exclude_LangOptions)
                self.result = {match[0]: match[1] for match in matches}
            else:  # Assuming 'rc' file type
                pattern = self.win_setup_all_pattern['en-US']
                match = re.search(pattern, content, re.DOTALL)
                if match:
                    english_block = match.group(1)
                    matches = re.findall(self.win_pattern['rc'], english_block)
                    self.result = {match[0]: match[1] for match in matches}
        except Exception as e:
            logger.error(f"Error processing file {source_file}: {e}")
            self.result = {'parse_error_msg': f"Error reading or processing the file: {e}"}

        return self.result

    def __parse_Chrome(self, source_file: str) -> Dict:
        """Parse Chrome-specific JSON files."""
        try:
            with open(source_file, 'r') as f:
                content = f.read()

            content = json.loads(content)
            
            self.result = {key: value['message'] for key, value in content.items()}
        except FileNotFoundError:
            logger.error(f"File {source_file} not found.")
            self.result = {'parse_error_msg': f"File not found: {source_file}"}
        except json.JSONDecodeError as json_err:
            logger.error(f"JSON decoding error in file {source_file}: {json_err}")
            return {'parse_error_msg': f"Invalid JSON format: {json_err}"}
        except Exception as e:
            logger.error(f"Unexpected error processing file {source_file}: {e}")
            self.result = {'parse_error_msg': f"Error reading or processing the file: {e}"}
        return self.result
    
    def __parse_common_file(self, source_file: str, file_pattern: re) -> Dict:
        """Parse files using a common pattern-based approach."""
        try:
            with open(source_file, 'r') as f:
                content = f.read()

            pattern = re.compile(file_pattern)

            matches = pattern.findall(content)
            
            for match in matches:
                self.result[match[0]] = match[1]

        except FileNotFoundError:
            logger.error(f"File {source_file} not found.")
            self.result = {'parse_error_msg': f"File not found: {source_file}"}
        except UnicodeDecodeError as e:
            logger.error(f"Encoding error when reading file {source_file}: {e}")
            self.result = {'parse_error_msg': f"Encoding error: {e}"}
        except re.error as e:
            logger.error(f"Regex error while processing file {source_file}: {e}")
            self.result = {'parse_error_msg': f"Regex error: {e}"}
        except Exception as e:
            logger.exception(f"Unexpected error processing file {source_file}: {e}")
            self.result = {'parse_error_msg': f"Unexpected error: {e}"}
        return self.result

    def __export_win(self, data: Dict) -> Tuple[bool, str]:
        """
        Export translations for Windows-specific file formats (xaml, isl, rc).

        Args:
            data (dict): Contains translation data and file information.

        Returns:
            tuple[bool, str]: Success status and updated content or error message.
        """
        lang_code = data['lang_code']
        translations = data['translations']
        try:
            encoding = detect_file_encoding(data['input_file'])
            with open(data['input_file'], 'r', encoding=encoding) as f:
                original_content = f.read()
        except UnicodeDecodeError:
            raise ValueError("File encoding format is not recognized")
        
        try:
            file_format = data['input_file'][data['input_file'].rfind('.') + 1:]
            if file_format == 'xaml':
                pattern = r'([\s]*)<[\s]*sys:String[\s]+x:Key=[\s]*\"([\w]+)\"(?:[\s]+xml:space=\"preserve\")?[\s\S]*?>([\s\S]*?)<\/sys:String>'
                content = original_content
            elif file_format == 'isl':
                if lang_code == 'es-latino' or lang_code == 'th':
                    return False, 'continue'
                header = read_header(lang_code)
                pattern = re.compile(r'(\[Messages\].*?)(?=\[\]|\Z)', re.DOTALL)
                exclude_LangOptions = pattern.search(original_content).group(1)
                content = header + exclude_LangOptions
                pattern = self.win_pattern['isl']
            elif file_format == 'rc':
                if lang_code not in self.win_setup_all_pattern:
                    return False, 'continue'
                pattern = self.win_setup_all_pattern[lang_code]
                match = re.search(pattern, original_content, re.DOTALL)
                if match:
                    content = match.group(1)
                    pattern = r'([\s]+)(IDS_[\w_]+)([\s]+)"((?:[^"\\]|\\.)*)"'
                else:
                    return False, f"Language block not found for {lang_code}"
            else:
                return False, f"Unsupported file format: {file_format}"
            
            def replace_value(match):
                """Replace matched strings with translations based on file format."""
                if file_format == 'xaml':
                    indent, key, _ = match.groups()
                    preserve_tag = ' xml:space="preserve"' if 'xml:space="preserve"' in match.group(0) else ''
                elif file_format == 'rc':
                    indent1, key, indent2, _ = match.groups()
                else:
                    key, _ = match.groups()

                if key in translations and lang_code in translations[key]:
                    translated_value = translations[key][lang_code]
                    if file_format == 'xaml':
                        return f'{indent}<sys:String x:Key="{key}"{preserve_tag}>{translated_value}</sys:String>'
                    elif file_format == 'isl':
                        return f'{key}={translated_value}'
                    elif file_format == 'rc':
                        return f'{indent1}{key}{indent2}"{translated_value}"'
                return match.group(0)

            updated_content = re.sub(pattern, replace_value, content)

            if file_format == 'rc':
                # Merge the updated content back into the original content for rc files
                updated_original_content = re.sub(self.win_setup_all_pattern[lang_code], 
                                                lambda m: m.group(0).replace(m.group(1), updated_content), 
                                                original_content, 
                                                flags=re.DOTALL)
                return True, updated_original_content
            else:
                return True, updated_content
            
        except Exception as e:
            logger.error(f"Error during export process for {data['input_file']}: {e}")
            return False, f'Error reading or processing the file: {e}'

    def __export_pattern_based(self, data: Dict, p_id: int) -> Tuple[bool, str]:
        """
        Export translations based on pattern matching for different platforms.

        Args:
            data (dict): Contains translation data and file information.
            p_id (int): Platform ID to determine the export format.

        Returns:
            tuple[bool, str]: Success status and updated content or error message.
        """
        lang_code = data['lang_code']
        pattern = self.normal_pattern[p_id]
        if p_id == 4:
            # Android XML resource pattern: matches <string> elements
            # Captures: (1) resource name, (2) entire value, (3) value without quotes
            pattern = r'<string name="([\w]+)">((?:")?([^"]+)(?:")?)</string>'
        translations = data['translations']
        try:
            with open(data['input_file'], 'r') as f:
                content = f.read()
            
            def replace_value(match):
                """Replace matched strings with translations based on platform."""
                key = match.group(1)
                if key in translations and lang_code in translations[key]:
                    translated_value = translations[key][lang_code]
                    if p_id == 1:  # WebUI
                        return f"{key} = '{translated_value}'"
                    elif p_id == 3 or p_id == 5:  # Mac and iOS
                        return f'"{key}" = "{translated_value}";'
                    elif p_id == 4:  # Android
                        if match.group(2).startswith('"') and match.group(2).endswith('"'):
                            return f'<string name="{key}">"{translated_value}"</string>'
                        else:
                            return f'<string name="{key}">{translated_value}</string>'
                    elif p_id == 7:  # Firefox
                        return f"{key}={translated_value}"
                return match.group(0)   # Return original if no translation found
            
            # Apply translations using regex substitution
            updated_content = re.sub(pattern, replace_value, content)
            return True, updated_content
        except Exception as e:
            logger.error(f"Error reading or processing the file: {e}")
            return False, f'Error reading or processing the file: {e}'
    
    def __export_json_based(self, data: Dict, is_webUI: bool) -> Tuple[bool, str]:
        """
        Export translations for JSON-based file formats, including WebUI JSON.

        Args:
            data (dict): Contains translation data and file information.
            is_webUI (bool): Flag to indicate if the file is a WebUI JSON format.

        Returns:
            tuple[bool, str]: A tuple containing:
                - bool: Success status of the export operation.
                - str: Updated content if successful, or error message if failed.
        """
        lang_code = data['lang_code']
        translations = data['translations']
        pre_namespace = ''
        try:
            with open(data['input_file'], 'r') as f:
                content = f.read()
            
            if is_webUI:
                pattern = re.compile(self.webUI_json_pattern, re.DOTALL)
                match = pattern.search(content)
                if match:
                    pre_namespace = match.group(1)
                    content = self.__convert_to_json(match.group(2))
                else:
                    return False, 'Pattern not found in content'
            
            content = json.loads(content)

            if is_webUI:
                for key1, value1 in content.items():
                    mid_namespace = f"{pre_namespace}.{key1}"
                    for key2, _ in value1.items():
                        namespace = f"{mid_namespace}.{key2}"
                        if namespace in translations and lang_code in translations[namespace]:
                            content[key1][key2] = translations[namespace][lang_code]
            else:
                for key, value in content.items():
                    if key in translations and lang_code in translations[key]:
                        value['message'] = translations[key][lang_code]
                        
            content = json.dumps(content, ensure_ascii=False, indent=4)
            content = self.__normalize_escape_sequences(content, revert=True)

            if is_webUI:
                content = f'{pre_namespace} = {content}'
            return True, content
        except Exception as e:
            logger.error(f"Error reading or processing the file: {e}")
            return False, f'Error reading or processing the file: {e}'
    
    def parse_excel_file(self, file_path: str) -> pd.DataFrame:
        """Parse the first sheet of an Excel file into a DataFrame."""
        sheet = load_workbook(filename=file_path, data_only=True).active
        df = pd.DataFrame(sheet.values)
        return df
    
    def process_excel_data(self, df: pd.DataFrame) -> Dict:
        """Process DataFrame and return a dictionary of the data."""
        if df.empty or df.shape[0] < 2:
            raise ValueError("DataFrame is empty or does not have enough rows.")
        mode = 0
        headers = df.iloc[0].tolist()
        lang_tags = headers[1:]
        datas = {}

        if df.iloc[0, 1] == 'lang_tag':
            mode = 1

        for _, row in df.iloc[1:].iterrows():
            str_id = row[0]
            if pd.notna(str_id): 
                str_id = str(int(str_id))
                if str_id not in datas:
                    datas[str_id] = {}
                if mode == 0:
                    for col, lang_tag in enumerate(lang_tags, start=1):
                        content = row[col]
                        if not lang_tag:
                            continue
                        datas[str_id][lang_tag] = str(content) if pd.notna(content) else None
                else:
                    lang_tag = row[1]
                    content = row[3]
                    datas[str_id][lang_tag] = str(content) if pd.notna(content) else None

        return datas
    
    def parse_file(self, p_id: int, app_name: str, source_file: str) -> Dict:
        """Parse the given file based on platform ID and app name."""
        self.result.clear()

        if p_id == 1 and app_name in self.webUI_json:
            return self.__parse_webUI_json(p_id, source_file)
        elif p_id == 2:
            return self.__parse_Win(source_file)
        elif p_id == 6:
            return self.__parse_Chrome(source_file)
        else:
            return self.__parse_common_file(source_file, self.normal_pattern[p_id])
    
    def generate_svn_file_content(self, data: Dict) -> str:
        """Generate SVN file content based on the given data."""
        p_id = int(data['p_id'])
        if p_id == 1 and data['app_name'] in self.webUI_json:
            return self.__export_json_based(data, True)
        elif p_id == 2:
            return self.__export_win(data)
        elif p_id == 6:
            return self.__export_json_based(data, False)
        else:
            return self.__export_pattern_based(data, p_id)

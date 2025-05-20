import os
import shutil
import chardet
import tempfile
import xlsxwriter
from server import logger
from config.directory_config import (
    SOURCE_OUT_DIRECTORY, 
    EXCEL_OUT_DIRECTORY, 
    WIN_SETUP_ALL_HEADER_DIRECTORY
)
from contextlib import suppress
from typing import Tuple, Dict
from concurrent.futures import ProcessPoolExecutor, as_completed

def check_directory_exists(directory: str) -> None:
    """Create a directory if it doesn't exist."""
    with suppress(FileExistsError):
        os.makedirs(directory, 0o755, exist_ok=True)

def archive_files(directory: str, app: str) -> str:
    """Archive files in a directory into a zip file."""
    check_directory_exists(SOURCE_OUT_DIRECTORY)
    unique_dir = tempfile.mkdtemp(dir=SOURCE_OUT_DIRECTORY)
    shutil.make_archive(os.path.join(unique_dir, app), 'zip', directory)
    return os.path.join(unique_dir, f'{app}.zip')

def save_to_xlsx(data, file_name, output_dir, proofread=False) -> None:
    """Save data to excel file"""
    file_path = os.path.join(output_dir, file_name)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with xlsxwriter.Workbook(file_path) as workbook:
        worksheet = workbook.add_worksheet()

        headers = list(data[0].keys()) if data else []
        for col_num, header in enumerate(headers):
            worksheet.write(0, col_num, header)
        start = 0 if proofread else 1
        for row_num, row in enumerate(data, start=start):
            for col_num, (_, value) in enumerate(row.items()):
                worksheet.write(row_num, col_num, value)
                
        worksheet.set_column(1, len(headers) - 1, 30)

def generate_excel(data: Dict, type: str, eng_string: Dict = {}) -> Tuple[bool, str | None]:
    """Generate Excel files from provided data using xlsxwriter."""
    check_directory_exists(EXCEL_OUT_DIRECTORY)
    
    try:
        # Create a unique temporary directory for this request
        unique_dir = tempfile.mkdtemp(dir=EXCEL_OUT_DIRECTORY)
        futures = []
        
        with ProcessPoolExecutor() as executor:
            if type == 'dfe':
                futures = [
                    executor.submit(
                        save_to_xlsx,
                        [{'String ID': str_id, **data_dict.get(str_id, {})} for str_id in data_dict],
                        f'{key[0]}_{key[1]}.xlsx',
                        os.path.join(unique_dir, key[0], key[1])
                    )
                    for key, data_dict in data.items()
                ]
            elif type == 'due':
                futures = [
                    executor.submit(
                        save_to_xlsx,
                        [{'String ID': str_id, 'en-US': eng_string.get(str_id, ''), lang_code: ''}
                         for str_id in str_ids],
                        f'{key[0]}_{key[1]}_{lang_code}.xlsx',
                        os.path.join(unique_dir, key[0], key[1], lang_code)
                    )
                    for key, lang_ids in data.items()
                    for lang_code, str_ids in lang_ids.items()
                ]
            elif type == 'dsr':
                strings, langs = data['strings'], data['selectedLanguages']
                data_list = [
                    {'String ID': int(str_id), **{lang: values.get('translations', {}).get(lang, '') 
                    for lang in langs}}
                    for str_id, values in strings.items()
                ]
                futures.append(executor.submit(save_to_xlsx, data_list, 'search_results.xlsx', unique_dir))
            elif type == 'dpr':
                data_list = [{'zh-TW': string} for _, string in data]
                save_to_xlsx(data_list, f'export_excel.xlsx', unique_dir)

            # Wait for all futures to complete
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Error while processing task: {str(e)}", exc_info=True)
                    continue

        return True, None, unique_dir
    except Exception as e:
        logger.error(f"Unexpected error in generate_excel: {str(e)}", exc_info=True)
        return False, str(e), None

def generate_svn_file(content, output_dir, file_name, encoding='UTF-8') -> Tuple[bool, str]:
    """Generate a file for SVN with given content."""
    check_directory_exists(output_dir)
    file_path = os.path.join(output_dir, file_name)
    try:
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
        return True, file_path
    except UnicodeEncodeError as e:
        logger.error(f"Encoding error: {e}")
        raise UnicodeEncodeError(
            'ascii', 
            content, 
            e.start, 
            e.end, 
            f"Encoding error: 此翻譯中含有錯誤編碼無法產生檔案{file_name}，請重新確認"
        )
    except PermissionError as e:
        logger.error(f"Permission error: {str(e)}")
        return False, f"Permission error: {str(e)}"
    except Exception as e:
        logger.error(f"Unexcepted error: {str(e)}", exc_info=True)
        return False, str(e)

def cleanup_files(directory: str) -> None:
    """Remove a directory and all its contents."""
    try:
        if directory:
            check_directory_exists(directory)
            shutil.rmtree(directory)
    except FileNotFoundError:
        logger.error(f"Directory not found: {directory}")
    except Exception as e:
        logger.error(f"Failed to clean up files in {directory}: {str(e)}", exc_info=True)

def detect_file_encoding(file_path: str) -> str:
    """Detect the encoding of a file."""
    with open(file_path, 'rb') as f:
        raw_data = f.read()
    return chardet.detect(raw_data)['encoding']

def read_header(lang_code: str) -> str:
    """Read the win setup all header file for a specific language."""
    header_file = os.path.join(WIN_SETUP_ALL_HEADER_DIRECTORY, f'{lang_code}.txt')
    try:
        with open(header_file, 'r') as f:
            content = f.read()
        return content
    except FileNotFoundError as e:
        logger.error(f"Header file not found for language {lang_code}: {str(e)}")
        return ""
    except Exception as e:
        logger.error(f"Failed to read header file for language {lang_code}: {str(e)}", exc_info=True)
        return ""

def move_file(source_path: str, destination_path: str, name: str) -> None:
    """Move a file to a new location."""
    if not os.path.exists(source_path):
        return False
    
    check_directory_exists(destination_path)
    try:
        shutil.move(source_path, os.path.join(destination_path, name))
        return True
    except FileNotFoundError as e:
        logger.error(f"Source file not found: {source_path}. Error: {str(e)}", exc_info=True)
    except PermissionError as e:
        logger.error(f"Permission denied when moving file {source_path} to {destination_path}{name}: {str(e)}", exc_info=True)
    except Exception as e:
        logger.error(f"Failed to move file {source_path} to {destination_path}{name}: {str(e)}", exc_info=True)
    
    return False

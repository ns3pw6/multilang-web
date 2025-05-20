import os
import shutil
import xlsxwriter
from server import logger
from contextlib import suppress
from typing import Dict, List

def check_directory_exists(directory: str) -> None:
    """Create a directory if it doesn't exist."""
    with suppress(FileExistsError):
        os.makedirs(directory, 0o755, exist_ok=True)

def cleanup(directories: List | str) -> None:
    """Remove a directory and all its contents."""
    if isinstance(directories, str):
        directories = [directories]
    
    try:
        for directory in directories:
            if directory:
                check_directory_exists(directory)
                for filename in os.listdir(directory):
                    file_path = os.path.join(directory, filename)
                    
                    if os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                    else:
                        os.remove(file_path)
    except FileNotFoundError:
        logger.error(f"Directory not found: {directory}")
    except Exception as e:
        logger.error(f"Failed to clean up files in {directory}: {str(e)}", exc_info=True)

def write_cache_excel(data: Dict) -> None:
    """Write data to an Excel file for caching using optimized method."""
    cleanup(data['target_dir'])
    
    filename = f"{data['platform']}_{data['app']}.xlsx"
    file_path = os.path.join(data['target_dir'], filename)

    with xlsxwriter.Workbook(file_path) as workbook:
        worksheet = workbook.add_worksheet()

        headers = list(data['strings'][0].keys()) if data else []
        for col_num, header in enumerate(headers):
            worksheet.write(0, col_num, header)
        
        for row_num, row in enumerate(data['strings'], start=1):
            for col_num, (_, value) in enumerate(row.items()):
                worksheet.write(row_num, col_num, value)
                
        worksheet.set_column(1, len(headers) - 1, 30)

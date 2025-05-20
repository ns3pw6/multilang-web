from flask import jsonify, request
from server import app, db, logger
from model.db import Updated
from utility.file_utils import write_cache_excel, cleanup
from typing import Dict, Tuple, List
from sqlalchemy import text
from collections import defaultdict
import threading, os, datetime, time
from concurrent.futures import ThreadPoolExecutor, as_completed

CACHE_FILE_DIRECTORY = app.config['CACHE_FILE_DIR']
SOURCE_IN_DIRECTORY = app.config['APP_SOURCE_IN_DIR']
SOURCE_OUT_DIRECTORY = app.config['APP_SOURCE_OUT_DIR']
EXCEL_OUT_DIRECTORY = app.config['APP_EXCEL_OUT_DIR']
LOCK_FILE = os.path.join(CACHE_FILE_DIRECTORY, '.lock')
LANGUAGE_MAPPING = {
    i: lang for i, lang in enumerate(
        app.config['LANGUAGE_LIST'], start=1
    )
}

MAX_WORKERS = os.cpu_count() << 1
lock = threading.Lock()

def collect_single_language(lang: str, data: Dict) -> None:
    items = tuple(data.items())
    
    rows = tuple({
        "String ID": str_id,
        "en-US": translations.get("en-US", ""),
        lang: translations.get(lang, "")
    } for str_id, translations in items)
    
    untranslated_rows = tuple(row for row in rows if not row[lang])
    return rows, untranslated_rows

def process_single_languague_dfe(lang: str, data: Dict, platform: str, app: str) -> None:
    target_dir = os.path.join(
        CACHE_FILE_DIRECTORY,
        'dfe',
        lang,
        platform,
        app
    )
    
    wrapped_data = {
        'platform': platform,
        'app': app,
        'target_dir': target_dir,
        'strings': data
    }
    
    thread = threading.Thread(target=write_cache_excel, args=(wrapped_data,))
    
    thread.start()
    thread.join()

def process_single_languague_due(lang: str, data: Dict, platform: str, app: str) -> None:
    target_dir = os.path.join(
        CACHE_FILE_DIRECTORY,
        'due',
        platform,
        app,
        lang
    )
    
    wrapped_data = {
        'platform': platform,
        'app': app,
        'target_dir': target_dir,
        'strings': data
    }
    
    thread = threading.Thread(target=write_cache_excel, args=(wrapped_data,))
    
    thread.start()
    thread.join()

def process_all_languages(data: Dict, platform: str, app: str) -> None:
    """Process all languages for a specific platform and app."""
    items = list(data[platform, app].items())
    all_strings = []
    
    chunk_size = 1000
    for i in range(0, len(items), chunk_size):
        chunk = items[i:i + chunk_size]
        chunk_strings = [{
            "String ID": str_id,
            "en-US": translations.get("en-US", ""),
            **{lang: translations.get(lang, "") for lang in LANGUAGE_MAPPING.values() if lang != "en-US"}
        } for str_id, translations in chunk]
        all_strings.extend(chunk_strings)

    target_dir = os.path.join(
        CACHE_FILE_DIRECTORY,
        'dfe',
        'all',
        platform,
        app,
    )
    write_cache_excel({
        'target_dir': target_dir,
        'strings': all_strings,
        'platform': platform,
        'app': app
    })

def process_tasks(formatted_results):
    all_tasks = []

    for (platform, app), data in formatted_results.items():
        all_tasks.append((process_all_languages, formatted_results, platform, app))
        
        for lang in LANGUAGE_MAPPING.values():
            if lang != "en-US":
                rows, untranslated_rows = collect_single_language(lang, data)

                if rows:
                    all_tasks.append((process_single_languague_dfe, lang, rows, platform, app))

                if untranslated_rows:
                    all_tasks.append((process_single_languague_due, lang, untranslated_rows, platform, app))
    
    return all_tasks

def check_updated() -> bool:
    """Check if any string has been updated."""
    try:
        folder_path = CACHE_FILE_DIRECTORY
        folder_mtime = os.path.getmtime(folder_path)
        folder_mtime_readable = datetime.datetime.fromtimestamp(folder_mtime)
        
        update_time = Updated.query.first().string_update_time
        if update_time:
            if update_time < folder_mtime_readable:
                return False
        return True
    except Exception as e:
        logger.error(f"Unexpected error when checking updated strings: {e}", exc_info=True)
        return jsonify({'msg': "DB error!"}), 500

def build_query(app_ids: List = []) -> Tuple:
    """Constructs an SQL query string dynamically based on the input filtering data."""
    raw_sql = """SELECT * FROM string_mapping WHERE p_id NOT IN (8, 9)"""
    if app_ids:
        ids = ', '.join(app_ids)
        raw_sql += f""" AND app_id IN ({ids})"""
    
    base_query = db.session.execute(text(raw_sql))
    return base_query

def format_result(results: tuple, target_lang_id: int = -1) -> Dict:
    """Formats the query results into a structured dictionary based on the given 'type'."""
    formatted_results = defaultdict(lambda: defaultdict(lambda: defaultdict(str)))

    for _, p_name, _, app_name, _, _, str_id, *lang_contents in results:
        key = (p_name, app_name)
        
        string_mapping = dict(zip(LANGUAGE_MAPPING.keys(), lang_contents))
        
        if target_lang_id != -1:
            formatted_results[key][str_id].update({
                LANGUAGE_MAPPING[1]: string_mapping[1],
                LANGUAGE_MAPPING[target_lang_id]: string_mapping[target_lang_id],
            })
        else:
            formatted_results[key][str_id] = dict(zip(LANGUAGE_MAPPING.values(), lang_contents))

    return {k: dict(v) for k, v in formatted_results.items()}

def set_caching():
    try:
        status = Updated.query.first()
        status.still_caching ^= 1
        db.session.commit()
        
        return True
    except Exception as e:
        logger.error(f'Encounter error when set still cache: {e}')
        return False

@app.route('/cache', methods=['GET', 'POST'])
def cache_export_files():
    """Cache export files with improved performance and error handling."""
    updated = check_updated()
    if not updated:
        return jsonify({'msg': 'There is no need to cache the download files.'}), 200
    if not lock.acquire(timeout=0.5):
        return jsonify({'msg': 'Resource is locked, try again later.'}), 400
    
    app_ids = []
    
    try:
        if request.method == 'POST':
            logger.error(f'Start recache app excel')
            data = request.get_json()
            app_ids = data['app_ids']
        else:
            logger.error(f'Start cache all app excel')
            cleanup(CACHE_FILE_DIRECTORY)
        
        result = set_caching()
        if not result:
            raise
        
        all_tasks = []

        result = build_query(app_ids).yield_per(500).all()
        formatted_results = format_result(result)
        all_tasks.extend(process_tasks(formatted_results))

        current_time = time.time()
        os.utime(CACHE_FILE_DIRECTORY, (current_time, current_time))        
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [executor.submit(fn, *args) for fn, *args in all_tasks]
            
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Error in thread: {str(e)}", exc_info=True)
                    raise

        result = set_caching()
        if not result:
            raise
        logger.error(f'End of cache excel')
        return jsonify({'msg': 'Cache export complete!'}), 200
    except Exception as e:
        logger.error(f"Critical error in cache_export_files: {str(e)}", exc_info=True)
        return jsonify({'msg': 'Cache export failed', 'error': str(e)}), 500
    finally:
        lock.release()
        cleanup([EXCEL_OUT_DIRECTORY, SOURCE_IN_DIRECTORY, SOURCE_OUT_DIRECTORY])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

from server import app, logger, db
from flask import jsonify
from typing import Any, Optional, Dict, Set, List
from functools import wraps
from threading import Lock, Thread
from queue import Queue
from model.dbModel import AppString_Namespace
import redis, pickle, requests, time

class CacheService:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=app.config['REDIS_HOST'],
            # port=app.config['REDIS_PORT'],
            db=app.config['REDIS_DB'],
            decode_responses=False
        )
        self._cache_queue = Queue()
        self._processing = False
        self._lock = Lock()
        self._worker_thread = None
        self._debounce_timer = None
        self.sleep_timer = app.config['CACHE_SLEEP_TIME']
        self.__start_worker()

    @staticmethod
    def cache_search_results(prefix: str, timeout: int = 1800):
        """Decorator for caching search results
        
        Args:
            prefix (str): Cache key prefix for the search type
            timeout (int): Cache timeout in seconds
            
        Returns:
            Callable: Decorated function with caching
        """
        def decorator(func):
            @wraps(func)
            def wrapper(self, data: Dict, *args, **kwargs):
                # Generate cache key
                query_args = {k: v for k, v in data.items() if v is not None}
                cached_result = self.get_cached_query(prefix, query_args)
                
                if cached_result is not None:
                    return jsonify(cached_result), cached_result['status']
                
                # Execute search if not cached
                result = func(self, data, *args, **kwargs)
                
                # Cache successful results
                if isinstance(result, tuple) and result[1] == 200:
                    self.cache_query_result(
                        prefix,
                        query_args,
                        result[0].json,
                        timeout
                    )
                
                return result
            return wrapper
        return decorator
    
    def invalidate_by_pattern(self, pattern: str) -> None:
        """Delete all cache entries matching the given pattern"""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
        except Exception as e:
            logger.error(f"Failed to invalidate cache pattern {pattern}: {str(e)}")

    def cache_query_result(self, prefix: str, query_args: Dict, result: Any, timeout: int = None) -> None:
        """Cache query results with pickle serialization"""
        try:
            cache_key = f"query_cache:{prefix}:{hash(str(query_args))}"
            self.redis_client.setex(
                name=cache_key,
                time=timeout or self.default_timeout,
                value=pickle.dumps(result)
            )
        except Exception as e:
            logger.error(f"Cache storage failed: {str(e)}")

    def get_cached_query(self, prefix: str, query_args: Dict) -> Optional[Any]:
        """Retrieve cached query results"""
        try:
            cache_key = f"query_cache:{prefix}:{hash(str(query_args))}"
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                return pickle.loads(cached_data)
        except Exception as e:
            logger.error(f"Cache retrieval failed: {str(e)}")
        return None
    
    def query_effected_apps(self, str_id: List) -> Set:
        app_ids = db.session.query(AppString_Namespace.app_id) \
                            .filter(AppString_Namespace.str_id.in_(str_id),
                                    AppString_Namespace.deleted == 0,
                                    ) \
                            .distinct() \
                            .all()
        return {str(app_id[0]) for app_id in app_ids}
    
    def __start_worker(self):
        """Start background worker thread for cache updates"""
        def worker():
            while True:
                try:
                    with self._lock:
                        # Stop processing if queue is empty
                        if self._cache_queue.empty():
                            self._processing = False
                            return
                        
                        # Collect all pending app IDs for batch update
                        apps_to_update = set()
                        while not self._cache_queue.empty():
                            apps_to_update.update(self._cache_queue.get())
                    
                    # Process batch update if there are apps to update
                    if apps_to_update:
                        self.__process_cache_update(apps_to_update)
                    
                    # Sleep to allow batching of requests
                    time.sleep(self.sleep_timer)
                except Exception as e:
                    logger.error(f"Cache worker error: {str(e)}")

        # Start daemon thread
        self._worker_thread = Thread(target=worker, daemon=True)
        self._worker_thread.start()

    def __process_cache_update(self, app_ids: Set):
        """
        Process cache update requests for given app IDs
        
        Args:
            app_ids (Set): Set of application IDs requiring cache updates
        """
        if not app_ids:
            return
            
        url = app.config['CACHE_URL']
        try:
            response = requests.post(
                url,
                json={'app_ids': list(app_ids)},
                headers={'Content-Type': 'application/json'}
            )
            if response.status_code != 200:
                logger.error(f"Cache update failed for apps {app_ids}: Status {response.status_code}")
            elif response.status_code == 200:
                logger.error(f'Cache updated excel success! Apps: {app_ids}, status: {response.status_code}')
        except Exception as e:
            logger.error(f"Cache update error for apps {app_ids}: {str(e)}")

    def signal_cache_service(self, apps: Set) -> None:
        """
        Signal cache service to update for specified apps
        
        Args:
            apps (Set): Set of app IDs that need cache updates
        """
        if not apps:
            return
            
        self._cache_queue.put(apps)
        
        with self._lock:
            if not self._processing:
                self._processing = True
                self.__start_worker()

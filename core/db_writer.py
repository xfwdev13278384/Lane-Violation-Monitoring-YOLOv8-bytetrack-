import mysql .connector
from mysql .connector import pooling
import threading
from queue import Queue
import atexit


_connection_pool = None
_pool_lock = threading .Lock()


def _get_pool():
    global _connection_pool
    if _connection_pool is None:
        with _pool_lock:
            if _connection_pool is None:
                _connection_pool = pooling .MySQLConnectionPool(
                    pool_name="violation_pool",
                    pool_size=3,
                    pool_reset_session=True,
                    host="localhost",
                    user="root",
                    password="Daiphuoc1306@",
                    database="traffic_violation_db"
                )
    return _connection_pool


def get_connection():
    return _get_pool().get_connection()


_insert_queue = Queue()
_insert_thread = None
_stop_thread = False


def _insert_worker():
    global _stop_thread
    while not _stop_thread:
        try:

            data = _insert_queue .get(timeout=1)
            if data is None:
                break
            _do_insert(data)
            _insert_queue .task_done()
        except:
            pass


def _do_insert(data):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn .cursor()
        sql = """
        INSERT INTO violations (
            vehicle_type,
            license_plate,
            violation_type,
            violation_time,
            image_path,
            video_name
        ) VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor .execute(sql, data)
        conn .commit()
    except Exception as e:
        print(f"[DB ERROR] Insert failed: {e }")
    finally:
        if cursor:
            cursor .close()
        if conn:
            conn .close()


def _start_insert_thread():
    global _insert_thread
    if _insert_thread is None or not _insert_thread .is_alive():
        _insert_thread = threading .Thread(target=_insert_worker, daemon=True)
        _insert_thread .start()


def _cleanup():
    global _stop_thread
    _stop_thread = True
    _insert_queue .put(None)
    if _insert_thread and _insert_thread .is_alive():
        _insert_thread .join(timeout=5)


atexit .register(_cleanup)


def insert_violation(
    vehicle_type,
    license_plate,
    violation_type,
    violation_time,
    image_path,
    video_name
):
    _start_insert_thread()

    data = (
        vehicle_type,
        license_plate,
        violation_type,
        violation_time,
        image_path,
        video_name
    )
    _insert_queue .put(data)


def insert_violation_sync(
    vehicle_type,
    license_plate,
    violation_type,
    violation_time,
    image_path,
    video_name
):
    data = (
        vehicle_type,
        license_plate,
        violation_type,
        violation_time,
        image_path,
        video_name
    )
    _do_insert(data)


def insert_violations_batch(violations_list):
    if not violations_list:
        return

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn .cursor()
        sql = """
        INSERT INTO violations (
            vehicle_type,
            license_plate,
            violation_type,
            violation_time,
            image_path,
            video_name
        ) VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor .executemany(sql, violations_list)
        conn .commit()
        print(f"[DB] Batch inserted {len (violations_list )} violations")
    except Exception as e:
        print(f"[DB ERROR] Batch insert failed: {e }")
    finally:
        if cursor:
            cursor .close()
        if conn:
            conn .close()


def flush_pending_inserts():
    _insert_queue .join()

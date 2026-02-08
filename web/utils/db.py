import mysql .connector
from mysql .connector import pooling


connection_pool = pooling .MySQLConnectionPool(
    pool_name="traffic_pool",
    pool_size=10,
    pool_reset_session=True,
    host="localhost",
    user="root",
    password="Daiphuoc1306@",
    database="traffic_violation_db"
)


def get_connection():
    return connection_pool .get_connection()

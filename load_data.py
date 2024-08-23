import sqlite3

class SQLiteManager:
    def __init__(self, db_name):
        self.db_name = db_name

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.conn.close()

    def insert_data(self, table_name, value):
        self.cursor.execute(f'''CREATE TABLE IF NOT EXISTS "{table_name}" (bvid TEXT UNIQUE)''')
        self.cursor.execute(f'INSERT OR IGNORE INTO "{table_name}" (bvid) VALUES (?)', (value,))

    def get_values(self, table_name):
        # 检查表是否存在，表不存在，返回空集合
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if not self.cursor.fetchone():
            return set()
        self.cursor.execute(f'SELECT bvid FROM "{table_name}"')
        return set(row[0] for row in self.cursor.fetchall())

import sqlite3


class DataBase:
    def __init__(self, path: str):
        self.path = path
        self.connect = sqlite3.connect(self.path)
        self.cursor = self.connect.cursor()
        print(f'database {path} connected')

    def add_record(self, table_name: str, *args):
        command = f'INSERT INTO {table_name} VALUES ('

        for i in range(len(args)):
            command += '?,'
        command = command[:-1] + ')'

        self.cursor.executemany(command, [args])
        self.connect.commit()

    def delete_record_by_id(self, table_name: str, record_id: int):
        self.cursor.execute(f"DELETE FROM {table_name} WHERE id = {record_id}")
        self.connect.commit()

    def get_record_by_id(self, table_name: str, record_id: int) -> dict:
        self.cursor.execute(f"SELECT * FROM {table_name} WHERE id LIKE {record_id}")
        column_names = [description[0] for description in self.cursor.description]
        result = self.cursor.fetchall()[0]
        user = {}
        for column_number in range(len(column_names)):
            user[column_names[column_number]] = result[column_number]
        return user

    def get_ids(self, table_name: str) -> list:
        all_ids = []
        self.cursor.execute(f'SELECT id FROM {table_name}')
        for record_id in self.cursor.fetchall():
            all_ids.append(record_id[0])
        return all_ids

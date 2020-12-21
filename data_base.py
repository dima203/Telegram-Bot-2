import sqlite3


class DataBase:
    def __init__(self, path: str):
        self.path = path
        self.connect = sqlite3.connect(self.path)
        self.cursor = self.connect.cursor()
        print('database connected')

    def add_user(self, user_id: int, user_name: str, post: str):
        user = [(user_id, user_name, post)]
        self.cursor.executemany('INSERT INTO users VALUES(?, ?, ?)', user)
        self.connect.commit()

    def delete_user_by_id(self, user_id: int):
        self.cursor.execute(f"DELETE FROM users WHERE user_id = {user_id}")
        self.connect.commit()

    def get_user_by_id(self, user_id: int) -> dict:
        self.cursor.execute(f"SELECT * FROM users WHERE user_id LIKE {user_id}")
        result = self.cursor.fetchall()[0]
        user = {'user_id': result[0], 'user_name': result[1], 'post': result[2]}
        return user

    def get_ids(self):
        all_ids = []
        self.cursor.execute('SELECT user_id FROM users')
        for user_id in self.cursor.fetchall():
            all_ids.append(user_id[0])
        return all_ids

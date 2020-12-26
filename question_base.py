import pickle
import datetime


class QuestionBase:
    def __init__(self, path: str):
        self.path = path
        file = open(path, 'rb')
        self.base = pickle.load(file)
        file.close()

    def get_message(self, message_id: int) -> dict:
        if message_id in self.base:
            return self.base[message_id]

    def add_message(self, text: str, lesson_group: str, lesson_id: int, author_id: int, date: datetime.datetime):
        message_id = self.get_ids()
        if message_id:
            message_id = max(message_id) + 1
        else:
            message_id = 1
        self.base[message_id] = {'text': text, 'author_id': author_id,
                                 'lesson_group': lesson_group, 'lesson_id': lesson_id, 'date': date}
        file = open(self.path, 'wb')
        pickle.dump(self.base, file)
        file.close()

    def delete_message(self, message_id: int):
        if message_id in self.base:
            del self.base[message_id]
            file = open(self.path, 'wb')
            pickle.dump(self.base, file)
            file.close()

    def get_ids(self) -> list:
        ids = []
        for message_id in self.base:
            ids.append(message_id)
        return ids

import pickle
import datetime


class HelpQuestionBase:
    def __init__(self, path: str):
        self.path = path
        file = open(path, 'rb')
        self.base = pickle.load(file)
        file.close()

    def get_question(self, question_id: int) -> dict:
        if question_id in self.base:
            return self.base[question_id]

    def get_question_answers(self, question_id) -> dict:
        if question_id in self.base:
            return self.base[question_id]['answers']

    def get_question_answer(self, question_id: int, answer_id: int) -> dict:
        if question_id in self.base:
            return self.base[question_id]['answers'][answer_id]

    def add_question(self, theme: str, text: str, author_id: int, date: datetime.datetime):
        question_id = self.get_questions_ids()
        if question_id:
            question_id = max(question_id) + 1
        else:
            question_id = 1
        self.base[question_id] = {'theme': theme, 'text': text, 'author_id': author_id, 'date': date, 'answers': {}}
        file = open(self.path, 'wb')
        pickle.dump(self.base, file)
        file.close()

    def add_answer(self, question_id: int, text: str, author_id: int, date: datetime.datetime):
        answer_id = self.get_answers_ids(question_id)
        if answer_id:
            answer_id = max(answer_id) + 1
        else:
            answer_id = 1
        self.base[question_id]['answers'][answer_id] = {'text': text, 'author_id': author_id, 'date': date}
        file = open(self.path, 'wb')
        pickle.dump(self.base, file)
        file.close()

    def delete_question(self, question_id: int):
        if question_id in self.base:
            del self.base[question_id]
            file = open(self.path, 'wb')
            pickle.dump(self.base, file)
            file.close()

    def delete_answer(self, question_id: int, answer_id: int):
        if question_id in self.base:
            if answer_id in self.get_answers_ids(question_id):
                del self.base[question_id]['answers'][answer_id]
                file = open(self.path, 'wb')
                pickle.dump(self.base, file)
                file.close()

    def get_questions_ids(self) -> list:
        ids = []
        for question_id in self.base:
            ids.append(question_id)
        return ids

    def get_answers_ids(self, question_id: int) -> list:
        ids = []
        for answer_id in self.base[question_id]['answers']:
            ids.append(answer_id)
        return ids

import os
import random
from collections import OrderedDict


questions_path = []


def shuffle_dict(dictionary):
    keys = list(dictionary.keys())
    random.shuffle(keys)
    return OrderedDict([(key, dictionary[key]) for key in keys])


def fetch_random_question_path():
    if not questions_path:
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        QUESTIONS_DIR = os.path.join(BASE_DIR, 'quiz-bot', 'quiz-questions')

        for root, dirs, files in os.walk(QUESTIONS_DIR):
            for filename in files:
                questions_path.append(os.path.join(root, filename))
    return questions_path.pop()


quiz_questions = OrderedDict()
shuffle_questions = {}
random_questions = {}


def fetch_random_questions():
    global random_questions
    if random_questions:
        return random_questions.popitem()
    if not quiz_questions:
        question_path = fetch_random_question_path()
        with open(question_path, "r", encoding="KOI8-R") as my_file:
            file_contents = my_file.read()
        quiz_questionss = file_contents.split('\n\n')
        for key, quiz_question in enumerate(quiz_questionss):
            if 'Вопрос' in quiz_question:
                question = quiz_questionss[key]
                try:
                    answer = quiz_questionss[key + 1]
                except IndexError:
                    continue
                quiz_questions[question] = answer
    if quiz_questions:
        global shuffle_questions
        if not shuffle_questions:
            shuffle_questions = shuffle_dict(quiz_questions)
        print(f'quiz_ques_count ->> {len(shuffle_questions)}')
        five_random_questions = shuffle_questions.popitem()
        print(f'quiz_ques ->> {five_random_questions}')
        if '\n   ' in five_random_questions:
            questions = five_random_questions[0].split('\n   ')[1:]
            answers = five_random_questions[1].split('\n   ')[1:]
            for key, random_question in enumerate(questions):
                random_questions[random_question] = answers[key]
        else:
            question = five_random_questions[0]
            answer = five_random_questions[1]
            random_questions[question] = answer
    return random_questions.popitem()

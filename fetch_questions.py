import os
import random
import logging
from collections import OrderedDict


questions_path = []
quiz_questions = OrderedDict()
shuffle_questions = {}
random_questions = {}

logger = logging.getLogger(__name__)


def shuffle_dict(dictionary):
    keys = list(dictionary.keys())
    random.shuffle(keys)
    return OrderedDict([(key, dictionary[key]) for key in keys])


def fetch_random_question_path(questions_dir):
    if not questions_path:
        for root, dirs, files in os.walk(questions_dir):
            for filename in files:
                questions_path.append(os.path.join(root, filename))
        random.shuffle(questions_path)
    return questions_path.pop()


def fetch_random_questions(questions_dir):
    global random_questions
    if random_questions:
        return random_questions.popitem()
    if not quiz_questions:
        question_path = fetch_random_question_path(questions_dir)
        with open(question_path, "r", encoding="KOI8-R") as my_file:
            file_contents = my_file.read()
        questions = file_contents.split('\n\n')
        for key, quiz_question in enumerate(questions):
            if 'Вопрос' in quiz_question:
                question = questions[key]
                try:
                    answer = questions[key + 1]
                except IndexError:
                    continue
                quiz_questions[question] = answer
    if quiz_questions:
        global shuffle_questions
        if not shuffle_questions:
            shuffle_questions = shuffle_dict(quiz_questions)
        logger.info(f'quiz_ques_count ->> {len(shuffle_questions)}')
        five_random_questions = shuffle_questions.popitem()
        logger.info(f'quiz_ques ->> {five_random_questions}')
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

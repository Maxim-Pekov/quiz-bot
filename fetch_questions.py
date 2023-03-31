import os
import random
import logging
from collections import OrderedDict


questions_path = []
quiz_questions = []

logger = logging.getLogger(__name__)


def fetch_random_question_path(questions_dir):
    global questions_path
    if not questions_dir:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        questions_dir = os.path.join(base_dir, 'quiz-bot', 'quiz-questions')
    if not questions_path:
        for root, dirs, files in os.walk(questions_dir):
            for filename in files:
                questions_path.append(os.path.join(root, filename))
        random.shuffle(questions_path)
    return questions_path.pop()


def fetch_random_questions(questions_dir):
    if not quiz_questions:
        question_path = fetch_random_question_path(questions_dir)
        logger.info(f'question_path ->> {question_path}')
        with open(question_path, "r", encoding="KOI8-R") as file:
            file_contents = file.read()
        questions = file_contents.split('\n\n')
        for key, quiz_question in enumerate(questions):
            if 'Вопрос' in quiz_question:
                question = questions[key]
                try:
                    answer = questions[key + 1]
                except IndexError:
                    continue
                quiz_questions.append((question, answer))
                random.shuffle(quiz_questions)
    return quiz_questions.pop()

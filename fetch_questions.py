import os
import random
import re
import logging


logger = logging.getLogger(__name__)


def fetch_random_question_path(questions_dir):
    questions_path = []
    if not questions_dir:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        questions_dir = os.path.join(base_dir, 'quiz-bot', 'quiz-questions')
    for root, dirs, files in os.walk(questions_dir):
        for filename in files:
            questions_path.append(os.path.join(root, filename))
    return questions_path


def fetch_questions(questions_dir):
    questions = []
    questions_path = fetch_random_question_path(questions_dir)
    for question_path in questions_path:
        with open(question_path, "r", encoding="KOI8-R") as file:
            file_contents = file.read()
        questions_info = file_contents.split('\n\n')
        for key, quiz_question in enumerate(questions_info):
            if 'Вопрос ' in quiz_question:
                question = re.sub(r'Вопрос \d+:\s+', '', quiz_question)
                try:
                    answer = re.sub(r'Ответ:\s+', '', questions_info[key + 1])
                except IndexError:
                    continue
                questions.append((question, answer[:-1]))
    return questions


def get_invisible_answer(answer, characters=None) -> str:
    answer_words = answer.split()
    invisible_answer = []
    for word in answer_words:
        word_length = len(word)
        if characters == '&':
            characters = list(set(answer.replace(' ', '')))
            random.shuffle(characters)
            try:
                characters.pop()
            except ValueError:
                pass


        if characters:
            invisible_word = []
            for letter in word:
                if letter in characters:
                    invisible_word.append(letter)
                else:
                    invisible_word.append('_')
            invisible_answer.append(''.join(invisible_word))
        else:
            invisible_answer.append('_' * word_length)
    return ' '.join(invisible_answer)

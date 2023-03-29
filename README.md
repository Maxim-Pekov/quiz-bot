![Typing SVG](https://readme-typing-svg.herokuapp.com?color=%2336BCF7&lines=QUIZ+BOT)


Этот проект бота под Телеграмм и ВК для игры в quiz. 

## Пример общения телеграмм бота.
<img src="static/demo_tg_bot.gif" width="600">

## Пример общения VK бота.
<img src="static/demo_vk_bot.gif" width="600">


## Готовых ботов вы можете протестировать по ссылкам:
* telegram - @@questions_159_bot
* vk_bot - [https://vk.com/](https://vk.com/im?sel=-219590143)

## Проект содержит 4е скрипта:
* `vk_bot.py` - Скрипт проверяет полученные сообщения в чате группы ВК, 
  после написания команды "Старт" присылает набор кнопок и вопрос, вы 
  обратным сообщением присылаете ответ, либо выбираете следующую команду 
  нажатие на одну из кнопок.
* `tg_bot.py` - Скрипт проверяет полученные сообщения в чате TG бота, 
  после написания команды "/start" присылает набор кнопок и вопрос, вы 
  обратным сообщением присылаете ответ, либо выбираете следующую команду 
  нажатие на одну из кнопок.
    <img src="static/tg_buttons.jpg" width="600">
* `fetch_questions.py` - Скрипт рандомно выбирает файл, а в указанном файле 
  вопрос, по переданному пути.
* `logs_handler.py` - Скрипт содержит вспомогательный хендлер для отправки 
  логов с ошибками в telegram.

## Установка

Используйте данную инструкцию по установке этого скрипта

1. Установить

```python
git clone https://github.com/Maxim-Pekov/quiz-bot.git
```

2. Создайте виртуальное окружение:

```python
python -m venv venv
```

3. Активируйте виртуальное окружение:
```python
.\venv\Scripts\activate    # for Windows
```
```python
source ./.venv/bin/activate    # for Linux
```

4. Перейдите в директорию `quiz-bot`
5. Установите зависимости командой ниже:
```python
pip install -r devman_bot/requirements.txt
```

6. Создайте файл с названием `.env`

7. Запишите в данном файле: 
   ваш API токен с сайта ВК, 
   телеграмм токен вашего бота, 
   TG_CHAT_ID - это id чата телеграмма куда присылать ошибки уровня Error,
   QUESTIONS_DIR=путь до папки с файлами где написаны вопросы для Квиза,
   REDIS_PASSWORD=AEA7B5sfkJ0MzcuQiDdDf0IVF0y4TZ5H
   REDIS_HOST=redis-18142.c12.us-east-1-4.ec2.cloud.redislabs.com
   REDIS_PORT=18142
   
```python
VK_API_TOKEN='vk1.a.bNnlnbblk47y5l4........'
TG_API_BOT=6276525627:AAGHhsfhssofGiOJMspZ425242QCnx54Ok
TG_CHAT_ID='7477755261'
REDIS_PASSWORD=AEA7B5sfkJ0MzcuQiDdDf464gsh48hs6
REDIS_HOST=redis-18156.c12.us-east-1-5.ec2.cloud.redislabs.com
REDIS_PORT=18882
QUESTIONS_DIR=quiz-questions
```

## About me

[<img align="left" alt="maxim-pekov | LinkedIn" width="30px" src="https://img.icons8.com/color/48/000000/linkedin-circled--v3.png" />https://www.linkedin.com/in/maxim-pekov/](https://www.linkedin.com/in/maxim-pekov/)
</br>

[<img align="left" alt="maxim-pekov" width="28px" src="https://upload.wikimedia.org/wikipedia/commons/5/5c/Telegram_Messenger.png" />https://t.me/MaxPekov/](https://t.me/MaxPekov/)
</br>

[//]: # (Карточка профиля: )
![](https://github-profile-summary-cards.vercel.app/api/cards/profile-details?username=Maxim-Pekov&theme=solarized_dark)

[//]: # (Статистика языков в коммитах:)

[//]: # (Статистика языков в репозиториях:)
![](https://github-profile-summary-cards.vercel.app/api/cards/most-commit-language?username=Maxim-Pekov&theme=solarized_dark)
![](https://github-profile-summary-cards.vercel.app/api/cards/repos-per-language?username=Maxim-Pekov&theme=solarized_dark)


[//]: # (Статистика профиля:)

[//]: # (Данные по коммитам за сутки:)
![](https://github-profile-summary-cards.vercel.app/api/cards/stats?username=Maxim-Pekov&theme=solarized_dark)
![](https://github-profile-summary-cards.vercel.app/api/cards/productive-time?username=Maxim-Pekov&theme=solarized_dark)

[//]: # ([![trophy]&#40;https://github-profile-trophy.vercel.app/?username=Maxim-Pekov&#41;]&#40;https://github.com/ryo-ma/github-profile-trophy&#41;)


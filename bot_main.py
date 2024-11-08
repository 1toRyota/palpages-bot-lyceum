import telebot
from telebot import types
import datetime
import database as db
import gigachat_request as gr
import summarizer
import re


def is_valid_nickname(nickname):
    # Проверка корректности никнейма формата @nickname
    pattern = r"^@[A-Za-z0-9_]+$"
    return bool(re.match(pattern, nickname))


def check_format(string):
    # Проверка корректности формата строки "Автор - Название"
    pattern = r'^[\wа-яА-ЯёЁ0-9\s!.,:;"\'()]*[-—–]+[\wа-яА-ЯёЁ0-9\s!.,:;"\'()]*$'

    # Возвращает True, если строка соответствует шаблону
    if re.match(pattern, string):
        return True
    else:
        return False


token = "7803160422:AAFqwn5hbF0f7FYk0mXc6AOnfPA1Ze81NaQ"
bot = telebot.TeleBot(token)


@bot.message_handler(commands=["start"])
def start(message):
    # Если пользователя нет в БД, регистрируем его
    if not db.user_exists(message.chat.id):
        db.register_user(message.chat.id, message.from_user.username, message.from_user.first_name)
    elif db.user_exists(message.chat.id):
        # Сбрасывает настройки по умолчанию для зарегистрированного пользователя
        db.reset_user_defaults(message.chat.id)

    # Создает кнопки для выбора действий
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Начать работу с текстом")
    btn2 = types.KeyboardButton("Профиль")
    btn3 = types.KeyboardButton("Друзья")
    markup.add(btn1, btn2, btn3)

    # Приветственное сообщение
    if message.from_user.first_name is None:
        bot.send_message(message.chat.id, text=f"Привет! Это PalPages!\n\nЕсли вы застряли в каком-то месте этого "
                                               f"рабочего пространства, отправьте /start", reply_markup=markup)
    else:
        bot.send_message(message.chat.id,
                         text=f"Привет, {message.from_user.first_name}! Это PalPages!", reply_markup=markup)
    # Логируем элемент message полностью при вводе команды /start
    print(message)


@bot.message_handler(content_types=["text"])
def func(message):
    # Логируем сообщения пользователя с отметкой времени
    print(
        f"{datetime.datetime.now()}: id:{message.chat.id}, {message.from_user.username} {message.from_user.first_name} "
        f"{message.from_user.last_name} - {message.text}"
    )

    # Обработка выбора "Начать работу с текстом"
    if message.text == "Начать работу с текстом" and not db.get_is_working_with_book(message.chat.id):
        booklist = db.get_books(message.chat.id)
        if len(booklist) == 0:
            # Сообщает, если у пользователя нет добавленных произведений
            bot.send_message(message.chat.id, text="У вас нет добавленных произведений.\nПожалуйста, отправьте "
                                                   "название нового произведения в формате Автор - Название",
                             reply_markup=types.ReplyKeyboardRemove())
            db.set_is_plus(message.chat.id, True)

        else:
            # Показывает список произведений, если они есть
            formatted_books = "\n".join(f"{i + 1}. {book}" for i, book in enumerate(booklist))
            bot.send_message(message.chat.id, text=f"Вот список ваших произведений:\n{formatted_books}\nОтправьте "
                                                   f"номер произведения, с которым хотите начать работу, "
                                                   f"или отправьте +, чтобы добавить новое произведение",
                             reply_markup=types.ReplyKeyboardRemove())
            db.set_is_choosing_book_for_work(message.chat.id, True)

    # Начало работы с выбранным произведением
    elif db.get_is_choosing_book_for_work(message.chat.id) and message.text.isdigit():
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Отправить фрагмент для сжатия сообщением")
        btn2 = types.KeyboardButton("Отправить .txt файл для сжатия")
        btn3 = types.KeyboardButton("Задать вопрос")
        btn4 = types.KeyboardButton("Создать тест")
        btn5 = types.KeyboardButton("Завершить работу с произведением")
        markup.add(btn1, btn2, btn3, btn4, btn5)

        db.set_is_choosing_book_for_work(message.chat.id, False)
        db.set_is_working_with_book(message.chat.id, True)
        db.set_working_with_book(message.chat.id, int(message.text) - 1)
        booklist = db.get_books(message.chat.id)
        try:
            # Уведомляет пользователя о начале работы с выбранным произведением
            book_index = db.get_working_with_book(message.chat.id)
            bot.send_message(message.chat.id, text=f"Вы начали работу с произведением {booklist[book_index - 1]}"
                                                   f"\n\nВнимание! "
                                                   f"Если Вы хотите сжать фрагмент длиной более 4096 символов, текст "
                                                   f"следует отправить .txt файлом, выбрав соответствующий вариант",
                             reply_markup=markup)
        except IndexError:
            bot.send_message(message.chat.id, text="Некорректный ввод", reply_markup=markup)

    # Добавление нового произведения
    elif message.text == "+" and not db.get_is_working_with_book(message.chat.id):
        db.set_is_plus(message.chat.id, True)
        bot.send_message(message.chat.id, text="Пожалуйста, отправьте название нового произведения в формате Автор - "
                                               "Название", reply_markup=types.ReplyKeyboardRemove())

    # Проверяет корректность формата введенного названия и добавляет книгу
    elif db.get_is_plus(message.chat.id) and check_format(message.text):
        db.add_books(message.chat.id, [message.text])
        db.set_is_working_with_book(message.chat.id, True)
        booklist_len = len(db.get_books(message.chat.id))
        db.set_working_with_book(message.chat.id, booklist_len - 1)

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Отправить фрагмент для сжатия сообщением")
        btn2 = types.KeyboardButton("Отправить .txt файл для сжатия")
        btn3 = types.KeyboardButton("Задать вопрос")
        btn4 = types.KeyboardButton("Создать тест")
        btn5 = types.KeyboardButton("Завершить работу с произведением")
        markup.add(btn1, btn2, btn3, btn4, btn5)

        # Уведомляет пользователя об успешном добавлении произведения
        bot.send_message(message.chat.id, text=f"Вы добавили {message.text} и начали работу с этим произведением\n\n"
                                               f"Внимание! Если Вы хотите сжать фрагмент длиной более 4096 символов, "
                                               f"текст следует отправить .txt файлом, выбрав соответствующий вариант",
                         reply_markup=markup)
        db.set_is_plus(message.chat.id, False)

    # Завершение работы с произведением
    elif message.text == "Завершить работу с произведением" and db.get_is_working_with_book(message.chat.id):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Начать работу с текстом")
        btn2 = types.KeyboardButton("Профиль")
        btn3 = types.KeyboardButton("Друзья")
        markup.add(btn1, btn2, btn3)

        db.set_is_working_with_book(message.chat.id, False)
        bot.send_message(message.chat.id, text="Вы завершили работу с произведением", reply_markup=markup)

    # Начало сеанса с вопросом по произведению
    elif message.text == "Задать вопрос" and db.get_is_working_with_book(message.chat.id):
        db.set_is_asking(message.chat.id, True)
        booklist = db.get_books(message.chat.id)
        book_index = db.get_working_with_book(message.chat.id)

        bot.send_message(message.chat.id,
                         text=f"Вы работаете с произведением {booklist[book_index - 1]}.\nОтправьте ваш "
                              f"вопрос по этому произведению",
                         reply_markup=types.ReplyKeyboardRemove())

    # Обработка вопроса по произведению
    elif db.get_is_asking(message.chat.id):
        db.set_is_waiting(message.chat.id, True)
        booklist = db.get_books(message.chat.id)
        book_index = db.get_working_with_book(message.chat.id)

        bot.send_message(message.chat.id, text="Подождите, пожалуйста, Ваш вопрос обрабатывается",
                         reply_markup=types.ReplyKeyboardRemove())

        # Получение ответа на вопрос с использованием GigaChat
        answer = gr.question(message.text, booklist[book_index - 1])

        # Кнопки для дальнейших действий
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Отправить фрагмент для сжатия сообщением")
        btn2 = types.KeyboardButton("Отправить .txt файл для сжатия")
        btn3 = types.KeyboardButton("Задать вопрос")
        btn4 = types.KeyboardButton("Создать тест")
        btn5 = types.KeyboardButton("Завершить работу с произведением")
        markup.add(btn1, btn2, btn3, btn4, btn5)

        # Отправка ответа на вопрос пользователя и отображение кнопок для дальнейших действий
        bot.send_message(message.chat.id, text=answer, reply_markup=markup)
        db.set_is_waiting(message.chat.id, False)
        db.set_is_asking(message.chat.id, False)

    # Создание теста по произведению
    elif message.text == "Создать тест" and db.get_is_working_with_book(message.chat.id):
        db.set_is_waiting(message.chat.id, True)

        booklist = db.get_books(message.chat.id)
        book_index = db.get_working_with_book(message.chat.id) - 1

        # Уведомление пользователя о начале обработки запроса на создание теста
        bot.send_message(message.chat.id, text="Пожалуйста, подождите, Ваш запрос обрабатывается",
                         reply_markup=types.ReplyKeyboardRemove())

        # Генерация теста на основе выбранного произведения
        test = gr.test(booklist[book_index])

        # Создание кнопок для дальнейших действий после получения теста
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Отправить фрагмент для сжатия сообщением")
        btn2 = types.KeyboardButton("Отправить .txt файл для сжатия")
        btn3 = types.KeyboardButton("Задать вопрос")
        btn4 = types.KeyboardButton("Создать тест")
        btn5 = types.KeyboardButton("Завершить работу с произведением")
        markup.add(btn1, btn2, btn3, btn4, btn5)

        # Отправка теста пользователю
        bot.send_message(message.chat.id, text=test, reply_markup=markup)
        db.set_is_waiting(message.chat.id, False)

    # Обработка отправки текста для сжатия через сообщение
    elif message.text == "Отправить фрагмент для сжатия сообщением" and db.get_is_working_with_book(message.chat.id):
        db.set_is_text_from_message(message.chat.id, True)
        db.set_is_choosing_summarizing_level(message.chat.id, True)

        # Кнопки для выбора уровня сжатия текста
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Стандартный")
        btn2 = types.KeyboardButton("Сильный")
        markup.add(btn1, btn2)

        bot.send_message(message.chat.id, text="Выберите уровень сжатия", reply_markup=markup)

    # Обработка отправки текста для сжатия через .txt файл
    elif message.text == "Отправить .txt файл для сжатия" and db.get_is_working_with_book(message.chat.id):
        db.set_is_text_from_file(message.chat.id, True)
        db.set_is_choosing_summarizing_level(message.chat.id, True)

        # Запрос уровня сжатия текста
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Стандартный")
        btn2 = types.KeyboardButton("Сильный")
        markup.add(btn1, btn2)

        bot.send_message(message.chat.id, text="Выберите уровень сжатия", reply_markup=markup)

    # Обработка выбора стандартного уровня сжатия
    elif db.get_is_choosing_summarizing_level(message.chat.id) and message.text == "Стандартный":
        db.update_summarizing_level(message.chat.id, 1)
        db.set_is_choosing_summarizing_level(message.chat.id, False)

        # Определение типа текста (файл или сообщение) для ответного сообщения
        if db.get_is_text_from_file(message.chat.id):
            message_type = "файл"
        elif db.get_is_text_from_message(message.chat.id):
            message_type = "текст"

        bot.send_message(message.chat.id, text=f"Отправьте {message_type} для сжатия",
                         reply_markup=types.ReplyKeyboardRemove())

    # Обработка выбора сильного уровня сжатия
    elif db.get_is_choosing_summarizing_level(message.chat.id) and message.text == "Сильный":
        db.update_summarizing_level(message.chat.id, 2)
        db.set_is_choosing_summarizing_level(message.chat.id, False)

        # Определение типа текста (файл или сообщение) для дальнейшей обработки
        if db.get_is_text_from_file(message.chat.id):
            message_type = "файл"
        elif db.get_is_text_from_message(message.chat.id):
            message_type = "текст"

        bot.send_message(message.chat.id, text=f"Отправьте {message_type} для сжатия",
                         reply_markup=types.ReplyKeyboardRemove())

    # Обработка текста, отправленного для сжатия через сообщение
    elif db.get_is_text_from_message(message.chat.id) and not db.get_is_choosing_summarizing_level(message.chat.id):
        bot.send_message(message.chat.id, text="Подождите, пожалуйста, Ваш текст суммаризируется\nПроцесс может "
                                               "занять до 5 минут", reply_markup=types.ReplyKeyboardRemove())

        db.set_is_waiting(message.chat.id, True)

        # Выполнение сжатия текста в зависимости от выбранного уровня
        if db.get_summarizing_level(message.chat.id) == 1:
            reply = summarizer.generate_std(message.text)
        elif db.get_summarizing_level(message.chat.id) == 2:
            reply = summarizer.generate_short(message.text)

        # Обновление текста в базе данных
        db.update_text(message.chat.id, message.text)

        # Подготовка кнопок для дальнейших действий после получения сжатого текста
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Отправить фрагмент для сжатия сообщением")
        btn2 = types.KeyboardButton("Отправить .txt файл для сжатия")
        btn3 = types.KeyboardButton("Задать вопрос")
        btn4 = types.KeyboardButton("Создать тест")
        btn5 = types.KeyboardButton("Завершить работу с произведением")
        markup.add(btn1, btn2, btn3, btn4, btn5)

        # Отправка сжатого текста пользователю
        bot.send_message(message.chat.id, text=reply, reply_markup=markup)
        db.set_is_text_from_message(message.chat.id, False)
        db.set_is_waiting(message.chat.id, False)

    # Переход к профилю пользователя
    elif message.text == "Профиль" and not db.get_is_working_with_book(message.chat.id):
        db.set_is_in_profile(message.chat.id, True)

        # Создание кнопок для управления профилем
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Добавить произведение")
        btn2 = types.KeyboardButton("Удалить произведение")
        btn3 = types.KeyboardButton("Назад")
        markup.add(btn1, btn2, btn3)

        booklist = db.get_books(message.chat.id)
        if len(booklist) == 0:
            # Уведомление о том, что у пользователя нет добавленных книг
            bot.send_message(message.chat.id, text=f"Ваш профиль:\n{message.from_user.first_name}, "
                                                   f"@{message.from_user.username}\n\n"
                                                   f"Вы пока не добавили ни одной книги",
                             reply_markup=markup)
        else:
            # Отображение списка добавленных книг пользователя
            formatted_books = "\n".join(f"{i + 1}. {book}" for i, book in enumerate(booklist))
            bot.send_message(message.chat.id, text=f"Ваш профиль:\n{message.from_user.first_name}, "
                                                   f"@{message.from_user.username}\n\nВаши книги:\n{formatted_books}",
                             reply_markup=markup)

    # Начало процесса добавления нового произведения
    elif message.text == "Добавить произведение" and not db.get_is_working_with_book(
            message.chat.id) and db.get_is_in_profile(message.chat.id):
        db.set_is_adding_book(message.chat.id, True)
        bot.send_message(message.chat.id, text="Пожалуйста, отправьте название нового произведения в формате Автор - "
                                               "Название", reply_markup=types.ReplyKeyboardRemove())

    # Проверка формата введенного названия и добавление книги в профиль
    elif db.get_is_adding_book(message.chat.id) and check_format(message.text):
        db.add_books(message.chat.id, [message.text])

        # Создание кнопок для управления профилем после добавления книги
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Добавить произведение")
        btn2 = types.KeyboardButton("Удалить произведение")
        btn3 = types.KeyboardButton("Назад")
        markup.add(btn1, btn2, btn3)

        # Уведомление о том, что книга успешно добавлена
        bot.send_message(message.chat.id, text=f"Вы добавили {message.text}", reply_markup=markup)

        db.set_is_adding_book(message.chat.id, False)

    # Начало процесса удаления произведения
    elif message.text == "Удалить произведение" and not db.get_is_working_with_book(
            message.chat.id) and db.get_is_in_profile(message.chat.id):
        db.set_is_choosing_book_for_deleting(message.chat.id, True)

        booklist = db.get_books(message.chat.id)
        formatted_books = "\n".join(f"{i + 1}. {book}" for i, book in enumerate(booklist))

        # Отображение списка книг для удаления
        bot.send_message(message.chat.id, text=f"Вот список ваших произведений:\n{formatted_books}\n\nОтправьте "
                                               f"номер произведения, которое хотите удалить",
                         reply_markup=types.ReplyKeyboardRemove())

    # Обработка выбора произведения для удаления
    elif db.get_is_choosing_book_for_deleting(message.chat.id) and message.text.isdigit():
        booklist = db.get_books(message.chat.id)

        # Создание кнопок для управления профилем после удаления книги
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Добавить произведение")
        btn2 = types.KeyboardButton("Удалить произведение")
        btn3 = types.KeyboardButton("Назад")
        markup.add(btn1, btn2, btn3)

        try:
            # Удаление выбранной книги из профиля
            book_to_remove = booklist[int(message.text) - 1]
            db.remove_books(message.chat.id, [book_to_remove])
            bot.send_message(message.chat.id, text=f"Вы удалили {book_to_remove}", reply_markup=markup)
            db.set_is_choosing_book_for_deleting(message.chat.id, False)

        except IndexError:
            # Уведомление об ошибочном вводе номера книги
            bot.send_message(message.chat.id, text="Некорректный ввод", reply_markup=types.ReplyKeyboardRemove())

    # Обработка команды "Назад" для выхода из профиля или списка друзей
    elif ((db.get_is_in_profile(message.chat.id) or db.get_is_in_friends(message.chat.id)) and not
            db.get_is_working_with_book(message.chat.id) and message.text == "Назад"):
        db.set_is_in_profile(message.chat.id, False)
        db.set_is_in_friends(message.chat.id, False)

        # Показ кнопок для начала новой работы
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Начать работу с текстом")
        btn2 = types.KeyboardButton("Профиль")
        btn3 = types.KeyboardButton("Друзья")
        markup.add(btn1, btn2, btn3)

        bot.send_message(message.chat.id, text="Чем займемся?", reply_markup=markup)

    # Проверяем, выбрана ли пользователем функция "Друзья" и не работает ли он с книгой в данный момент
    elif message.text == "Друзья" and not db.get_is_working_with_book(message.chat.id) and not db.get_is_in_friends(
            message.chat.id):
        # Устанавливаем статус работы с друзьями
        db.set_is_in_friends(message.chat.id, True)

        # Получаем список друзей пользователя
        friendlist = db.get_friends(message.chat.id)

        # Создаем клавиатуру для взаимодействия с друзьями
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Добавить друга")
        btn2 = types.KeyboardButton("Удалить друга")
        btn3 = types.KeyboardButton("Посмотреть книги друга")
        btn4 = types.KeyboardButton("Назад")
        markup.add(btn1, btn2, btn3, btn4)

        # Если друзей нет, отправляем сообщение с соответствующей информацией
        if len(friendlist) == 0:
            bot.send_message(message.chat.id, text="Вы еще не добавили ни одного друга", reply_markup=markup)
        else:
            # Форматируем и отправляем список друзей
            formatted_friends = "\n".join(f"{i + 1}. {book}" for i, book in enumerate(friendlist))
            bot.send_message(message.chat.id, text=f"Список Ваших друзей:\n\n{formatted_friends}", reply_markup=markup)

    # Проверяем, выбрана ли функция добавления друга
    elif message.text == "Добавить друга" and db.get_is_in_friends(message.chat.id):
        # Устанавливаем статус добавления друга
        db.set_is_adding_friend(message.chat.id, True)

        # Создаем клавиатуру для взаимодействия с друзьями
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Добавить друга")
        btn2 = types.KeyboardButton("Удалить друга")
        btn3 = types.KeyboardButton("Посмотреть книги друга")
        btn4 = types.KeyboardButton("Назад")
        markup.add(btn1, btn2, btn3, btn4)

        # Просим пользователя отправить никнейм друга
        bot.send_message(message.chat.id, text="Отправьте никнейм друга, которого хотите добавить, в формате @nickname",
                         reply_markup=types.ReplyKeyboardRemove())

    # Проверяем, введен ли никнейм для добавления друга
    elif db.get_is_in_friends(message.chat.id) and db.get_is_adding_friend(message.chat.id) and is_valid_nickname(
            message.text):
        # Сбрасываем статус добавления друга
        db.set_is_adding_friend(message.chat.id, False)

        # Создаем клавиатуру для взаимодействия с друзьями
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Добавить друга")
        btn2 = types.KeyboardButton("Удалить друга")
        btn3 = types.KeyboardButton("Посмотреть книги друга")
        btn4 = types.KeyboardButton("Назад")
        markup.add(btn1, btn2, btn3, btn4)

        # Проверяем, существует ли пользователь с указанным никнеймом
        if db.user_exists(db.get_friend_chat_id(message.text[1:])):
            # Добавляем друга и отправляем подтверждение
            bot.send_message(message.chat.id, text=f"Вы добавили {message.text} в список своих друзей",
                             reply_markup=markup)
            db.add_friends(message.chat.id, [message.text])

        else:
            # Если друг еще не зарегистрирован, отправляем сообщение
            bot.send_message(message.chat.id, text="Кажется, Ваш друг еще не начал пользоваться PalPages :(",
                             reply_markup=markup)

    # Проверяем, выбрана ли функция удаления друга
    elif db.get_is_in_friends(message.chat.id) and message.text == "Удалить друга":
        # Устанавливаем статус удаления друга
        db.set_is_deleting_friend(message.chat.id, True)
        # Получаем список друзей
        friedlist = db.get_friends(message.chat.id)

        # Создаем клавиатуру для взаимодействия с друзьями
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Добавить друга")
        btn2 = types.KeyboardButton("Удалить друга")
        btn3 = types.KeyboardButton("Посмотреть книги друга")
        btn4 = types.KeyboardButton("Назад")
        markup.add(btn1, btn2, btn3, btn4)

        # Если друзей нет, уведомляем пользователя
        if len(friedlist) == 0:
            bot.send_message(message.chat.id, text="Вы еще не добавили ни одного друга", reply_markup=markup)

        else:

            # Форматируем и отправляем список друзей с просьбой выбрать друга для удаления

            formatted_friends = "\n".join(f"{i + 1}. {book}" for i, book in enumerate(friedlist))

            bot.send_message(message.chat.id,
                             text=f"Список Ваших друзей:\n\n{formatted_friends}\n\nОтправьте номер друга, которого "
                                  f"хотите удалить",
                             reply_markup=types.ReplyKeyboardRemove())

        # Проверяем, введен ли номер друга для удаления

    elif db.get_is_deleting_friend(message.chat.id) and message.text.isdigit():
        # Сбрасываем статус удаления друга
        db.set_is_deleting_friend(message.chat.id, False)

        # Создаем клавиатуру для взаимодействия с друзьями
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Добавить друга")
        btn2 = types.KeyboardButton("Удалить друга")
        btn3 = types.KeyboardButton("Посмотреть книги друга")
        btn4 = types.KeyboardButton("Назад")
        markup.add(btn1, btn2, btn3, btn4)

        # Получаем список друзей и пытаемся удалить друга по номеру
        friendlist = db.get_friends(message.chat.id)

        try:
            friend_to_remove = friendlist[int(message.text) - 1]
            db.remove_friends(message.chat.id, [friend_to_remove])
            bot.send_message(message.chat.id, text=f"Вы удалили {friend_to_remove} из списка друзей",
                             reply_markup=markup)

        except IndexError:
            bot.send_message(message.chat.id, text="Некорректный ввод", reply_markup=types.ReplyKeyboardRemove())

    # Проверяем, выбрана ли функция просмотра книг друга
    elif db.get_is_in_friends(message.chat.id) and message.text == "Посмотреть книги друга":

        # Получаем список друзей
        friedlist = db.get_friends(message.chat.id)

        # Создаем клавиатуру для взаимодействия с друзьями
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Добавить друга")
        btn2 = types.KeyboardButton("Удалить друга")
        btn3 = types.KeyboardButton("Посмотреть книги друга")
        btn4 = types.KeyboardButton("Назад")
        markup.add(btn1, btn2, btn3, btn4)

        # Если друзей нет, уведомляем пользователя

        if len(friedlist) == 0:
            bot.send_message(message.chat.id, text="Вы еще не добавили ни одного друга", reply_markup=markup)

        else:
            # Форматируем и отправляем список друзей с просьбой выбрать для просмотра книг
            formatted_friends = "\n".join(f"{i + 1}. {book}" for i, book in enumerate(friedlist))

            bot.send_message(message.chat.id,
                             text=f"Список Ваших друзей:\n\n{formatted_friends}\n\nОтправьте @nickname друга, книги "
                                  f"которого хотите посмотреть",
                             reply_markup=types.ReplyKeyboardRemove())

            db.set_is_seeing_friend_books(message.chat.id, True)

    # Проверяем, введен ли никнейм для просмотра книг друга
    elif db.get_is_in_friends(message.chat.id) and db.get_is_seeing_friend_books(message.chat.id) and is_valid_nickname(
            message.text):

        # Сбрасываем статус просмотра книг друга
        db.set_is_seeing_friend_books(message.chat.id, False)

        # Создаем клавиатуру для взаимодействия с друзьями
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Добавить друга")
        btn2 = types.KeyboardButton("Удалить друга")
        btn3 = types.KeyboardButton("Посмотреть книги друга")
        btn4 = types.KeyboardButton("Назад")
        markup.add(btn1, btn2, btn3, btn4)

        try:
            # Получаем ID друга и его книги
            friend_id = db.get_friend_chat_id(message.text[1:])
            friend_booklist = db.get_books(friend_id)

            # Проверяем, есть ли книги у друга
            if len(friend_booklist) == 0:
                bot.send_message(message.chat.id, text=f"{message.text} еще не добавил(а) ни одной книги",
                                 reply_markup=markup)

            else:
                formatted_books = "\n".join(f"{i + 1}. {book}" for i, book in enumerate(friend_booklist))
                bot.send_message(message.chat.id, text=f"Книги {message.text}:\n\n{formatted_books}",
                                 reply_markup=markup)

        except IndexError:
            bot.send_message(message.chat.id, text="Некорректный ввод", reply_markup=types.ReplyKeyboardRemove())

    # Если ожидается завершение процесса, просим подождать
    elif db.get_is_waiting(message.chat.id):
        bot.send_message(message.chat.id, text="Пожалуйста, дождитесь завершения процесса")

    # Обработка некорректного ввода
    else:
        bot.send_message(message.chat.id, text="Некорректный ввод")


# Обработка файлов для суммаризации текста
@bot.message_handler(content_types=["document"])
def file_summarizing(message):
    if db.get_is_text_from_file(message.chat.id) and db.get_is_working_with_book(message.chat.id):
        db.set_is_waiting(message.chat.id, True)
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Сохраняем файл
        src = "text.txt"
        with open(src, "wb+") as txt_file:
            txt_file.write(downloaded_file)

        with open(src, "r", encoding="utf-8") as text_file:
            message_text = text_file.read()

        db.update_text(message.chat.id, message_text)

        # Уведомляем пользователя о процессе суммаризации
        bot.send_message(message.chat.id,
                         text="Подождите, пожалуйста, Ваш текст суммаризируется\nПроцесс может занять до 5 минут",
                         reply_markup=types.ReplyKeyboardRemove())

        # Клавиатура для взаимодействия с функцией суммаризации
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Отправить фрагмент для сжатия сообщением")
        btn2 = types.KeyboardButton("Отправить .txt файл для сжатия")
        btn3 = types.KeyboardButton("Задать вопрос")
        btn4 = types.KeyboardButton("Создать тест")
        btn5 = types.KeyboardButton("Завершить работу с произведением")
        markup.add(btn1, btn2, btn3, btn4, btn5)

        # Запускаем суммаризацию в зависимости от уровня
        if db.get_summarizing_level(message.chat.id) == 1:
            reply_text = summarizer.generate_std(message_text)
        elif db.get_summarizing_level(message.chat.id) == 2:
            reply_text = summarizer.generate_short(message_text)

        # Очищаем флаг и отправляем суммаризованный текст
        db.set_is_text_from_file(message.chat.id, False)
        bot.send_message(message.chat.id, text=reply_text, reply_markup=markup)
        db.set_is_waiting(message.chat.id, False)
        db.set_is_text_from_file(message.chat.id, False)
    else:
        bot.send_message(message.chat.id, text="Некорректный ввод")


# Запуск бота
try:
    bot.polling(none_stop=True)
except telebot.apihelper.ApiTelegramException:
    # Перезапуск бота в случае ошибки 502
    bot.polling(none_stop=True)
except Exception as error:
    # Запись логов в случае ошибки
    print(error)
finally:
    # Закрытие подключения к базе данных при завершении работы
    db.close_connection()

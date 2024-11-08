import telebot
from telebot import types
import datetime
import summarizer

token = "<token>"
bot = telebot.TeleBot(token)

# Эта версия бота не использует БД, поэтому используются следующие переменные для определения выбора пользователя
isTextFromMessage = False
isTextFromFile = False
isChoosingSummarizingLevel = False
summarizing_level = 1


# Обработка старта пользователя
@bot.message_handler(commands=["start"])
def start(message):
    # Кнопки для дальнейших действий
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Отправить текст для сжатия сообщением")
    btn2 = types.KeyboardButton("Отправить .txt файл для сжатия")
    markup.add(btn1, btn2)

    # Отправляем приветствие
    bot.send_message(message.chat.id,
                     text="Привет, {0.first_name}! Это PalPages!\n\nВыберите способ отправки текста\nВнимание! "
                          "Если в вашем тексте более 4096 символов, текст нужно отправить .txt файлом, "
                          "выбрав соответствующщий вариант".format(message.from_user), reply_markup=markup)

    # Логируем элемент message полностью при вводе команды /start
    print(message)


@bot.message_handler(content_types=["text"])
def func(message):
    global isTextFromMessage, isTextFromFile, isChoosingSummarizingLevel, summarizing_level
    # Логируем сообщения пользователя с отметкой времени
    print(
        f"{datetime.datetime.now()}: id:{message.chat.id}, {message.from_user.username} {message.from_user.first_name} "
        f"{message.from_user.last_name} - {message.text}"
    )

    # Обработка отправки текста для сжатия через сообщение
    if message.text == "Отправить текст для сжатия сообщением":
        isTextFromMessage = True
        isChoosingSummarizingLevel = True

        # Кнопки для выбора уровня сжатия текста
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn3 = types.KeyboardButton("Стандартный")
        btn4 = types.KeyboardButton("Сильный")
        markup.add(btn3, btn4)

        bot.send_message(message.chat.id, text="Выберите уровень сжатия", reply_markup=markup)

    # Обработка отправки текста для сжатия через .txt файл
    elif message.text == "Отправить .txt файл для сжатия":
        isTextFromFile = True
        isChoosingSummarizingLevel = True

        # Кнопки для выбора уровня сжатия текста
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn3 = types.KeyboardButton("Стандартный")
        btn4 = types.KeyboardButton("Сильный")
        markup.add(btn3, btn4)

        bot.send_message(message.chat.id, text="Выберите уровень сжатия", reply_markup=markup)

    # Обработка выбора стандартного уровня сжатия
    elif isChoosingSummarizingLevel and message.text == "Стандартный":
        summarizing_level = 1
        isChoosingSummarizingLevel = False

        # Определение типа текста (файл или сообщение) для ответного сообщения
        if isTextFromFile:
            type = "файл"
        elif isTextFromMessage:
            type = "текст"

        # Кнопки для дальнейших действий
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Отправить текст для сжатия сообщением")
        btn2 = types.KeyboardButton("Отправить .txt файл для сжатия")
        markup.add(btn1, btn2)

        bot.send_message(message.chat.id, text=f"Отправьте {type} для сжатия", reply_markup=markup)

    # Обработка выбора сильного уровня сжатия
    elif isChoosingSummarizingLevel and message.text == "Сильный":
        summarizing_level = 2
        isChoosingSummarizingLevel = False

        # Определение типа текста (файл или сообщение) для ответного сообщения
        if isTextFromFile:
            type = "файл"
        elif isTextFromMessage:
            type = "текст"

        # Кнопки для дальнейших действий
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Отправить текст для сжатия сообщением")
        btn2 = types.KeyboardButton("Отправить .txt файл для сжатия")
        markup.add(btn1, btn2)

        bot.send_message(message.chat.id, text=f"Отправьте {type} для сжатия", reply_markup=markup)

    # Обработка текста, отправленного для сжатия через сообщение
    elif isTextFromMessage and (message.text != "Сильный" or message.text != "Стандартный"):
        bot.send_message(message.chat.id, text="Подождите, пожалуйста, Ваш текст суммаризируется\nПроцесс может "
                                               "занять до 5 минут", reply_markup=types.ReplyKeyboardRemove())

        # Выполнение сжатия текста в зависимости от выбранного уровня
        if summarizing_level == 1:
            reply = summarizer.generate_std(message.text)
        elif summarizing_level == 2:
            reply = summarizer.generate_short(message.text)

        # Кнопки для дальнейших действий
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Отправить текст для сжатия сообщением")
        btn2 = types.KeyboardButton("Отправить .txt файл для сжатия")
        markup.add(btn1, btn2)

        bot.send_message(message.chat.id, text=reply, reply_markup=markup)
        isTextFromMessage = False

    else:
        bot.send_message(message.chat.id, text="Некорректная команда")


# Обработка файлов для суммаризации текста
@bot.message_handler(content_types=["document"])
def file_summarizing(message):
    global isTextFromMessage, isTextFromFile, isChoosingSummarizingLevel, summarizing_level

    if isTextFromFile:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Сохраняем файл
        src = "text.txt"
        with open(src, "wb+") as txt_file:
            txt_file.write(downloaded_file)
        with open(src, "r", encoding="utf-8") as text_file:
            message_text = text_file.read()

        # Уведомляем пользователя о процессе суммаризации
        bot.send_message(message.chat.id, text="Подождите, пожалуйста, Ваш текст суммаризируется\nПроцесс может "
                                               "занять до 5 минут")

        # Кнопки для дальнейших действий
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Отправить текст для сжатия сообщением")
        btn2 = types.KeyboardButton("Отправить .txt файл для сжатия")
        markup.add(btn1, btn2)

        # Выполнение сжатия текста в зависимости от выбранного уровня
        if summarizing_level == 1:
            reply = summarizer.generate_std(message_text)
        elif summarizing_level == 2:
            reply = summarizer.generate_short(message_text)

        isTextFromFile = False
        bot.send_message(message.chat.id, text=reply, reply_markup=markup)


# Запуск бота
bot.polling(none_stop=True)

import telebot
from telebot import types
import datetime
import summarizer

token = "<token>"
bot = telebot.TeleBot(token)

isTextFromMessage = False
isTextFromFile = False
isChoosingSummarizingLevel = False
summarizing_level = 1


@bot.message_handler(commands=["start"])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Отправить текст для сжатия сообщением")
    btn2 = types.KeyboardButton("Отправить .txt файл для сжатия")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id,
                     text="Привет, {0.first_name}! Это PalPages!\n\nВыберите способ отправки текста\nВнимание! "
                          "Если в вашем тексте более 4096 символов, текст нужно отправить .txt файлом, "
                          "выбрав соответствующщий вариант".format(message.from_user), reply_markup=markup)
    print(message)


@bot.message_handler(content_types=["text"])
def func(message):
    global isTextFromMessage, isTextFromFile, isChoosingSummarizingLevel, summarizing_level
    print(
        f"{datetime.datetime.now()}: id:{message.chat.id}, {message.from_user.username} {message.from_user.first_name} "
        f"{message.from_user.last_name} - {message.text}"
    )

    if message.text == "Отправить текст для сжатия сообщением":
        isTextFromMessage = True
        isChoosingSummarizingLevel = True
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn3 = types.KeyboardButton("Стандартный")
        btn4 = types.KeyboardButton("Сильный")
        markup.add(btn3, btn4)

        bot.send_message(message.chat.id, text="Выберите уровень сжатия", reply_markup=markup)

    elif message.text == "Отправить .txt файл для сжатия":
        isTextFromFile = True
        isChoosingSummarizingLevel = True
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn3 = types.KeyboardButton("Стандартный")
        btn4 = types.KeyboardButton("Сильный")
        markup.add(btn3, btn4)

        bot.send_message(message.chat.id, text="Выберите уровень сжатия", reply_markup=markup)

    elif isChoosingSummarizingLevel and message.text == "Стандартный":
        summarizing_level = 1
        isChoosingSummarizingLevel = False
        if isTextFromFile:
            type = "файл"
        elif isTextFromMessage:
            type = "текст"

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Отправить текст для сжатия сообщением")
        btn2 = types.KeyboardButton("Отправить .txt файл для сжатия")
        markup.add(btn1, btn2)

        bot.send_message(message.chat.id, text=f"Отправьте {type} для сжатия", reply_markup=markup)

    elif isChoosingSummarizingLevel and message.text == "Сильный":
        summarizing_level = 2
        isChoosingSummarizingLevel = False
        if isTextFromFile:
            type = "файл"
        elif isTextFromMessage:
            type = "текст"

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Отправить текст для сжатия сообщением")
        btn2 = types.KeyboardButton("Отправить .txt файл для сжатия")
        markup.add(btn1, btn2)

        bot.send_message(message.chat.id, text=f"Отправьте {type} для сжатия", reply_markup=markup)

    elif isTextFromMessage and (message.text != "Сильный" or message.text != "Стандартный"):
        bot.send_message(message.chat.id, text="Подождите, пожалуйста, Ваш текст суммаризируется\nПроцесс может "
                                               "занять до 5 минут", reply_markup=types.ReplyKeyboardRemove())
        if summarizing_level == 1:
            reply = summarizer.generate_std(message.text)
        elif summarizing_level == 2:
            reply = summarizer.generate_short(message.text)

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Отправить текст для сжатия сообщением")
        btn2 = types.KeyboardButton("Отправить .txt файл для сжатия")
        markup.add(btn1, btn2)

        bot.send_message(message.chat.id, text=reply, reply_markup=markup)
        isTextFromMessage = False

    else:
        bot.send_message(message.chat.id, text="Некорректная команда")


@bot.message_handler(content_types=["document"])
def file_summarizing(message):
    global isTextFromMessage, isTextFromFile, isChoosingSummarizingLevel, summarizing_level

    if isTextFromFile:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        src = "text.txt"
        with open(src, "wb+") as txt_file:
            txt_file.write(downloaded_file)
        with open(src, "r", encoding="utf-8") as text_file:
            message_text = text_file.read()

        bot.send_message(message.chat.id, text="Подождите, пожалуйста, Ваш текст суммаризируется\nПроцесс может "
                                               "занять до 5 минут")

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Отправить текст для сжатия сообщением")
        btn2 = types.KeyboardButton("Отправить .txt файл для сжатия")
        markup.add(btn1, btn2)

        if summarizing_level == 1:
            reply = summarizer.generate_std(message_text)
        elif summarizing_level == 2:
            reply = summarizer.generate_short(message_text)

        isTextFromFile = False

        bot.delete_message(message.chat.id, message_id=message.message_id - 1)
        bot.send_message(message.chat.id, text=reply, reply_markup=markup)


bot.polling(none_stop=True)

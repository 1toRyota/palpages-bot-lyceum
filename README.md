# PalPages

PalPages — это Telegram-бот, который упрощает работу с литературными произведениями. Он помогает сокращать фрагменты произведений, давать ответы на вопросы и создавать тесты по прочитанному. Главной фишкой PalPages является функция "Эхо автора", которая позволяет пользователю пообщаться с авторами произведений с помощью ИИ.  

## Демо

Ознакомиться с демо-записью работы бота можно ознакомиться по ссылке: https://drive.google.com/file/d/1bwAaPB5I9PlYTaXYMytbNwvSOAVG-M_O/view?usp=sharing

## Описание

PalPages предлагает пользователям следующие функции:  

- **Добавление произведений**: Пользователи могут добавлять любые произведения, указав их авторов и названия.
- **Эхо автора**: Пользователи могут пообщаться с ИИ в роли автора произведения, чтобы лучше понять смысл.
- **Сокращение**: Бот позволяет сокращать фрагменты произведений с разной интенсивностью.
- **Создание тестов**: Пользователи могут создавать тесты по добавленным произведениям для самопроверки.
- **Управление профилем**: Возможность просматривать и управлять добавленными книгами.
- **Система друзей**: Возможность добавлять друзей и обмениваться прогрессом.

## Установка и запуск

1. Склонируйте репозиторий:
   ```bash
   git clone https://github.com/1toRyota/palpages-bot-sirius.git
   ```
2. Перейдите в папку проекта:
   ```bash
   cd palpages-bot-sirius
   ```
3. Установите библиотеки из requirements.txt:
   ```bash
   pip install -r requirements.txt
   ```
4. Установите LM Studio по ссылке: https://lmstudio.ai/download
5. Скачайте модель Gemma2 в LM Studio по ссылке: lmstudio://open_from_hf?model=DiTy/gemma-2-9b-it-russian-function-calling-GGUF
6. В настройках LM Studio: General > Уровень сложности интерфейса: **Разработчик**
7. В левом меню перейдите во вкладку **Разработка**
8. В верхнем меню выберите модель Gemma2 с подходящими настройками  
В проекте используются:  
- **Длина контекста** - 8192
- **Разгрузка GPU** - 42/42
- **CPU Thread Pool Size** - 6
- **Размер пакета оценки** - 512
9. Нажмите **Загрузить модель** (Ctrl+Enter)  
10. Дождитесь завершения загрузки модели  
11. С помощью кнопки **Start** (Ctrl+R) запустите локальный сервер с LLM  
12. Создайте базу данных с помощью:
   ```bash
   python3 database_creating.py
   ```
13. Откройте файл бота:
- **bot_for_additional_task.py** - код бота только для дополнительного задания
- **bot_main.py** - код полной версии прототипа бота
14. Замените значение переменной **token** на токен Вашего бота, созданного с помощью https://t.me/BotFather
15. Запустите бота с помощью:
   ```bash
   python3 bot_main.py
   ```
или
   ```bash
   python3 bot_for_additional_task.py
   ```

## Ход работы
- [x] Проектирование архитектуры бота и реализация базового функционала
- [x] Интеграция базы данных пользователей
- [x] Интеграция LLM GigaChat для дополнительных функций 
- [x] Итеграция локальной LLM для суммаризации текста
- [ ] Реализация функции **Эхо автора**
- [ ] Поддержка нескольких языков
    - [x] Русский
    - [ ] Английский

## Набор файлов
palpages-bot-sirius/  
   ├── bot_for_additional_task.py  
   ├── bot_main.py  
   ├── database.py  
   ├── database_creating.py  
   ├── gigachat_request.py  
   ├── summarizer.py  
   ├── text.txt  
   ├── user_data.db  
   ├── requirements.txt  
   └── README.md  

## Технологии
Далее описаны технологии, используемые в проекте

- **OpenSource LLM Gemma2, запущенная на локальном сервере** - суммаризация текста
- **LM Studio** - загрузка модели и запуск локального сервера
- **OpenAI API** - коммуникация между ботом и локальным сервером
- **LLM GigaChat** - ответы на вопросы и создание тестов по произведениям
- **GigaChat API** - обращение к LLM GigaChat
- **SQLite3** - база данных пользователей
- **PyTelegramBotAPI** - обработка сообщений ботом

## Контакты

- Email: d.n.mukhin@yandex.ru
- VK: [Дмитрий Мухин](https://vk.com/mukhin_d)
- Telegram: [@d_n_mukhin](https://t.me/d_n_mukhin)

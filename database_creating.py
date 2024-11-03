import sqlite3

# Подключение к базе данных SQLite
conn = sqlite3.connect('user_data.db')
cursor = conn.cursor()

# Создание таблицы
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    chat_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    summarizing_level INTEGER,
    books TEXT,
    friends TEXT,
    text TEXT,
    isWorkingWithBook INTEGER DEFAULT 0,
    workingWithBook INTEGER DEFAULT -1,
    isTextFromMessage INTEGER DEFAULT 0,
    isTextFromFile INTEGER DEFAULT 0,
    isChoosingSummarizingLevel INTEGER DEFAULT 0,
    isAddingBook INTEGER DEFAULT 0,
    isAddingFriend INTEGER DEFAULT 0,
    isChoosingBookForWork INTEGER DEFAULT 0,
    isChoosingBookForDeleting INTEGER DEFAULT 0,
    isDeletingFriend INTEGER DEFAULT 0,
    isAsking INTEGER DEFAULT 0,
    isWaiting INTEGER DEFAULT 0,
    isInProfile INTEGER DEFAULT 0,
    isInFriends INTEGER DEFAULT 0,
    isPlus INTEGER DEFAULT 0,
    isSeeingFriendBooks INTEGER DEFAULT 0
)
''')

conn.commit()  # Сохранение изменений
conn.close()  # Закрытие соединения с базой данных

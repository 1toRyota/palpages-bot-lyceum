import sqlite3
import json

# Соединение с базой данных SQLite
conn = sqlite3.connect('user_data.db', check_same_thread=False)
cursor = conn.cursor()


# Функция для проверки существования записи о пользователе
def user_exists(chat_id):
    cursor.execute('SELECT 1 FROM users WHERE chat_id = ?', (chat_id,))
    return cursor.fetchone() is not None


# Функция для регистрации нового пользователя
def register_user(chat_id, username, first_name, summarizing_level=0, books=None, friends=None, text=""):
    if not books:
        books = []
    if not friends:
        friends = []
    cursor.execute('''
    INSERT INTO users (chat_id, username, first_name, summarizing_level, books, friends, text)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (chat_id, username, first_name, summarizing_level, json.dumps(books), json.dumps(friends), text))
    conn.commit()


def reset_user_defaults(chat_id):
    # SQL-запрос для сброса значений переменных к дефолтным
    cursor.execute('''
        UPDATE users
        SET 
            summarizing_level = 0,
            text = '',
            isWorkingWithBook = 0,
            workingWithBook = -1,
            isTextFromMessage = 0,
            isTextFromFile = 0,
            isChoosingSummarizingLevel = 0,
            isAddingBook = 0,
            isAddingFriend = 0,
            isChoosingBookForWork = 0,
            isChoosingBookForDeleting = 0,
            isDeletingFriend = 0,
            isAsking = 0,
            isWaiting = 0,
            isInProfile = 0,
            isInFriends = 0,
            isPlus = 0,
            isSeeingFriendBooks = 0
        WHERE chat_id = ?
    ''', (chat_id,))

    # Сохранение изменений
    conn.commit()


# Функция для изменения значения summarizing_level у пользователя
def update_summarizing_level(chat_id, new_level):
    cursor.execute('UPDATE users SET summarizing_level = ? WHERE chat_id = ?', (new_level, chat_id))
    conn.commit()


# Функция для получения значения summarizing_level у пользователя
def get_summarizing_level(chat_id):
    cursor.execute('SELECT summarizing_level FROM users WHERE chat_id = ?', (chat_id,))
    result = cursor.fetchone()
    return result[0] if result else None


# Функция для добавления книг в список books пользователя
def add_books(chat_id, new_books):
    cursor.execute('SELECT books FROM users WHERE chat_id = ?', (chat_id,))
    result = cursor.fetchone()
    if result:
        books = json.loads(result[0])
        books.extend(new_books)
        cursor.execute('UPDATE users SET books = ? WHERE chat_id = ?', (json.dumps(books), chat_id))
        conn.commit()


# Функция для удаления книг из списка books пользователя
def remove_books(chat_id, books_to_remove):
    cursor.execute('SELECT books FROM users WHERE chat_id = ?', (chat_id,))
    result = cursor.fetchone()
    if result:
        books = json.loads(result[0])
        books = [book for book in books if book not in books_to_remove]
        cursor.execute('UPDATE users SET books = ? WHERE chat_id = ?', (json.dumps(books), chat_id))
        conn.commit()


# Функция для получения списка books пользователя
def get_books(chat_id):
    cursor.execute('SELECT books FROM users WHERE chat_id = ?', (chat_id,))
    result = cursor.fetchone()
    return json.loads(result[0]) if result else []


# Функция для получения значения isInProfile
def get_is_in_profile(chat_id):
    cursor.execute('SELECT isInProfile FROM users WHERE chat_id = ?', (chat_id,))
    result = cursor.fetchone()
    return bool(result[0]) if result else None


# Функция для получения значения isInFriends
def get_is_in_friends(chat_id):
    cursor.execute('SELECT isInFriends FROM users WHERE chat_id = ?', (chat_id,))
    result = cursor.fetchone()
    return bool(result[0]) if result else None


# Функция для добавления друзей в список friends пользователя
def add_friends(chat_id, new_friends):
    cursor.execute('SELECT friends FROM users WHERE chat_id = ?', (chat_id,))
    result = cursor.fetchone()
    if result:
        friends = json.loads(result[0])
        friends.extend(new_friends)
        cursor.execute('UPDATE users SET friends = ? WHERE chat_id = ?', (json.dumps(friends), chat_id))
        conn.commit()


# Функция для удаления друзей из списка friends пользователя
def remove_friends(chat_id, friends_to_remove):
    cursor.execute('SELECT friends FROM users WHERE chat_id = ?', (chat_id,))
    result = cursor.fetchone()
    if result:
        friends = json.loads(result[0])
        friends = [friend for friend in friends if friend not in friends_to_remove]
        cursor.execute('UPDATE users SET friends = ? WHERE chat_id = ?', (json.dumps(friends), chat_id))
        conn.commit()


# Функция для получения списка friends пользователя
def get_friends(chat_id):
    cursor.execute('SELECT friends FROM users WHERE chat_id = ?', (chat_id,))
    result = cursor.fetchone()
    return json.loads(result[0]) if result else []


# Функция для получения chat_id пользователя по его username
def get_friend_chat_id(friend_username):
    cursor.execute('SELECT chat_id FROM users WHERE username = ?', (friend_username,))
    result = cursor.fetchone()
    return result[0] if result else None


# Функция для перезаписи текста пользователя
def update_text(chat_id, new_text):
    cursor.execute('UPDATE users SET text = ? WHERE chat_id = ?', (new_text, chat_id))
    conn.commit()


# Функция для получения значения isTextFromMessage
def get_is_text_from_message(chat_id):
    cursor.execute('SELECT isTextFromMessage FROM users WHERE chat_id = ?', (chat_id,))
    result = cursor.fetchone()
    return bool(result[0]) if result else None


# Функция для получения значения isTextFromFile
def get_is_text_from_file(chat_id):
    cursor.execute('SELECT isTextFromFile FROM users WHERE chat_id = ?', (chat_id,))
    result = cursor.fetchone()
    return bool(result[0]) if result else None


# Функция для получения значения isChoosingSummarizingLevel
def get_is_choosing_summarizing_level(chat_id):
    cursor.execute('SELECT isChoosingSummarizingLevel FROM users WHERE chat_id = ?', (chat_id,))
    result = cursor.fetchone()
    return bool(result[0]) if result else None


# Функция для получения значения isAddingBook
def get_is_adding_book(chat_id):
    cursor.execute('SELECT isAddingBook FROM users WHERE chat_id = ?', (chat_id,))
    result = cursor.fetchone()
    return bool(result[0]) if result else None


# Функция для получения значения isAddingFriend
def get_is_adding_friend(chat_id):
    cursor.execute('SELECT isAddingFriend FROM users WHERE chat_id = ?', (chat_id,))
    result = cursor.fetchone()
    return bool(result[0]) if result else None


# Функция для получения значения isDeletingFriend
def get_is_deleting_friend(chat_id):
    cursor.execute('SELECT isDeletingFriend FROM users WHERE chat_id = ?', (chat_id,))
    result = cursor.fetchone()
    return bool(result[0]) if result else None


# Функция для получения значения isWorkingWithBook
def get_is_working_with_book(chat_id):
    cursor.execute('SELECT isWorkingWithBook FROM users WHERE chat_id = ?', (chat_id,))
    result = cursor.fetchone()
    return bool(result[0]) if result else None


# Функция для получения значения workingWithBook
def get_working_with_book(chat_id):
    cursor.execute('SELECT workingWithBook FROM users WHERE chat_id = ?', (chat_id,))
    result = cursor.fetchone()
    return result[0] if result else None


# Функция для получения значения isChoosingBookForWork
def get_is_choosing_book_for_work(chat_id):
    cursor.execute('SELECT isChoosingBookForWork FROM users WHERE chat_id = ?', (chat_id,))
    result = cursor.fetchone()
    return bool(result[0]) if result else None


# Функция для получения значения isAsking
def get_is_asking(chat_id):
    cursor.execute('SELECT isAsking FROM users WHERE chat_id = ?', (chat_id,))
    result = cursor.fetchone()
    return bool(result[0]) if result else None


def get_is_plus(chat_id):
    cursor.execute('SELECT isPlus FROM users WHERE chat_id = ?', (chat_id,))
    result = cursor.fetchone()
    return bool(result[0]) if result else None


# Функция для получения значения isSeeingFriendBooks
def get_is_seeing_friend_books(chat_id):
    cursor.execute('SELECT isSeeingFriendBooks FROM users WHERE chat_id = ?', (chat_id,))
    result = cursor.fetchone()
    return bool(result[0]) if result else None


# Функция для получения значения isWaiting
def get_is_waiting(chat_id):
    cursor.execute('SELECT isWaiting FROM users WHERE chat_id = ?', (chat_id,))
    result = cursor.fetchone()
    return bool(result[0]) if result else None


# Функция для получения значения isChoosingBookForDeleting
def get_is_choosing_book_for_deleting(chat_id):
    cursor.execute('SELECT isChoosingBookForDeleting FROM users WHERE chat_id = ?', (chat_id,))
    result = cursor.fetchone()
    return bool(result[0]) if result else None


# Функция для изменения булевой переменной isWorkingWithBook
def set_is_working_with_book(chat_id, value):
    cursor.execute('UPDATE users SET isWorkingWithBook = ? WHERE chat_id = ?', (int(value), chat_id))

    if not value:
        set_working_with_book(chat_id, -1)

    conn.commit()


# Функция для изменения значения isChoosingBookForWork
def set_is_choosing_book_for_work(chat_id, value):
    cursor.execute('UPDATE users SET isChoosingBookForWork = ? WHERE chat_id = ?', (int(value), chat_id))
    conn.commit()


# Функция для изменения значения isChoosingBookForDeleting
def set_is_choosing_book_for_deleting(chat_id, value):
    cursor.execute('UPDATE users SET isChoosingBookForDeleting = ? WHERE chat_id = ?', (int(value), chat_id))
    conn.commit()


# Функция для изменения числовой переменной workingWithBook
def set_working_with_book(chat_id, value):
    cursor.execute('UPDATE users SET workingWithBook = ? WHERE chat_id = ?', (value + 1, chat_id))
    conn.commit()


# Функция для изменения значения isSeeingFriendBooks
def set_is_seeing_friend_books(chat_id, value):
    cursor.execute('UPDATE users SET isSeeingFriendBooks = ? WHERE chat_id = ?', (int(value), chat_id))
    conn.commit()


# Функция для изменения значения isTextFromMessage
def set_is_text_from_message(chat_id, value):
    cursor.execute('UPDATE users SET isTextFromMessage = ? WHERE chat_id = ?', (int(value), chat_id))
    conn.commit()


# Функция для изменения значения isTextFromFile
def set_is_text_from_file(chat_id, value):
    cursor.execute('UPDATE users SET isTextFromFile = ? WHERE chat_id = ?', (int(value), chat_id))
    conn.commit()


# Функция для изменения значения isChoosingSummarizingLevel
def set_is_choosing_summarizing_level(chat_id, value):
    cursor.execute('UPDATE users SET isChoosingSummarizingLevel = ? WHERE chat_id = ?', (int(value), chat_id))
    conn.commit()


# Функция для изменения значения isAddingBook
def set_is_adding_book(chat_id, value):
    cursor.execute('UPDATE users SET isAddingBook = ? WHERE chat_id = ?', (int(value), chat_id))
    conn.commit()


# Функция для изменения значения isAddingFriend
def set_is_adding_friend(chat_id, value):
    cursor.execute('UPDATE users SET isAddingFriend = ? WHERE chat_id = ?', (int(value), chat_id))
    conn.commit()


# Функция для изменения значения isDeletingFriend
def set_is_deleting_friend(chat_id, value):
    cursor.execute('UPDATE users SET isDeletingFriend = ? WHERE chat_id = ?', (int(value), chat_id))
    conn.commit()


# Функция для изменения значения isInProfile
def set_is_in_profile(chat_id, value):
    cursor.execute('UPDATE users SET isInProfile = ? WHERE chat_id = ?', (int(value), chat_id))
    conn.commit()


# Функция для изменения значения isInFriends
def set_is_in_friends(chat_id, value):
    cursor.execute('UPDATE users SET isInFriends = ? WHERE chat_id = ?', (int(value), chat_id))
    conn.commit()


# Функция для изменения значения isAsking
def set_is_asking(chat_id, value):
    cursor.execute('UPDATE users SET isAsking = ? WHERE chat_id = ?', (int(value), chat_id))
    conn.commit()


def set_is_plus(chat_id, value):
    cursor.execute('UPDATE users SET isPlus = ? WHERE chat_id = ?', (int(value), chat_id))
    conn.commit()


# Функция для изменения значения isWaiting
def set_is_waiting(chat_id, value):
    cursor.execute('UPDATE users SET isWaiting = ? WHERE chat_id = ?', (int(value), chat_id))
    conn.commit()


# Закрытие соединения с базой данных
def close_connection():
    conn.close()

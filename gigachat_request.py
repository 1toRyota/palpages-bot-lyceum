from langchain.schema import HumanMessage, SystemMessage
from langchain_community.chat_models.gigachat import GigaChat


chat = GigaChat(
    credentials='NjdjNTYzMTAtNGUwOS00YmE5LWE2ZDctMDQzZjYxZDBlMjk1Ojg0MTdlZjY1LTIzYWItNGE3Ni1iNDRkLTc5YmY3NjUwMDg4NA==',
    verify_ssl_certs=False)


def question(user_question, book_name):
    messages = [
        SystemMessage(
            content='Ты – умный помощник по литературе. Твоя главная задача – верно ответить на вопрос по '
                    'произведению. Любые отклонение от оригинального произведения недопустимы.'
        )
    ]
    user_input = f'Ответь на вопрос по произведению {book_name}: {user_question}'
    messages.append(HumanMessage(content=user_input))
    res = chat(messages)
    messages.append(res)
    return res.content


def test(book_name):
    messages = [
        SystemMessage(
            content='Ты – умный помощник по литературе. Твоя главная задача – составить тест из 10 вопросов по 4 '
                    'варианта ответа в каждом по заданному произведению. Любые отклонение от оригинального '
                    'произведения недопустимы.'
        )
    ]
    user_input = f'Создай тест по произведению {book_name}'
    messages.append(HumanMessage(content=user_input))
    res = chat(messages)
    messages.append(res)
    return res.content

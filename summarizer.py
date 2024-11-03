from openai import OpenAI

client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")


def generate_std(message_text):
    completion = client.chat.completions.create(
        model="gemma-2-9b",
        messages=[
            {"role": "system",
             "content": "Ты – бот, который специализируется на создании точных суммаризаций любых текстов. Ты "
                        "анализируешь содержание и представляешь текст в сжатой форме, сохраняя основной смысл и "
                        "контекст. Ты должен адаптироваться под любые стили и форматы текста, предоставляя ответ, "
                        "соответствующий запросам пользователя. Если в тексте больше 10 предложений, то его нужно "
                        "сжать минимум до 5-7 предложений."},
            {"role": "user", "content": f"Сократи этот текст: {message_text}"}
        ],
        temperature=0.9,
    )
    return completion.choices[0].message.content


def generate_short(message_text):
    completion = client.chat.completions.create(
        model="gemma-2-9b",
        messages=[
            {"role": "system",
             "content": "Ты – бот, который специализируется на создании точных и кратких суммаризаций любых текстов. "
                        "Ты анализируешь содержание и представляешь текст в сжатой форме, сохраняя основной смысл и "
                        "контекст. Ты должен адаптироваться под любые стили и форматы текста, предоставляя ответ, "
                        "соответствующий запросам пользователя Главная задача: сжать текст в 2-3 предложения."},
            {"role": "user", "content": f"Сократи этот текст до 2-3 предложений: {message_text}"}
        ],
        temperature=0.5
    )
    return completion.choices[0].message.content

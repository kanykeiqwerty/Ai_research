import json

from groq import Groq
from config import GROQ_API_KEY 

client = Groq(api_key=GROQ_API_KEY)


def build_prompt(bank_name: str) -> str:
    return f"""
Найди руководство банка "{bank_name}".

Ответь строго в JSON формате:

[
  {{
    "full_name": "",
    "position": "",
    "phone": "",
    "email": "",
    "social_links": ""
  }}
]

Если данных нет — верни [].
Никакого текста вне JSON.
"""


def call_model(prompt: str):
    if not prompt.strip():
        print("⚠ Пустой prompt, возвращаю []")
        return []

    try:
        # Вызов GROQ API
        chat_completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=[
                {"role": "system", "content": "Ты возвращаешь только JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=8192
        )

        # Ответ модели
        content = chat_completion.choices[0].message.content.strip()

        # Пробуем распарсить JSON
        return json.loads(content)
    except json.JSONDecodeError:
        print("⚠ Ошибка JSON:", content)
        return []
    except Exception as e:
        print("⚠ Ошибка запроса:", e)
        return []

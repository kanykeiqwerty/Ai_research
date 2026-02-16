# ai_clients/groq_client.py
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


def call_groq_model(prompt: str, model_name: str):
    """Общая функция для вызова любой модели Groq"""
    if not prompt.strip():
        print("⚠ Пустой prompt, возвращаю []")
        return []

    try:
        chat_completion = client.chat.completions.create(
            model=model_name,  # <-- передаём название модели
            messages=[
                {"role": "system", "content": "Ты возвращаешь только JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=8192
        )

        content = chat_completion.choices[0].message.content.strip()
        return json.loads(content)
    except json.JSONDecodeError:
        print(f"⚠ Ошибка JSON ({model_name}):", content)
        return []
    except Exception as e:
        print(f"⚠ Ошибка запроса ({model_name}):", e)
        return []
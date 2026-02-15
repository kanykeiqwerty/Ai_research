import json
from groq import Groq
from config import GROQ_API_KEY 

client = Groq(api_key=GROQ_API_KEY)


def build_prompt(bank_name: str, stage: str = "initial") -> str:
    """
    Строит промпт для поиска руководства банка.
    stage: "initial" для первого запроса, "verify" для проверки
    """
    
    if stage == "initial":
        return f"""
Найди ПОЛНУЮ информацию о руководстве банка "{bank_name}".

Ищи ВСЕХ топ-менеджеров:
- Председатель Правления / CEO / Президент
- Заместители председателя
- Члены Правления
- Директора ключевых департаментов

Для каждого человека собери:
- Полное ФИО (Фамилия Имя Отчество)
- Точная должность
- Номер Телефона (если доступен)
- Email (если доступен)
- Ссылки на LinkedIn или другие соцсети

ВАЖНО: 
- Ищи актуальную информацию (2024-2026)
- Используй официальный сайт банка
- Проверяй несколько источников
- НЕ выдумывай данные - только проверенные факты
-Если личный телефон отсутствует, укажи общий телефон банка.
-Если личный email отсутствует, укажи общий email банка.
Ответь СТРОГО в JSON формате:

[
  {{
    "full_name": "Фамилия Имя Отчество",
    "position": "Точная должность",
    "phone": "Номер Телефона или null",
    "email": "Email или null",
    "social_links": "URL соцсетей или null"
  }}
]

Если данных нет — верни [].
Никакого текста вне JSON.
"""
    
    elif stage == "verify":
        return f"""
ПРОВЕРКА И ДОПОЛНЕНИЕ данных о руководстве банка "{bank_name}".

Я уже нашёл некоторых руководителей. Твоя задача:
1. ПРОВЕРИТЬ актуальность найденных данных
2. НАЙТИ дополнительных руководителей (которых я мог пропустить)
3. ДОПОЛНИТЬ недостающие контакты (телефоны, email, соцсети)

Ищи на официальном сайте банка, в новостях, в пресс-релизах.

ОСОБОЕ ВНИМАНИЕ:
- Заместители председателя правления
- Члены правления
- Руководители ключевых направлений (IT, Risk, Finance, HR)

Ответь СТРОГО в JSON формате:

[
  {{
    "full_name": "Фамилия Имя Отчество",
    "position": "Точная должность",
    "phone": "Телефон или null",
    "email": "Email или null",
    "social_links": "URL соцсетей или null"
  }}
]

ВАЖНО:
- Только актуальные данные (2024-2026)
- Только проверенные факты
- Если данных нет — верни []
- Никакого текста вне JSON
-Если личный телефон отсутствует, укажи общий телефон банка.
-Если личный email отсутствует, укажи общий email банка.
"""
    
    else:
        raise ValueError(f"Unknown stage: {stage}")


def call_model(prompt: str, model: str = "llama-3.3-70b-versatile"):
    """
    Вызывает Groq API с промптом.
    Groq автоматически использует веб-поиск, если нужно.
    """
    if not prompt.strip():
        print("⚠ Пустой prompt, возвращаю []")
        return []

    try:
        # Вызов GROQ API с системным промптом для активации поиска
        chat_completion = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system", 
                    "content": """Ты эксперт по поиску информации о компаниях и их руководстве.

ОБЯЗАТЕЛЬНО используй веб-поиск для получения актуальной информации.
Ищи на официальных сайтах компаний, в новостях, пресс-релизах.

Возвращай ТОЛЬКО валидный JSON массив.
Никакого текста, пояснений или markdown - только чистый JSON."""
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0,  # Низкая температура для точности
            max_tokens=500,  # Больше токенов для полного списка
        )

        # Ответ модели
        content = chat_completion.choices[0].message.content.strip()
        
        # Очистка от возможных markdown обёрток
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        
        content = content.strip()

        # Пробуем распарсить JSON
        parsed = json.loads(content)
        
        # Проверяем, что это список
        if not isinstance(parsed, list):
            print(f"⚠ Ожидался список, получено: {type(parsed)}")
            return []
        
        return parsed
        
    except json.JSONDecodeError as e:
        print(f"⚠ Ошибка JSON парсинга: {e}")
        print(f"Ответ модели (первые 500 символов):\n{content[:500]}")
        
        # Попытка извлечь JSON из текста
        try:
            # Ищем JSON массив в тексте
            start = content.find('[')
            end = content.rfind(']') + 1
            if start != -1 and end > start:
                json_str = content[start:end]
                return json.loads(json_str)
        except:
            pass
        
        return []
        
    except Exception as e:
        print(f"⚠ Ошибка запроса к Groq API: {e}")
        return []


def call_model_with_retry(prompt: str, max_retries: int = 2):
    """
    Вызывает модель с повторными попытками при ошибках.
    """
    for attempt in range(max_retries):
        try:
            result = call_model(prompt)
            if result:  # Если получили результат
                return result
            
            if attempt < max_retries - 1:
                print(f"  ⚠ Попытка {attempt + 1}/{max_retries}: пустой результат, повторяю...")
                
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"  ⚠ Попытка {attempt + 1}/{max_retries}: ошибка {e}, повторяю...")
            else:
                print(f"  ❌ Все попытки исчерпаны: {e}")
    
    return []
import json
import re
from time import sleep
from groq import Groq
from config import GROQ_API_KEY 

client = Groq(api_key=GROQ_API_KEY)


def build_prompt(bank_name: str, stage: str = "initial", existing_data=None) -> str:
    """
    Строит промпт для поиска руководства банка.
    
    Args:
        bank_name: Название банка
        stage: "initial" для первого поиска, "verify" для проверки
        existing_data: Уже найденные данные (для этапа verify)
    """
    
    if stage == "initial":
        # AI-1: Первичный поиск - ищем ВСЕХ руководителей
        return f'''Найди руководителей банка "{bank_name}" 

Искать должности:
- Председатель правления / CEO
- Заместители председателя
- Коммерческий директор
- Директор по продуктам
- Директор по цифровой трансформации / Digital
- Директор по развитию
- Директор розничного блока
- Директор корпоративного блока
- Директор по маркетингу / CMO
- IT-директор / CTO
- Директор по рискам / CRO
- Директор по продажам
- Руководитель проектов / PMO
- Руководитель блока МСБ
- CISO / Информационная безопасность
- Head of Innovation
- Enterprise Architect
- Юридический директор
- Директор по закупкам

Верни ТОЛЬКО JSON массив (без markdown):
[{{"full_name":"Фамилия Имя Отчество","position":"Должность","phone":"","email":""}}]

Требования:
- ФИО только на РУССКОМ языке (кириллица)
- Если нашёл на английском - переведи на русский
- Телефон и email - если найдены
- Если ничего не найдено - верни []
- НЕ включай людей не из этого банка'''
    
    elif stage == "verify":
        # AI-2: Проверка и дополнение
        existing_str = ""
        if existing_data:
            existing_str = "\n\nУЖЕ НАЙДЕННЫЕ ДАННЫЕ:\n"
            for person in existing_data:
                existing_str += f"- {person.full_name}, {person.position}"
                if person.phone:
                    existing_str += f", тел: {person.phone}"
                if person.email:
                    existing_str += f", email: {person.email}"
                existing_str += "\n"
        
        return f'''Проверь информацию о руководстве банка "{bank_name}".
{existing_str}

ЗАДАЧИ:
1. Проверь актуальность найденных людей (работают ли они там сейчас)
2. Дополни контакты (телефон, email) для уже найденных людей
3. НЕ придумывай контакты
4. Проверяй что человек работает именно в банке "{bank_name}"

Верни ТОЛЬКО JSON массив (без markdown):
[{{"full_name":"Фамилия Имя Отчество","position":"Должность","phone":"","email":""}}]

Требования:
- ФИО только на РУССКОМ языке
- Если человек УЖЕ ЕСТЬ в списке выше - НЕ дублируй его, просто добавь контакты если нашёл

- Если информация не найдена или устарела - укажи в comment
- Если ничего нового не найдено - верни []'''
    
    else:
        raise ValueError(f"Unknown stage: {stage}")


def call_model(prompt: str):
    """
    Вызывает Groq Compound с веб-поиском.
    """
    if not prompt.strip():
        return []

    try:
        completion = client.chat.completions.create(
            model="groq/compound",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_completion_tokens=2048,  # Увеличено для большего количества результатов
            top_p=1,
            stream=True,
            stop=None,
            compound_custom={"tools":{"enabled_tools":["web_search"]}}
        )

        content = ""
        for chunk in completion:
            delta_content = chunk.choices[0].delta.content or ""
            content += delta_content

        # Убираем markdown и лишние пробелы
        for marker in ["```json", "```", "```\n", "\n```"]:
            content = content.replace(marker, "")
        content = content.strip()

        # Проверка на пустой ответ
        if not content:
            print(f"  ⚠️ Модель вернула пустой ответ")
            return []
        
        # Ищем JSON в тексте
        start_idx = content.find('[')
        end_idx = content.rfind(']')
        
        if start_idx == -1 or end_idx == -1:
            print(f"  ⚠️ JSON не найден в ответе: {content[:200]}")
            return []
        
        json_str = content[start_idx:end_idx+1]
        
        # Парсим JSON
        parsed = json.loads(json_str)
        
        if not isinstance(parsed, list):
            print(f"  ⚠️ Ответ не список: {type(parsed)}")
            return []
        
        return parsed

    except json.JSONDecodeError as e:
        print(f"  ⚠️ Ошибка парсинга JSON: {e}")
        print(f"  📄 Сырой ответ (первые 500 символов): {content[:500] if content else 'ПУСТО'}")
        return []
    
    except Exception as e:
        print(f"  ⚠️ Ошибка Groq Compound: {e}")
        raise e


def call_model_with_retry(prompt: str, max_retries: int = 5):
    """
    Вызывает модель с повторными попытками при ошибках.
    Автоматически обрабатывает Rate Limit и Request Too Large.
    """
    for attempt in range(max_retries):
        try:
            result = call_model(prompt)
            
            if result:
                sleep(3)  # Пауза после успешного запроса
                return result
            
            return []
            
        except Exception as e:
            error_msg = str(e)
            
            # ОБРАБОТКА REQUEST TOO LARGE
            if "Request Entity Too Large" in error_msg or "Too Large" in error_msg:
                print(f"  ⚠️ Запрос слишком большой. Веб-страница банка очень объемная.")
                return []
            
            # ОБРАБОТКА RATE LIMIT
            if "Rate limit" in error_msg:
                match = re.search(r'try again in ([\d.]+)s', error_msg)
                
                if match:
                    wait_time = float(match.group(1)) + 3
                else:
                    wait_time = 25
                
                print(f"  ⏳ Rate limit. Ожидание {wait_time:.1f}с...")
                sleep(wait_time)
                continue
            
            # ДРУГИЕ ОШИБКИ
            if attempt < max_retries - 1:
                print(f"  ⚠️ Попытка {attempt + 1}/{max_retries}: {error_msg[:150]}")
                sleep(5)
            else:
                print(f"  ❌ Все попытки исчерпаны: {error_msg[:150]}")
                return []
    
    return []
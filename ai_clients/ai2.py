from models import Person
from ai_clients.base import build_prompt, call_model_with_retry
from groq import Groq
from config import GROQ_API_KEY
import json
from time import sleep

client = Groq(api_key=GROQ_API_KEY)


def call_llama(prompt: str, max_retries: int = 3):
    """
    Вызывает Llama через Groq API для проверки и дополнения данных.
    """
    for attempt in range(max_retries):
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",  # Можно заменить на другую модель Llama
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=2048,
                top_p=1,
                stream=False,
            )
            
            content = completion.choices[0].message.content.strip()
            
            if not content:
                print(f"  ⚠️ Llama вернула пустой ответ")
                return []
            
            # Убираем markdown
            for marker in ["```json", "```", "```\n", "\n```"]:
                content = content.replace(marker, "")
            content = content.strip()
            
            # Ищем JSON
            start_idx = content.find('[')
            end_idx = content.rfind(']')
            
            if start_idx == -1 or end_idx == -1:
                print(f"  ⚠️ JSON не найден в ответе Llama")
                return []
            
            json_str = content[start_idx:end_idx+1]
            parsed = json.loads(json_str)
            
            if not isinstance(parsed, list):
                return []
            
            return parsed
            
        except json.JSONDecodeError as e:
            print(f"  ⚠️ Ошибка парсинга JSON от Llama: {e}")
            if attempt < max_retries - 1:
                sleep(3)
                continue
            return []
            
        except Exception as e:
            error_msg = str(e)
            
            if "Rate limit" in error_msg:
                print(f"  ⏳ Rate limit Llama, ожидание...")
                sleep(20)
                continue
            
            if attempt < max_retries - 1:
                print(f"  ⚠️ Попытка {attempt + 1}/{max_retries}: {error_msg[:150]}")
                sleep(5)
            else:
                print(f"  ❌ Llama: {error_msg[:150]}")
                return []
    
    return []


def search(bank_name: str, existing_data=None):
    """
    AI-2: Второй этап - проверка и дополнение данных.
    Использует Llama через Groq API.
    
    Args:
        bank_name: Название банка
        existing_data: Список Person объектов из AI-1
    """
    print(f"  🔍 AI-2 (Llama): Проверка и дополнение данных для {bank_name}")
    
    # Строим промпт для проверки
    prompt = build_prompt(bank_name, stage="verify", existing_data=existing_data)
    
    # Вызываем Llama
    data = call_llama(prompt)
    
    if not data:
        print(f"  ℹ️ AI-2: Нет дополнительных данных для {bank_name}")
        return []
    
    print(f"  ✅ AI-2: Найдено {len(data)} записей для проверки/дополнения")
    
    # Конвертируем в объекты Person
    persons = []
    for item in data:
        full_name = item.get("full_name", "").strip()
        if not full_name or len(full_name.split()) < 2:
            continue
        
        # Проверяем кириллицу
        if not any(ord(c) >= 0x0400 and ord(c) <= 0x04FF for c in full_name):
            print(f"    ⚠️ Пропущено (не кириллица): {full_name}")
            continue
        
        person = Person(
            bank=bank_name,
            full_name=full_name,
            position=item.get("position", "").strip(),
            phone=item.get("phone") if item.get("phone") else None,
            email=item.get("email") if item.get("email") else None,
            social_links=item.get("social_links") if item.get("social_links") else None,
            source="AI-2 (Llama)",
            comment=item.get("comment", "").strip() if item.get("comment") else None
        )
        
        persons.append(person)
        print(f"    - {person.full_name} ({person.position})")
        if person.comment:
            print(f"      💬 {person.comment}")
    
    return persons
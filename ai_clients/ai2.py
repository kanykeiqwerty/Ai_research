from models import Person
from ai_clients.base import build_prompt, call_model_with_retry


def search(bank_name: str, existing_data: list = None):
    """
    AI-2: Второй этап - проверка и дополнение данных.
    Получает результаты AI-1 и ищет дополнительную информацию.
    """
    print(f"  🔍 AI-2: Проверка и дополнение для {bank_name}")
    
    if existing_data:
        print(f"  📋 AI-2: Уже найдено {len(existing_data)} человек, ищу дополнительно...")
    
    # Строим промпт для проверки и дополнения
    prompt = build_prompt(bank_name, stage="verify")
    
    # Вызываем модель
    data = call_model_with_retry(prompt)
    
    if not data:
        print(f"  ⚠️ AI-2: Дополнительной информации не найдено")
        return []
    
    print(f"  ✓ AI-2: Найдено {len(data)} человек(а)")
    
    # Конвертируем в объекты Person
    persons = []
    for item in data:
        # Пропускаем пустые записи
        full_name = item.get("full_name", "").strip()
        if not full_name or len(full_name.split()) < 2:
            continue
        
        person = Person(
            bank=bank_name,
            full_name=full_name,
            position=item.get("position", "").strip(),
            phone=item.get("phone") if item.get("phone") else None,
            email=item.get("email") if item.get("email") else None,
            social_links=item.get("social_links") if item.get("social_links") else None,
            source="AI-2 (Groq Web Search)"
        )
        
        persons.append(person)
        print(f"    - {person.full_name} ({person.position})")
    
    return persons
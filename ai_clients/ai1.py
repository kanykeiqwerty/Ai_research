from models import Person
from ai_clients.base import build_prompt, call_model_with_retry


def search(bank_name: str):
    """
    AI-1: Первый этап поиска руководства банка.
    Использует встроенный веб-поиск Groq.
    """
    print(f"  🔍 AI-1: Поиск руководства {bank_name}")
    
    # Строим промпт для начального поиска
    prompt = build_prompt(bank_name, stage="initial")
    
    # Вызываем модель (Groq автоматически использует веб-поиск)
    data = call_model_with_retry(prompt)
    
    if not data:
        print(f"  ❌ AI-1: Ничего не найдено для {bank_name}")
        return []
    
    print(f"  ✓ AI-1: Найдено {len(data)} человек(а)")
    
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
            source="AI-1 (Groq Web Search)"
        )
        
        persons.append(person)
        print(f"    - {person.full_name} ({person.position})")
    
    if not persons:
        print(f"  ⚠️ После фильтрации не осталось валидных записей")
        print(f"  📝 Создаём пустую запись для банка")
        
        empty_person = Person(
            bank=bank_name,
            full_name="",
            position="",
            phone=None,
            email=None,
            social_links=None,
            source="AI-1 (Groq Web Search)",
            comment="Информация не найдена или отфильтрована"
        )
        return [empty_person]
    
    return persons

# merger.py
from difflib import SequenceMatcher


def normalize(text: str):
    """Базовая нормализация текста"""
    if not text:
        return ""
    return text.lower().replace(".", "").replace(" ", "").strip()


def similarity(a: str, b: str) -> float:
    """Вычисляет схожесть двух строк (0.0 - 1.0)"""
    return SequenceMatcher(None, normalize(a), normalize(b)).ratio()


def is_same_person(person1, person2, threshold=0.85) -> bool:
    """
    Проверяет, являются ли два человека одним и тем же.
    Использует схожесть ФИО и совпадение должности.
    """
    # Сравниваем ФИО
    name_similarity = similarity(person1.full_name, person2.full_name)
    
    # Если ФИО очень похожи (например, отличается только отчество)
    if name_similarity >= threshold:
        return True
    
    # Дополнительная проверка: если фамилия + имя совпадают
    name1_parts = person1.full_name.split()
    name2_parts = person2.full_name.split()
    
    if len(name1_parts) >= 2 and len(name2_parts) >= 2:
        # Сравниваем фамилию и имя (первые два слова)
        first_two_1 = " ".join(name1_parts[:2])
        first_two_2 = " ".join(name2_parts[:2])
        
        if normalize(first_two_1) == normalize(first_two_2):
            return True
    
    return False


def merge(existing, new):
    """Объединяет два списка Person с учетом дубликатов"""
    merged = existing.copy()
    
    for new_person in new:
        found = False
        
        for old_person in merged:
            if is_same_person(old_person, new_person):
                found = True
                
                print(f"  🔄 Найден дубликат: {old_person.full_name} ≈ {new_person.full_name}")
                
                # Обновляем данные (берем более полные)
                if not old_person.phone and new_person.phone:
                    old_person.phone = new_person.phone
                    print(f"     📞 Добавлен телефон")
                
                if not old_person.email and new_person.email:
                    old_person.email = new_person.email
                    print(f"     📧 Добавлен email")
                
                if not old_person.social_links and new_person.social_links:
                    old_person.social_links = new_person.social_links
                    print(f"     🔗 Добавлены соцсети")
                
                # Проверяем конфликты в ФИО
                if normalize(old_person.full_name) != normalize(new_person.full_name):
                    old_person.comment = f"Возможные варианты ФИО: {old_person.full_name} / {new_person.full_name}"
                    print(f"     ⚠️  Разные варианты ФИО")
                
                # Проверяем конфликты в должности
                if normalize(old_person.position) != normalize(new_person.position):
                    if old_person.comment:
                        old_person.comment += f"; Должности: {old_person.position} / {new_person.position}"
                    else:
                        old_person.comment = f"Должности: {old_person.position} / {new_person.position}"
                    old_person.status = "Конфликт"
                    print(f"     ⚠️  Конфликт должностей")
                
                # Объединяем источники
                if new_person.source not in old_person.source:
                    old_person.source = f"{old_person.source}, {new_person.source}"
                
                break
        
        if not found:
            merged.append(new_person)
            print(f"  ➕ Добавлен новый: {new_person.full_name} ({new_person.position})")
    
    return merged

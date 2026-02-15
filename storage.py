# storage.py
import json
import os

from excel import save_results
current_results = None
current_output_file = None
def save_checkpoint(data: dict, filename: str):
    checkpoint = {}
    
    for bank, persons in data.items():
        checkpoint[bank] = []
        for person in persons:
            checkpoint[bank].append({
                "bank": person.bank,
                "full_name": person.full_name,
                "position": person.position,
                "phone": person.phone,
                "email": person.email,
                "social_links": person.social_links,
                "source": person.source,
                "date_collected": person.date_collected,
                "status": person.status,
                "comment": person.comment
            })
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(checkpoint, f, ensure_ascii=False, indent=2)


def load_checkpoint(filename: str = "checkpoint_stage.json"):
    """Загружает сохранённые результаты."""
    if not os.path.exists(filename):
        return None
    
    from models import Person
    
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    results = {}
    for bank, persons_data in data.items():
        results[bank] = []
        for item in persons_data:
            results[bank].append(
                Person(
                    bank=item["bank"],
                    full_name=item["full_name"],
                    position=item["position"],
                    phone=item.get("phone"),
                    email=item.get("email"),
                    social_links=item.get("social_links"),
                    source=item.get("source", ""),
                    date_collected=item.get("date_collected", ""),
                    status=item.get("status", "Найдено"),
                    comment=item.get("comment", "")
                )
            )
    
    print(f"📂 Загружен checkpoint: {len(results)} банков")
    return results


def emergency_save():
    """
    Аварийное сохранение при закрытии программы (Ctrl+C, ошибка и т.д.).
    Сохраняет все имеющиеся данные в Excel.
    """
    global current_results, current_output_file
    
    if current_results and current_output_file:
        try:
            print(f"\n\n{'='*60}")
            print(f"⚠️  АВАРИЙНОЕ СОХРАНЕНИЕ")
            print(f"{'='*60}")
            
            # Собираем все результаты в один список
            all_persons = []
            for bank, persons in current_results.items():
                all_persons.extend(persons)
            
            if all_persons:
                # Сохраняем в Excel
                save_results(current_output_file, all_persons)
                
                print(f"✅ Данные успешно сохранены!")
                print(f"💾 Файл: {current_output_file}")
                print(f"📁 Записей: {len(all_persons)}")
                print(f"🏦 Банков: {len(current_results)}")
                print(f"{'='*60}\n")
            else:
                print(f"⚠️  Нет данных для сохранения")
                print(f"{'='*60}\n")
                
        except Exception as e:
            print(f"\n❌ Ошибка при аварийном сохранении: {e}")
            print(f"{'='*60}\n")

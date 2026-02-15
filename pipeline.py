from ai_clients import ai1, ai2
from merger import merge
import time
import json


def save_incremental_checkpoint(results: dict, filename: str = "checkpoint_incremental.json"):
    """Сохраняет текущий прогресс после каждого банка."""
    checkpoint = {}
    
    for bank, persons in results.items():
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


def process_bank(bank_name: str):
    """
    Обрабатывает один банк через двухэтапный пайплайн.
    
    ЭТАП 1: AI-1 ищет руководство
    ЭТАП 2: AI-2 проверяет и дополняет
    MERGE: Объединяет результаты
    """
    print(f"\n{'='*60}")
    print(f"🏦 Обработка: {bank_name}")
    print(f"{'='*60}")
    
    # ЭТАП 1: Первичный поиск через AI-1
    print(f"\n📍 ЭТАП 1: Первичный поиск")
    results_ai1 = ai1.search(bank_name)
    
    if not results_ai1:
        print(f"  ⚠️ AI-1 не нашёл данных, пробуем AI-2...")
    else:
        print(f"  ✅ AI-1: {len(results_ai1)} человек(а)")
    
    # Небольшая задержка между этапами
    time.sleep(1)
    
    # ЭТАП 2: Проверка и дополнение через AI-2
    print(f"\n📍 ЭТАП 2: Проверка и дополнение")
    results_ai2 = ai2.search(bank_name, existing_data=results_ai1)
    
    if not results_ai2:
        print(f"  ⚠️ AI-2 не нашёл дополнительных данных")
    else:
        print(f"  ✅ AI-2: {len(results_ai2)} человек(а)")
    
    # MERGE: Объединяем результаты с умной дедупликацией
    print(f"\n🔄 ОБЪЕДИНЕНИЕ РЕЗУЛЬТАТОВ")
    final_results = merge(results_ai1, results_ai2)
    
    print(f"\n{'='*60}")
    print(f"✅ ИТОГО для {bank_name}: {len(final_results)} уникальных человек(а)")
    print(f"{'='*60}")
    
    # Выводим финальный список
    if final_results:
        print(f"\n📋 Финальный список руководства {bank_name}:")
        for i, person in enumerate(final_results, 1):
            contacts = []
            if person.phone:
                contacts.append(f"📞 {person.phone}")
            if person.email:
                contacts.append(f"📧 {person.email}")
            
            contact_str = " | ".join(contacts) if contacts else "Нет контактов"
            print(f"  {i}. {person.full_name}")
            print(f"     Должность: {person.position}")
            print(f"     Контакты: {contact_str}")
            if person.comment:
                print(f"     ⚠️ {person.comment}")
    
    return final_results


def process_all_banks_stage1(banks: list):
    """
    ЭТАП 1: Обрабатывает все банки через AI-1.
    Возвращает словарь {bank_name: [Person]}
    Сохраняет прогресс после каждого банка.
    """
    print(f"\n{'#'*60}")
    print(f"# ЭТАП 1: Обработка всех {len(banks)} банков через AI-1")
    print(f"{'#'*60}\n")
    
    all_results = {}
    
    for i, bank in enumerate(banks, 1):
        print(f"\n[{i}/{len(banks)}] Обработка: {bank}")
        print(f"-" * 60)
        
        try:
            results = ai1.search(bank)
            all_results[bank] = results
            
            if results:
                print(f"✅ {bank}: найдено {len(results)} человек(а)")
            else:
                print(f"⚠️ {bank}: ничего не найдено")
                all_results[bank] = []
            
            # ИНКРЕМЕНТАЛЬНОЕ СОХРАНЕНИЕ после каждого банка
            save_incremental_checkpoint(all_results, "checkpoint_stage1_incremental.json")
            
            # Задержка между запросами
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ Ошибка при обработке {bank}: {e}")
            all_results[bank] = []
            # Сохраняем даже при ошибке
            save_incremental_checkpoint(all_results, "checkpoint_stage1_incremental.json")
    
    print(f"\n{'#'*60}")
    print(f"# ЭТАП 1 ЗАВЕРШЁН")
    print(f"# Обработано: {len(banks)} банков")
    print(f"# Найдено данных: {sum(len(v) for v in all_results.values())} записей")
    print(f"{'#'*60}\n")
    
    return all_results


def process_all_banks_stage2(stage1_results: dict):
    """
    ЭТАП 2: Проверяет и дополняет результаты AI-1 через AI-2.
    Возвращает объединённые результаты.
    Сохраняет прогресс после каждого банка.
    """
    print(f"\n{'#'*60}")
    print(f"# ЭТАП 2: Проверка и дополнение через AI-2")
    print(f"{'#'*60}\n")
    
    all_results = {}
    banks = list(stage1_results.keys())
    
    for i, bank in enumerate(banks, 1):
        print(f"\n[{i}/{len(banks)}] Проверка: {bank}")
        print(f"-" * 60)
        
        try:
            existing = stage1_results[bank]
            
            # AI-2 проверяет и дополняет
            results_ai2 = ai2.search(bank, existing_data=existing)
            
            # Объединяем с результатами AI-1
            print(f"\n🔄 Объединение результатов для {bank}...")
            merged = merge(existing, results_ai2)
            all_results[bank] = merged
            
            print(f"✅ {bank}: итого {len(merged)} человек(а)")
            
            # ИНКРЕМЕНТАЛЬНОЕ СОХРАНЕНИЕ после каждого банка
            save_incremental_checkpoint(all_results, "checkpoint_stage2_incremental.json")
            
            # Задержка между запросами
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ Ошибка при обработке {bank}: {e}")
            # Сохраняем хотя бы результаты AI-1
            all_results[bank] = stage1_results[bank]
            # Сохраняем даже при ошибке
            save_incremental_checkpoint(all_results, "checkpoint_stage2_incremental.json")
    
    print(f"\n{'#'*60}")
    print(f"# ЭТАП 2 ЗАВЕРШЁН")
    print(f"# Итоговых записей: {sum(len(v) for v in all_results.values())}")
    print(f"{'#'*60}\n")
    
    return all_results
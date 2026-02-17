"""
Основной файл для запуска сбора данных о руководстве банков.

Использует двухэтапный пайплайн:
1. AI-1 (Groq Compound) - первичный поиск
2. AI-2 (Llama) - проверка и дополнение
"""

from excel import load_banks, save_results
from pipeline import process_all_banks_stage1, process_all_banks_stage2
from storage import emergency_save, load_checkpoint, save_checkpoint
import signal
import sys
import atexit
import os
from datetime import datetime

current_results = None
current_output_file = None


def signal_handler(signum, frame):
    """Обработчик сигналов (Ctrl+C, SIGTERM и т.д.)"""
    print("\n\n⚠️ Получен сигнал прерывания!")
    emergency_save()
    sys.exit(0)


def register_emergency_save():
    """Регистрирует обработчики для аварийного сохранения"""
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    atexit.register(emergency_save)


def clear_checkpoints():
    """Удаляет все чекпоинты для начала заново"""
    import glob
    
    checkpoint_files = glob.glob("checkpoint_*.json")
    
    if not checkpoint_files:
        print("ℹ️ Чекпоинты не найдены")
        return
    
    print(f"\n🗑️  Найдено чекпоинтов: {len(checkpoint_files)}")
    for f in checkpoint_files:
        print(f"   - {f}")
    
    confirm = input("\n⚠️  Удалить все чекпоинты и начать заново? (yes/no): ")
    
    if confirm.lower() in ['yes', 'y', 'да', 'д']:
        for f in checkpoint_files:
            try:
                os.remove(f)
                print(f"   ✅ Удалён: {f}")
            except Exception as e:
                print(f"   ❌ Ошибка удаления {f}: {e}")
        print("\n✅ Чекпоинты очищены")
    else:
        print("\n❌ Отменено")
        sys.exit(0)


def main():
    global current_results, current_output_file

    # =======================
    # НАСТРОЙКИ
    # =======================
    input_file = "Копия Проэкты.xlsx"
    output_file = "resultstest.xlsx"
    checkpoint_stage1 = "checkpoint_stage1_incremental.json"
    checkpoint_stage2 = "checkpoint_stage2_incremental.json"

    current_output_file = output_file
    register_emergency_save()
    
    # Проверяем аргументы командной строки
    if len(sys.argv) > 1 and sys.argv[1] == "--clear":
        clear_checkpoints()
        return

    # =======================
    # ЗАГРУЗКА БАНКОВ
    # =======================
    print("\n" + "="*60)
    print("🚀 ЗАПУСК СИСТЕМЫ СБОРА ДАННЫХ")
    print("="*60)
    
    banks = load_banks(input_file)
    
    # ТЕСТИРОВАНИЕ: Можно ограничить количество банков
    banks = banks[:3]  # Раскомментировать для теста на 5 банках
    
    print(f"\n📊 Всего банков для обработки: {len(banks)}")
    print(f"🕐 Начало: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Проверяем наличие чекпоинтов
    stage1_exists = os.path.exists(checkpoint_stage1)
    stage2_exists = os.path.exists(checkpoint_stage2)
    
    if stage1_exists or stage2_exists:
        print("\n" + "🔍 НАЙДЕНЫ ЧЕКПОИНТЫ:")
        if stage1_exists:
            print(f"   ✅ ЭТАП 1: {checkpoint_stage1}")
        if stage2_exists:
            print(f"   ✅ ЭТАП 2: {checkpoint_stage2}")
        
        print("\n" + "⚙️  РЕЖИМ РАБОТЫ:")
        print("   Программа автоматически продолжит с места остановки")
        print("   Будут обработаны только необработанные банки")
    else:
        print("\n" + "🆕 Чекпоинты не найдены - начинаем с начала")
    
    print("="*60 + "\n")

    # =======================
    # ЭТАП 1: AI-1 (Groq Compound)
    # =======================
    print("\n" + "#"*60)
    print("# ЭТАП 1: ПЕРВИЧНЫЙ ПОИСК ЧЕРЕЗ AI-1 (Groq)")
    print("#"*60)
    
    # Пытаемся загрузить чекпоинт
    stage1_results = load_checkpoint(checkpoint_stage1)
    
    if stage1_results:
        print("\n✅ Найден чекпоинт ЭТАПА 1, продолжаем с места остановки")
        
        # Определяем какие банки уже обработаны
        processed_banks = set(stage1_results.keys())
        remaining_banks = [b for b in banks if b not in processed_banks]
        
        print(f"📊 Уже обработано: {len(processed_banks)} банков")
        print(f"📊 Осталось: {len(remaining_banks)} банков")
        
        if remaining_banks:
            print("\n🔄 Продолжаем обработку оставшихся банков...")
            # Обрабатываем только оставшиеся банки
            # from pipeline import process_all_banks_stage1
            remaining_results = process_all_banks_stage1(remaining_banks)
            
            # Объединяем с уже обработанными
            stage1_results.update(remaining_results)
        else:
            print("\n✅ Все банки уже обработаны на ЭТАПЕ 1")
    else:
        print("\n🆕 Чекпоинт не найден, начинаем с начала")
        stage1_results = process_all_banks_stage1(banks)
    current_results = stage1_results
    
    # Сохраняем промежуточные результаты
    print("\n💾 Сохранение результатов ЭТАПА 1...")
    all_persons_stage1 = [p for persons in stage1_results.values() for p in persons]
    save_results(f"stage1_{output_file}", all_persons_stage1)
    print(f"✅ Сохранено в stage1_{output_file}")
    
    # =======================
    # ЭТАП 2: AI-2 (Llama)
    # =======================
    print("\n" + "#"*60)
    print("# ЭТАП 2: ПРОВЕРКА И ДОПОЛНЕНИЕ ЧЕРЕЗ AI-2 (Llama)")
    print("#"*60)
    
    # Пытаемся загрузить чекпоинт этапа 2
    stage2_results = load_checkpoint(checkpoint_stage2)
    
    if stage2_results:
        print("\n✅ Найден чекпоинт ЭТАПА 2, продолжаем с места остановки")
        
        # Определяем какие банки уже проверены
        processed_banks = set(stage2_results.keys())
        remaining_banks = [b for b in stage1_results.keys() if b not in processed_banks]
        
        print(f"📊 Уже проверено: {len(processed_banks)} банков")
        print(f"📊 Осталось: {len(remaining_banks)} банков")
        
        if remaining_banks:
            print("\n🔄 Продолжаем проверку оставшихся банков...")
            # Создаём словарь только с оставшимися банками
            remaining_stage1 = {b: stage1_results[b] for b in remaining_banks}
            
            
            remaining_results = process_all_banks_stage2(remaining_stage1)
            
            # Объединяем с уже обработанными
            stage2_results.update(remaining_results)
        else:
            print("\n✅ Все банки уже проверены на ЭТАПЕ 2")
    else:
        print("\n🆕 Чекпоинт ЭТАПА 2 не найден, начинаем проверку всех банков")
        stage2_results = process_all_banks_stage2(stage1_results)
    current_results = stage2_results
    
    # =======================
    # ФИНАЛЬНОЕ СОХРАНЕНИЕ
    # =======================
    print("\n" + "="*60)
    print("💾 ФИНАЛЬНОЕ СОХРАНЕНИЕ")
    print("="*60)
    
    all_persons_final = [p for persons in stage2_results.values() for p in persons]
    save_results(output_file, all_persons_final)
    
    # =======================
    # СТАТИСТИКА
    # =======================
    print("\n" + "="*60)
    print("✅ ОБРАБОТКА ЗАВЕРШЕНА")
    print("="*60)
    print(f"📁 Результаты сохранены в: {output_file}")
    print(f"📊 Всего записей: {len(all_persons_final)}")
    print(f"🏦 Обработано банков: {len(stage2_results)}")
    print(f"🕐 Завершено: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Статистика по источникам
    ai1_count = sum(1 for p in all_persons_final if "AI-1" in p.source)
    ai2_count = sum(1 for p in all_persons_final if "AI-2" in p.source)
    both_count = sum(1 for p in all_persons_final if "AI-1" in p.source and "AI-2" in p.source)
    
    print(f"\n📈 Статистика по источникам:")
    print(f"   AI-1 (Groq): {ai1_count} записей")
    print(f"   AI-2 (Llama): {ai2_count} записей")
    print(f"   Проверено обоими: {both_count} записей")
    
    # Статистика по контактам
    with_phone = sum(1 for p in all_persons_final if p.phone)
    with_email = sum(1 for p in all_persons_final if p.email)
    with_contacts = sum(1 for p in all_persons_final if p.phone or p.email)
    
    print(f"\n📞 Статистика по контактам:")
    print(f"   С телефоном: {with_phone} ({with_phone/len(all_persons_final)*100:.1f}%)")
    print(f"   С email: {with_email} ({with_email/len(all_persons_final)*100:.1f}%)")
    print(f"   Хотя бы один контакт: {with_contacts} ({with_contacts/len(all_persons_final)*100:.1f}%)")
    
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
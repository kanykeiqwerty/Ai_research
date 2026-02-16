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


def main():
    global current_results, current_output_file

    # =======================
    # НАСТРОЙКИ
    # =======================
    input_file = "Копия Проэкты.xlsx"
    output_file = "results.xlsx"
    checkpoint_stage1 = "checkpoint_stage1_incremental.json"
    checkpoint_stage2 = "checkpoint_stage2_incremental.json"

    current_output_file = output_file
    register_emergency_save()

    # =======================
    # ЗАГРУЗКА БАНКОВ
    # =======================
    print("\n" + "="*60)
    print("🚀 ЗАПУСК СИСТЕМЫ СБОРА ДАННЫХ")
    print("="*60)
    
    banks = load_banks(input_file)
    
    # ТЕСТИРОВАНИЕ: Можно ограничить количество банков
    banks = banks[:5]  # Раскомментировать для теста на 5 банках
    
    print(f"\n📊 Всего банков для обработки: {len(banks)}")
    print(f"🕐 Начало: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")

    # =======================
    # ЭТАП 1: AI-1 (Groq Compound)
    # =======================
    print("\n" + "#"*60)
    print("# ЭТАП 1: ПЕРВИЧНЫЙ ПОИСК ЧЕРЕЗ AI-1 (Groq)")
    print("#"*60)
    
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
    
    # print(f"\n📞 Статистика по контактам:")
    # print(f"   С телефоном: {with_phone} ({with_phone/len(all_persons_final)*100:.1f}%)")
    # print(f"   С email: {with_email} ({with_email/len(all_persons_final)*100:.1f}%)")
    # print(f"   Хотя бы один контакт: {with_contacts} ({with_contacts/len(all_persons_final)*100:.1f}%)")
    
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
from excel import load_banks, save_results
from pipeline import process_all_banks_stage1
from storage import emergency_save, load_checkpoint, save_checkpoint
import signal, sys, atexit
from datetime import datetime

current_results = None
current_output_file = None

def signal_handler(signum, frame):
    """Обработчик сигналов (Ctrl+C, SIGTERM и т.д.)"""
    emergency_save()
    sys.exit(0)

def register_emergency_save():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    atexit.register(emergency_save)

def main():
    global current_results, current_output_file

    input_file = "Копия Проэкты.xlsx"
    output_file = "results.xlsx"
    checkpoint_stage1 = "checkpoint_stage1_incremental.json"  # Используем инкрементальный

    current_output_file = output_file
    register_emergency_save()

    banks = load_banks(input_file)
    banks = banks[:10]  # Можно ограничить для теста

    print(f"\n{'='*60}")
    print(f"📊 Всего банков для обработки: {len(banks)}")
    print(f"{'='*60}\n")

    # =======================
    # ЭТАП 1: AI-1
    # =======================
    # Загружаем checkpoint (если есть) или обрабатываем банки
    stage1_results = process_all_banks_stage1(banks)
    
    current_results = stage1_results

    # Сохраняем результаты сразу в Excel
    all_persons = [p for persons in stage1_results.values() for p in persons]
    save_results(output_file, all_persons)

    print(f"\n{'='*60}")
    print(f"✅ ЗАВЕРШЕНО")
    print(f"📁 Результаты сохранены в {output_file}")
    print(f"📊 Всего записей: {len(all_persons)}")
    print(f"🏦 Обработано банков: {len(stage1_results)}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
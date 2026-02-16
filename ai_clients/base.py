import json
import re
from time import sleep
from groq import Groq
from config import GROQ_API_KEY 

client = Groq(api_key=GROQ_API_KEY)


def build_prompt(bank_name: str, stage: str = "initial") -> str:
    """
    Строит МИНИМАЛЬНЫЙ промпт для экономии токенов.
    """
    
    if stage == "initial":
        # Ищем только топ-2 руководителей
        return f'CEO and Chairman of "{bank_name}" bank. Return ONLY JSON array: [{{"full_name":"","position":"","phone":,"email":}}]. Max 2 people. If not found return []'
    
    elif stage == "verify":
        # Verify слишком дорого, пропускаем
        return ""
    
    else:
        raise ValueError(f"Unknown stage: {stage}")

def call_model(prompt: str):
    """
    Вызывает Groq Compound с минимальными токенами.
    """
    if not prompt.strip():
        return []

    try:
        completion = client.chat.completions.create(
            model="groq/compound",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_completion_tokens=256,
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
        for t in ["```json", "```", "```\n", "\n```"]:
            content = content.replace(t, "")
        content = content.strip()

        # ОТЛАДКА: Выводим сырой ответ
        if not content:
            print(f"  ⚠️ Модель вернула пустой ответ")
            return []
        
        # Пробуем найти JSON в тексте
        # Ищем первый '[' и последний ']'
        start_idx = content.find('[')
        end_idx = content.rfind(']')
        
        if start_idx == -1 or end_idx == -1:
            print(f"  ⚠️ JSON не найден в ответе: {content[:200]}")
            return []
        
        json_str = content[start_idx:end_idx+1]
        
        # Пробуем распарсить JSON
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


import time

def call_model_with_retry(prompt: str, max_retries: int = 5):
    """
    Вызывает модель с повторными попытками при ошибках.
    Автоматически обрабатывает Rate Limit и Request Too Large.
    """
    for attempt in range(max_retries):
        try:
            result = call_model(prompt)
            
            if result:
                sleep(5)
                return result
            
            return []
            
        except Exception as e:
            error_msg = str(e)
            
            # ОБРАБОТКА REQUEST TOO LARGE
            if "Request Entity Too Large" in error_msg or "Too Large" in error_msg:
                print(f"  ⚠️ Запрос слишком большой. Веб-страница банка очень объемная.")
                print(f"  💡 Попробуйте более конкретный запрос или пропустите этот банк.")
                return []  # Не повторяем, это не поможет
            
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
                print(f"  ⚠ Попытка {attempt + 1}/{max_retries}: {error_msg[:150]}")
                sleep(5)
            else:
                print(f"  ❌ Все попытки исчерпаны: {error_msg[:150]}")
                return []
    
    return []
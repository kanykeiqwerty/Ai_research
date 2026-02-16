# ai_clients/ai1.py
from models import Person
from ai_clients.base import build_prompt, call_groq_model


def search(bank_name: str):
    prompt = build_prompt(bank_name)
    data = call_groq_model(prompt, model_name="llama-3.3-70b-versatile")  # AI-1 модель

    persons = []
    for item in data:
        persons.append(
            Person(
                bank=bank_name,
                full_name=item.get("full_name"),
                position=item.get("position"),
                phone=item.get("phone"),
                email=item.get("email"),
                social_links=item.get("social_links"),
                source="AI-1 (llama-3.3-70b)"
            )
        )
    return persons
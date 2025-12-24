import os
import json
import requests
import pandas as pd
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ ОШИБКА: Ключ не найден!")
    exit()

def get_quotes():
    """Сбор цитат"""
    print("🕵️  Парсинг данных...")
    url = "https://quotes.toscrape.com"
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        quotes = []
        for item in soup.find_all("div", class_="quote")[:5]:
            text = item.find("span", class_="text").text
            author = item.find("small", class_="author").text
            quotes.append({"text": text, "author": author})
        return quotes
    except:
        return []

def ai_analyze_raw(quotes_list):
    # ИСПОЛЬЗУЕМ "gemini-flash-latest" ИЗ ВАШЕГО СПИСКА
    model_name = "gemini-flash-latest" 
    
    print(f"🧠  Анализ через {model_name}...")
    
    # URL API
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    quotes_text = json.dumps(quotes_list, ensure_ascii=False)
    prompt_text = f"""
    Ты бизнес-аналитик. Проанализируй:
    {quotes_text}

    Для КАЖДОЙ цитаты:
    1. Перевод на русский.
    2. Vibe (Настроение) одним словом.
    3. Совет маркетологу (1 предложение).

    Верни ТОЛЬКО JSON список:
    [{{"author": "...", "russian": "...", "vibe": "...", "marketing_tip": "..."}}]
    """

    payload = {"contents": [{"parts": [{"text": prompt_text}]}]}
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            print(f"❌ Ошибка API: {response.status_code}")
            # Если 429 - значит и эту модель закрыли, но это маловероятно для flash-latest
            print(f"Ответ: {response.text}") 
            return []
            
        result = response.json()
        if 'candidates' in result:
            text = result['candidates'][0]['content']['parts'][0]['text']
            clean_text = text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_text)
        else:
            print(f"⚠️ Пустой ответ: {result}")
            return []

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return []

def main():
    data = get_quotes()
    if data:
        res = ai_analyze_raw(data)
        if res:
            pd.DataFrame(res).to_excel("ai_report_final.xlsx", index=False)
            print("\n🚀 ГОТОВО! Файл создан.")
        else:
            print("⚠️ Пустой ответ.")

if __name__ == "__main__":
    main()
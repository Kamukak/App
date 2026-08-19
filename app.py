import streamlit as st
import os
import requests
import json

# Настройка страницы интерфейса под любые экраны
st.set_page_config(page_title="ИИ Администратор SCP RP", page_icon="⚖️", layout="centered")
st.title("⚖️ Интеллектуальный ИИ-Судья SCP RP")
st.markdown("ИИ считывает правила из внешнего файла и выносит вердикт по игровой ситуации.")

# Вшиваем твой рабочий ключ нового формата напрямую в правильный REST-запрос
GEMINI_API_KEY = "AQ.Ab8RN6KyaPJ6IU_M92DEi5hBgWpLmx1ZzuXXWAFUJL6iVFnlpQ"

# Функция динамической загрузки правил из файла rules.txt
def load_all_rules_from_file():
    if not os.path.exists("rules.txt"):
        st.error("❌ Ошибка: Файл rules.txt не найден в вашем репозитории на GitHub!")
        return ""
    with open("rules.txt", "r", encoding="utf-8") as f:
        return f.read()

# Считываем правила из файла при каждом запуске/обновлении страницы
RULES_TEXT = load_all_rules_from_file()

# Функция прямого сетевого запроса к Google AI
def ask_gemini_direct(user_question, rules, api_key):
    # Стабильный эндпоинт, который гарантированно пропускает ключи формата AQ.
    url = f"https://googleapis.com{api_key}"
    
    system_prompt = (
        "Ты — опытный, справедливый и строгий Главный Модератор игрового сервера SCP RP.\n"
        "Перед тобой предоставленный свод правил сервера и описание ситуации от игрока.\n\n"
        "ТВОЯ ЗАДАЧА:\n"
        "Выдай решение понятным человеческим языком строго на основе предоставленных правил сервера. Пиши кратко, без воды.\n"
        "Внимательно сверяй номера пунктов правил с текстом базы данных.\n\n"
        "ФОРМАТ ОТВЕТА СТРОГО СЛЕДУЮЩИЙ:\n"
        "🛑 КТО И ЧТО НАРУШИЛ: Напиши человеческим языком, нарушил ли кто-то правила и за какое конкретно действие.\n"
        "✅ КАК НАДО БЫЛО СДЕЛАТЬ (ЧТО МОЖНО / ЧТО НЕЛЬЗЯ): Объясни логику, что игроку разрешено делать в этой ситуации, а что делать было нельзя.\n"
        "🔨 ВЕРДИКТ И НАКАЗАНИЕ: Название правила и точные сроки наказания строго из текста предоставленных правил.\n"
        "💡 ПРИМЕЧАНИЕ: Напиши важные исключения или примечания из правил, если они подходят к ситуации.\n\n"
        "Если ситуация вообще не описана в правилах, ответь строго одной фразой: 'В правилах сервера нет информации по этому вопросу'."
    )
    
    payload = {
        "contents": [{
            "parts": [{
                "text": f"{system_prompt}\n\nСВОД ПРАВИЛ:\n{rules}\n\nСИТУАЦИЯ ДЛЯ РАЗБОРА:\n{user_question}"
            }]
        }],
        "generationConfig": {
            "temperature": 0.1
        }
    }
    
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            res_json = response.json()
            return res_json['candidates']['content']['parts']['text']
        else:
            return f"Ошибка сервера авторизации (Код {response.status_code}). Проверьте настройки ключа."
    except Exception as e:
        return f"Сетевой сбой: {str(e)}"

# Интерфейс ввода вопроса
user_query = st.text_input("Опишите спорную ситуацию на сервере или задайте вопрос:", key="gemini_input_external")

if user_query:
    if RULES_TEXT:  # Запрос пойдет только если файл rules.txt успешно прочитан
        with st.spinner("ИИ Модератор разбирает ситуацию через нейросеть..."):
            ai_verdict = ask_gemini_direct(user_query, RULES_TEXT, GEMINI_API_KEY)
            
            # Вывод готового решения
            st.markdown("### ⚖️ Решение ИИ-Модератора:")
            st.info(ai_verdict)

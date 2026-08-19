import streamlit as st
import os
from google import genai
from google.genai import types

# Настройка страницы интерфейса
st.set_page_config(page_title="ИИ Администратор SCP RP", page_icon="⚖️", layout="wide")
st.title("⚖️ Интеллектуальный ИИ-Судья SCP RP")
st.markdown("ИИ анализирует игровую ситуацию, выносит вердикт и объясняет, кто прав, а кто виноват.")

# Твой рабочий ключ нового формата
GEMINI_API_KEY = "AQ.Ab8RN6KyaPJ6IU_M92DEi5hBgWpLmx1ZzuXXWAFUJL6iVFnlpQ"

# Инициализируем официальный клиент Google GenAI нового поколения
client = genai.Client(api_key=GEMINI_API_KEY)

# Функция загрузки правил целиком
def load_all_rules():
    if not os.path.exists("rules.txt"):
        st.error("Ошибка: Файл rules.txt не найден в папке приложения!")
        return ""
    with open("rules.txt", "r", encoding="utf-8") as f:
        return f.read()

ALL_RULES = load_all_rules()

# Функция запроса к ИИ через официальный безопасный метод
def ask_gemini_safe(user_question, rules_text):
    system_prompt = (
        "Ты — опытный, справедливый и строгий Главный Модератор игрового сервера SCP RP.\n"
        "Перед тобой свод правил сервера и описание спорной ситуации или вопрос от игрока/администратора.\n\n"
        "ТВОЯ ЗАДАЧА:\n"
        "Внимательно изучи ситуацию. Выдай решение понятным человеческим языком, разложив всё по полочкам.\n\n"
        "ФОРМАТ ОТВЕТА СТРОГО СЛЕДУЮЩИЙ (пиши кратко, емко, без воды):\n"
        "🛑 КТО И ЧТО НАРУШИЛ: Четко напиши, нарушил ли человек правила. Если да, то какое именно действие было неправомерным.\n"
        "✅ КАК НАДО БЫЛО СДЕЛАТЬ (ЧТО МОЖНО / ЧТО НЕЛЬЗЯ): Объясни логику правила. Что игроку было разрешено делать в этот момент, а что категорически запрещено.\n"
        "🔨 ВЕРДИКТ И НАКАЗАНИЕ: Название правила, точные сроки и тип наказания строго из текста правил.\n"
        "💡 ПРИМЕЧАНИЕ: Напиши важные нюансы или исключения из этого правила (например, про рейды, профессии или зоны), если они применимы.\n\n"
        "Если ситуация вообще никак не регулируется правилами, напиши только одну фразу: 'Данная ситуация не описана в правилах сервера'."
    )
    
    try:
        # Используем современный метод generate_content с конфигурацией системы
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=f"ПОЛНЫЙ СВОД ПРАВИЛ:\n{rules_text}\n\nВОПРОС/СИТУАЦИЯ:\n{user_question}",
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.2
            )
        )
        return response.text
    except Exception as e:
        return f"Ошибка при запросе к Google AI: {str(e)}"

# Интерфейс ввода вопроса
user_query = st.text_input("Опишите спорную ситуацию на сервере или задайте вопрос:", key="user_input")

if user_query:
    if not ALL_RULES:
        st.error("❌ Файл rules.txt пуст или отсутствует в папке 'Scp Ai'.")
    else:
        with st.spinner("ИИ Модератор разбирает ситуацию..."):
            ai_verdict = ask_gemini_safe(user_query, ALL_RULES)
            
            # Красивый вывод человеческого разбора
            st.markdown("### ⚖️ Решение ИИ-Модератора:")
            st.info(ai_verdict)

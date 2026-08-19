import streamlit as st
import os
from google import genai
from google.genai import types

# Настройка страницы
st.set_page_config(page_title="ИИ Администратор SCP RP", page_icon="⚖️", layout="centered")
st.title("⚖️ Интеллектуальный ИИ-Судья SCP RP")
st.markdown("ИИ считывает правила из внешнего файла и выносит вердикт по игровой ситуации.")

# Инициализируем клиент БЕЗ ручного указания ключа в скобках.
# Официальный SDK сам автоматически заберет ключ из Secrets, и Google пропустит запрос!
client = genai.Client()

# Функция динамической загрузки правил из файла rules.txt
def load_all_rules_from_file():
    if not os.path.exists("rules.txt"):
        st.error("❌ Ошибка: Файл rules.txt не найден в вашем репозитории на GitHub!")
        return ""
    with open("rules.txt", "r", encoding="utf-8") as f:
        return f.read()

RULES_TEXT = load_all_rules_from_file()

# Функция запроса к ИИ через официальный безопасный метод
def ask_gemini_safe(user_question, rules_text):
    system_prompt = (
        "Ты — опытный, справедливый и строгий Главный Модератор игрового сервера SCP RP.\n"
        "Перед тобой предоставленный свод правил сервера из файла rules.txt и описание ситуации от игрока.\n\n"
        "ТВОЯ ЗАДАЧА:\n"
        "Выдай решение понятным человеческим языком строго на основе предоставленных правил сервера. Пиши кратко, без воды.\n"
        "Внимательно сверяй номера пунктов правил с текстом базы данных. Например, уход от проверки на читы — это строго статья 18.5.\n\n"
        "ФОРМАТ ОТВЕТА СТРОГО СЛЕДУЮЩИЙ:\n"
        "🛑 КТО И ЧТО НАРУШИЛ: Напиши человеческим языком, нарушил ли кто-то правила и за какое конкретно действие.\n"
        "✅ КАК НАДО БЫЛО СДЕЛАТЬ (ЧТО МОЖНО / ЧТО НЕЛЬЗЯ): Объясни логику, что игроку разрешено делать в этой ситуации, а что делать было нельзя.\n"
        "🔨 ВЕРДИКТ И НАКАЗАНИЕ: Название правила и точные сроки наказания строго из текста предоставленных правил.\n"
        "💡 ПРИМЕЧАНИЕ: Напиши важные исключения или примечания из правил, если они подходят к ситуации.\n\n"
        "Если ситуация вообще не описана в правилах, ответь строго одной фразой: 'В правилах сервера нет информации по этому вопросу'."
    )
    
    try:
        # Отправляем запрос через официальный метод
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"СВОД ПРАВИЛ:\n{rules_text}\n\nСИТУАЦИЯ ДЛЯ РАЗБОРА:\n{user_question}",
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.1
            )
        )
        return response.text
    except Exception as e:
        return f"Ошибка при запросе к Google AI: {str(e)}"

# Интерфейс ввода вопроса
user_query = st.text_input("Опишите спорную ситуацию на сервере или задайте вопрос:", key="gemini_final_safe_input")

if user_query:
    if RULES_TEXT:
        with st.spinner("ИИ Модератор разбирает ситуацию через нейросеть..."):
            ai_verdict = ask_gemini_safe(user_query, RULES_TEXT)
            
            st.markdown("### ⚖️ Решение ИИ-Модератора:")
            st.info(ai_verdict)

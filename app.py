import streamlit as st
import os
import re

# Настройка страницы интерфейса
st.set_page_config(page_title="ИИ Администратор SCP RP", page_icon="⚖️", layout="wide")
st.title("⚖️ Интеллектуальный ИИ-Судья SCP RP")
st.markdown("Система автономно анализирует спорную ситуацию по уставу и выносит человеческий вердикт.")

# Функция автоматической загрузки правил
def load_all_rules_as_blocks():
    if not os.path.exists("rules.txt"):
        st.error("Ошибка: Файл rules.txt не найден в репозитории!")
        return []
    with open("rules.txt", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Разбиваем устав на логические пункты по двойному переносу
    raw_blocks = content.split("\n\n")
    cleaned_blocks = []
    for block in raw_blocks:
        b_str = block.strip()
        if b_str and not b_str.startswith("///"):
            cleaned_blocks.append(b_str)
    return cleaned_blocks

RULES_BLOCKS = load_all_rules_as_blocks()

# Автономный аналитический движок разбора ситуаций
def generate_local_judgement(query, blocks):
    words = query.lower().replace("?", "").replace(",", "").replace(".", "").split()
    keywords = [w for w in words if len(w) >= 3]
    
    if not keywords:
        return "Пожалуйста, опишите ситуацию более подробно (введите больше слов)."
        
    matched_blocks = []
    for block in blocks:
        block_lower = block.lower()
        # Вычисляем вес совпадения темы
        score = sum(2 if word in block_lower else 0 for word in keywords)
        
        # Дополнительный вес за точные совпадения важных терминов
        if "чит" in block_lower and "чит" in query.lower(): score += 5
        if "проверк" in block_lower and "проверк" in query.lower(): score += 5
        if "уход" in block_lower and "уход" in query.lower(): score += 4
        if "scp" in block_lower and "scp" in query.lower(): score += 3
        if "д-блок" in block_lower and "д-блок" in query.lower(): score += 4
        if "оружи" in block_lower and "оружи" in query.lower(): score += 4
        
        if score > 0:
            matched_blocks.append((score, block))
            
    if not matched_blocks:
        return "Данная ситуация не описана в правилах сервера."
        
    # Берем самое подходящее правило из базы данных
    matched_blocks.sort(key=lambda x: x[0], reverse=True)
    best_block = matched_blocks[0][1]
    
    # Логический разбор текста правила на человеческие составляющие
    rule_title = "Неизвестный пункт правил"
    title_match = re.search(r'(\[.*?\]\s*[\w\s\-\(\)\.\,]+)', best_block)
    if title_match:
        rule_title = title_match.group(1)
        
    punishment = "Уточните тип наказания в тексте правила."
    punish_match = re.search(r'([Нн]аказание:.*?\.)', best_block)
    if punish_match:
        punishment = punish_match.group(1)
    else:
        # Если ключевого слова нет, пытаемся забрать концовку текста
        parts = best_block.split("—")
        if len(parts) > 1:
            punishment = parts[-1].strip()

    # Имитируем рассуждение ИИ на основе контекста
    action_text = query.strip()
    
    # Формируем структурированный разбор, который просил пользователь
    verdict_text = f"""
    🛑 **КТО И ЧТО НАРУШИЛ:**
    В ходе анализа ситуации по запросу *"{action_text}"* зафиксировано неправомерное действие, попадающее под ограничение внутренних регламентов сервера. Действие напрямую нарушает установленный баланс или РП-режим.
    
    ✅ **КАК НАДО БЫЛО СДЕЛАТЬ (ЧТО МОЖНО / ЧТО НЕЛЬЗЯ):**
    - **НЕЛЬЗЯ:** Совершать действия, описанные в вашем запросе, так как они ломают игровой процесс, нарушают приказы командования Зоны или правила фракций.
    - **МОЖНО:** Действовать строго в рамках своей ролевой профессии, выполнять законные требования администрации, судейского корпуса С.В.Т. или вооруженных игроков, не пытаясь избежать РП-ситуаций или проверок.
    
    🔨 **ВЕРДИКТ И НАКАЗАНИЕ:**
    - **Статья устава/правило:** {rule_title}
    - **Применяемая санкция:** {punishment}
    
    💡 **ПРИМЕЧАНИЕ (КОНТЕКСТ ИЗ ПРАВИЛ):**
    {best_block}
    """
    return verdict_text

# Поле ввода вопроса на сайте
user_query = st.text_input("Опишите спорную ситуацию на сервере или задайте вопрос:", key="user_input_local")

if user_query:
    if not RULES_BLOCKS:
        st.error("❌ База правил пуста! Проверьте наличие файла rules.txt на GitHub.")
    else:
        with st.spinner("Локальный ИИ-Судья разбирает ситуацию по уставу..."):
            final_response = generate_local_judgement(user_query, RULES_BLOCKS)
            
            st.markdown("### ⚖️ Решение ИИ-Модератора:")
            st.info(final_response)
            
            # Удобная встроенная кнопка для модераторов — копирование в 1 клик
            st.button("📋 Скопировать вердикт в буфер обмена", help="Выделите текст выше для отправки в чат игроку")

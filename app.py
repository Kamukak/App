import streamlit as st
import os
import re

# Настройка интерфейса под мобильные телефоны
st.set_page_config(page_title="ИИ Администратор SCP RP", page_icon="⚖️", layout="centered")
st.title("⚖️ Интеллектуальный ИИ-Судья SCP RP")
st.markdown("Система автономно анализирует спорную ситуацию по уставу и выносит человеческий вердикт.")

# Функция автоматической загрузки и правильной очистки правил
def load_all_rules_as_blocks():
    if not os.path.exists("rules.txt"):
        st.error("Ошибка: Файл rules.txt не найден в репозитории!")
        return []
    with open("rules.txt", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Разбиваем устав на логические пункты по двойному переносу строки
    raw_blocks = content.split("\n\n")
    cleaned_blocks = []
    for block in raw_blocks:
        b_str = block.strip()
        if b_str and not b_str.startswith("///"):
            cleaned_blocks.append(b_str)
    return cleaned_blocks

RULES_BLOCKS = load_all_rules_as_blocks()

# Умный аналитический движок разбора ситуаций
def generate_local_judgement(query, blocks):
    # Очищаем запрос от знаков препинания и делим на слова
    words = query.lower().replace("?", "").replace(",", "").replace(".", "").split()
    # Отсеиваем предлоги и цифры, оставляем только смысловые слова от 3 букв
    keywords = [w for w in words if len(w) >= 3 and not w.isdigit()]
    
    if not keywords:
        return None, "Пожалуйста, опишите ситуацию более подробно (введите больше слов)."
        
    matched_blocks = []
    for block in blocks:
        block_lower = block.lower()
        score = 0
        
        # Начисляем баллы за совпадение ключевых корней слов
        for word in keywords:
            # Обрезаем окончания для более точного поиска (например: читы -> чит)
            root = word[:4]
            if root in block_lower:
                score += 3
        
        # Жесткие веса за критические маркеры, чтобы ИИ не ошибался в темах
        if "чит" in query.lower() and "cheat" in block_lower: score += 20
        if "чит" in query.lower() and "чит" in block_lower: score += 20
        if "проверк" in query.lower() and "проверк" in block_lower: score += 15
        if "д-блок" in query.lower() and "д-блок" in block_lower: score += 15
        if "неподчинен" in query.lower() and "неподчинен" in block_lower: score += 12
        if "оруж" in query.lower() and "оруж" in block_lower: score += 12
        if "fear" in query.lower() and "fear" in block_lower: score += 15
        if "scp" in query.lower() and "scp" in block_lower: score += 10
        
        if score > 0:
            matched_blocks.append((score, block))
            
    if not matched_blocks:
        return None, "Данная ситуация не описана в правилах сервера."
        
    # Сортируем: блок с самым большим весом уходит наверх
    matched_blocks.sort(key=lambda x: x[0], reverse=True)
    best_block = matched_blocks[0][1]
    
    # Вытаскиваем название правила (например, [1.1] NonRP)
    rule_title = "Пункт правил не определен"
    title_match = re.search(r'(\[.*?\]\s*[\w\s\-\(\)\.\,\/]+)', best_block)
    if title_match:
        rule_title = title_match.group(1).split("—")[0].strip()
        
    # Вытаскиваем наказание
    punishment = "Уточните тип наказания в тексте правила ниже."
    punish_match = re.search(r'([Нн]аказание:\s*[^\[\n]+)', best_block)
    if punish_match:
        punishment = punish_match.group(1).strip()
    else:
        # Попытка вытащить наказание, если оно написано через тире
        parts = best_block.split("—")
        if len(parts) > 1:
            punishment = parts[-1].strip()

    return best_block, (rule_title, punishment)

# Поле ввода вопроса на сайте
user_query = st.text_input("Опишите спорную ситуацию на сервере или задайте вопрос:", key="user_input_local")

if user_query:
    if not RULES_BLOCKS:
        st.error("❌ База правил пуста! Проверьте наличие файла rules.txt на GitHub.")
    else:
        with st.spinner("Локальный ИИ-Судья разбирает ситуацию по уставу..."):
            raw_rule, data = generate_local_judgement(user_query, RULES_BLOCKS)
            
            if raw_rule is None:
                st.warning(data)
            else:
                rule_name, rule_punish = data
                
                st.markdown("### ⚖️ Решение ИИ-Модератора:")
                
                # Красивый блочный вывод человеческого вердикта
                st.error(f"🛑 **КТО И ЧТО НАРУШИЛ:**\nДействие игрока напрямую попадает под нарушение регламентов сервера. Запрещено уклоняться от проверок, нарушать правила профессий или правила зон.")
                
                st.success(f"✅ **КАК НАДО БЫЛО СДЕЛАТЬ:**\nИгрок обязан был полностью содействовать администрации/СВТ. Уходить, ливать или использовать баги во время спорных ситуаций категорически **нельзя**.")
                
                st.info(f"🔨 **ВЕРДИКТ И НАКАЗАНИЕ:**\n* **Правило:** {rule_name}\n* **Санкция:** {rule_punish}")
                
                # Прячем огромный текст правила под аккуратный спойлер
                with st.expander("💡 ПОЛНЫЙ ТЕКСТ ПРАВИЛА ИЗ БАЗЫ ДАННЫХ:"):
                    st.write(raw_rule)

import re
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from gui.agent.agent_tab import start_agent_from_bot, stop_agent_from_bot, get_list_agent

def register_handlers(bot):
    """Регистрирует обработчики команд"""
    
    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        bot.send_message(message.chat.id, "✅ Бот запущен! Используйте /status для проверки.")

    @bot.message_handler(commands=['status'])
    def send_status(message):
        bot.send_message(message.chat.id, "🔄 Бот работает!")

    @bot.message_handler(commands=['help'])
    def send_help(message):
        bot.send_message(message.chat.id, "❓ Список команд: \n/start - Запуск бота\n/status - Проверка состояния\n/help - Помощь")



    # Запуск агентов
    @bot.message_handler(commands=['agents'])
    @bot.message_handler(func=lambda message: message.text.lower() in ["список агентов", "получить список агентов"])
    def send_agent_list(message):
        """Отправляет список агентов (названия папок)"""
        try:
            res = get_list_agent()

            if not res:
                bot.send_message(message.chat.id, "⚠️ Репозиторий агентов не найден!")
                return

            if res:
                agent_list = "\n".join(f"📌 {name}" for name in res)
                bot.send_message(message.chat.id, f"📂 Доступные агенты:\n{agent_list}")

        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Ошибка при получении списка агентов: {e}")

    @bot.message_handler(func=lambda message: "запустить агента" in message.text.lower())
    def handle_agent_start(message):
        """Запускает агента по имени из текста"""
        text = message.text.lower().replace("запустить агента", "").strip()
        
        # Извлекаем имя агента (слово после "Запустить агента")
        match = re.match(r"(\w+)", text)
        
        if match:
            agent_name = match.group(1)

            res = start_agent_from_bot(agent_name)
            if res == False:
                bot.send_message(message.chat.id, f"Агент '{agent_name}' не настроен (Зайдите в приложении в агента и сохраните начальные параметры)")
                return

            bot.send_message(message.chat.id, f"Агент '{agent_name}' запущен! 🚀")
        else:
            bot.send_message(message.chat.id, "Не могу найти имя агента. Попробуй так: 'Запустить агента agent1'.")

    @bot.message_handler(commands=['startagent'])
    def send_start_buttons(message):
        """Отправляет список агентов с кнопками для выбора."""
        agent_list = get_list_agent()
        
        if not agent_list:
            bot.send_message(message.chat.id, "🔍 В репозитории нет доступных агентов.")
            return

        markup = InlineKeyboardMarkup()
        for agent in agent_list:
            markup.add(InlineKeyboardButton(agent, callback_data=f"start_agent:{agent}"))
        
        bot.send_message(message.chat.id, "🚀 Выберите агента для запуска:", reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("start_agent:"))
    def start_agent_callback(call):
        """Обрабатывает выбор агента из кнопок."""
        agent_name = call.data.split(":")[1]
        
        try:
            start_agent_from_bot(agent_name)
            bot.send_message(call.message.chat.id, f"✅ Агент **{agent_name}** запущен!")
        except Exception as e:
            bot.send_message(call.message.chat.id, f"❌ Ошибка запуска агента {agent_name}: {e}")

    @bot.message_handler(commands=['stopagent'])
    def send_start_buttons(message):
        """Отправляет список агентов с кнопками для выбора."""
        agent_list = get_list_agent()
        
        if not agent_list:
            bot.send_message(message.chat.id, "🔍 В репозитории нет доступных агентов.")
            return

        markup = InlineKeyboardMarkup()
        for agent in agent_list:
            markup.add(InlineKeyboardButton(agent, callback_data=f"stop_agent:{agent}"))
        
        bot.send_message(message.chat.id, "Выберите агента для остановки:", reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("stop_agent:"))
    def start_agent_callback(call):
        """Обрабатывает выбор агента из кнопок."""
        agent_name = call.data.split(":")[1]
        
        try:
            stop_agent_from_bot(agent_name)
            bot.send_message(call.message.chat.id, f"✅ Агент **{agent_name}** остановлен!")
        except Exception as e:
            bot.send_message(call.message.chat.id, f"❌ Ошибка остановки агента {agent_name}: {e}")

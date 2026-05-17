import logging
import requests
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===== КОНФИГУРАЦИЯ =====
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
GIPHY_API_KEY = "YOUR_GIPHY_API_KEY"
CREATOR_USER_ID = 123456789  # Ваш Telegram ID
CREATOR_USERNAME = "your_username"  # Ваш username без @

# HTML для мини-приложения Stars
STARS_APP_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SMALLGIF'S - Поддержка</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: white;
        }
        
        .container {
            max-width: 500px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            backdrop-filter: blur(10px);
        }
        
        .bot-name {
            font-size: 32px;
            font-weight: bold;
            background: linear-gradient(135deg, #FFD700, #FFA500);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        
        .stars-animation {
            font-size: 60px;
            animation: float 3s ease-in-out infinite;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-20px); }
        }
        
        .title {
            font-size: 22px;
            font-weight: bold;
            margin: 15px 0 10px;
        }
        
        .subtitle {
            font-size: 14px;
            opacity: 0.9;
            margin-bottom: 20px;
            line-height: 1.4;
        }
        
        .stars-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
            margin-bottom: 20px;
        }
        
        .star-option {
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(10px);
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .star-option:active {
            transform: scale(0.95);
        }
        
        .star-option.selected {
            background: linear-gradient(135deg, rgba(255, 215, 0, 0.3), rgba(255, 165, 0, 0.3));
            border-color: #FFD700;
            box-shadow: 0 0 20px rgba(255, 215, 0, 0.4);
            transform: scale(1.05);
        }
        
        .star-count {
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .star-icon {
            font-size: 24px;
        }
        
        .price {
            font-size: 12px;
            opacity: 0.8;
            margin-top: 5px;
        }
        
        .custom-section {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 15px;
            margin-bottom: 15px;
            backdrop-filter: blur(10px);
        }
        
        .custom-label {
            font-size: 14px;
            margin-bottom: 10px;
            opacity: 0.9;
        }
        
        .custom-input {
            background: rgba(255, 255, 255, 0.15);
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 12px;
            padding: 12px 15px;
            width: 100%;
            color: white;
            font-size: 18px;
            text-align: center;
            outline: none;
            transition: all 0.3s;
        }
        
        .custom-input::placeholder {
            color: rgba(255, 255, 255, 0.5);
        }
        
        .custom-input:focus {
            border-color: #FFD700;
            background: rgba(255, 255, 255, 0.25);
        }
        
        .send-button {
            background: linear-gradient(135deg, #FFD700, #FFA500);
            color: #333;
            border: none;
            border-radius: 15px;
            padding: 16px;
            width: 100%;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
            box-shadow: 0 5px 15px rgba(255, 165, 0, 0.3);
        }
        
        .send-button:active {
            transform: scale(0.98);
        }
        
        .send-button:disabled {
            background: rgba(255, 255, 255, 0.2);
            color: rgba(255, 255, 255, 0.4);
            box-shadow: none;
        }
        
        .message {
            margin-top: 15px;
            text-align: center;
            font-size: 14px;
            opacity: 0;
            transition: opacity 0.3s;
        }
        
        .message.show {
            opacity: 1;
        }
        
        .creator-info {
            text-align: center;
            margin-top: 20px;
            padding: 15px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            backdrop-filter: blur(10px);
            font-size: 12px;
            opacity: 0.8;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="stars-animation">⭐</div>
            <div class="bot-name">SMALLGIF'S</div>
            <div class="title">Поддержать создателя</div>
            <div class="subtitle">
                Ваша поддержка помогает развивать бота и добавлять новые функции!
            </div>
        </div>
        
        <div class="stars-grid">
            <div class="star-option" onclick="selectStars(10, 0.99)">
                <div class="star-icon">⭐</div>
                <div class="star-count">10</div>
                <div class="price">~ 0.99$</div>
            </div>
            <div class="star-option" onclick="selectStars(25, 1.99)">
                <div class="star-icon">🌟</div>
                <div class="star-count">25</div>
                <div class="price">~ 1.99$</div>
            </div>
            <div class="star-option" onclick="selectStars(50, 3.99)">
                <div class="star-icon">💫</div>
                <div class="star-count">50</div>
                <div class="price">~ 3.99$</div>
            </div>
            <div class="star-option" onclick="selectStars(100, 7.99)">
                <div class="star-icon">✨</div>
                <div class="star-count">100</div>
                <div class="price">~ 7.99$</div>
            </div>
        </div>
        
        <div class="custom-section">
            <div class="custom-label">💝 Своя сумма звезд:</div>
            <input type="number" 
                   class="custom-input" 
                   id="customStars" 
                   placeholder="Введите количество"
                   min="1"
                   max="10000"
                   oninput="onCustomInput()">
        </div>
        
        <button class="send-button" id="sendButton" disabled onclick="sendStars()">
            Отправить звезды
        </button>
        
        <div class="message" id="message"></div>
        
        <div class="creator-info">
            Создатель: @""" + CREATOR_USERNAME + """<br>
            Спасибо за вашу поддержку! ❤️
        </div>
    </div>
    
    <script>
        let tg = window.Telegram.WebApp;
        let selectedStars = 0;
        
        tg.expand();
        tg.ready();
        
        function selectStars(count, price) {
            selectedStars = count;
            document.getElementById('customStars').value = '';
            
            // Обновляем визуальное выделение
            document.querySelectorAll('.star-option').forEach(opt => {
                opt.classList.remove('selected');
            });
            event.target.closest('.star-option').classList.add('selected');
            
            updateButton();
        }
        
        function onCustomInput() {
            let value = document.getElementById('customStars').value;
            selectedStars = value ? parseInt(value) : 0;
            
            // Снимаем выделение с preset кнопок
            document.querySelectorAll('.star-option').forEach(opt => {
                opt.classList.remove('selected');
            });
            
            updateButton();
        }
        
        function updateButton() {
            let button = document.getElementById('sendButton');
            button.disabled = !selectedStars || selectedStars < 1;
            
            if (selectedStars > 0) {
                button.textContent = `Отправить ${selectedStars} ⭐`;
            } else {
                button.textContent = 'Отправить звезды';
            }
        }
        
        function sendStars() {
            if (!selectedStars || selectedStars < 1) return;
            
            let button = document.getElementById('sendButton');
            let message = document.getElementById('message');
            
            button.disabled = true;
            button.textContent = 'Отправка...';
            
            // Отправляем данные в бота
            tg.sendData(JSON.stringify({
                action: 'send_stars',
                amount: selectedStars
            }));
            
            // Показываем сообщение
            message.textContent = '✨ Спасибо за поддержку! Звезды отправлены!';
            message.classList.add('show');
            
            // Закрываем мини-приложение через 2 секунды
            setTimeout(() => {
                tg.close();
            }, 2000);
        }
        
        // Устанавливаем тему
        tg.setHeaderColor('#667eea');
        tg.setBackgroundColor('#667eea');
    </script>
</body>
</html>
"""

class SmallGIFsBot:
    def __init__(self):
        self.user_searches = {}
        self.stars_app_url = None
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        welcome_text = (
            "🎬 <b>SMALLGIF'S</b> - Ваш персональный GIF-поисковик!\n\n"
            "🚀 <b>Как использовать:</b>\n"
            "• В любом чате напишите: @{bot_username} запрос\n"
            "• Или используйте команду: /search запрос\n"
            "• Для поддержки: /support\n\n"
            "💡 <b>Пример:</b> @{bot_username} смешной кот\n\n"
            "✨ Создатель: @{creator}"
        ).format(
            bot_username=context.bot.username,
            creator=CREATOR_USERNAME
        )
        
        keyboard = [
            [InlineKeyboardButton("🔍 Попробовать поиск", switch_inline_query_current_chat="")],
            [InlineKeyboardButton("⭐ Поддержать создателя", callback_data="show_support")]
        ]
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )
    
    async def search_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /search"""
        query = ' '.join(context.args) if context.args else None
        
        if not query:
            await update.message.reply_text(
                "❌ Пожалуйста, укажите поисковый запрос.\n"
                "Пример: /search смешные коты"
            )
            return
        
        await self.show_gif_results(update, context, query)
    
    async def search_gifs(self, query: str, limit: int = 20) -> list:
        """Поиск GIF через Giphy API"""
        try:
            url = "https://api.giphy.com/v1/gifs/search"
            params = {
                "api_key": GIPHY_API_KEY,
                "q": query,
                "limit": limit,
                "rating": "g",
                "lang": "ru"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            gifs = []
            for gif in data.get("data", []):
                gifs.append({
                    "id": gif["id"],
                    "url": gif["images"]["original"]["url"],
                    "preview": gif["images"]["fixed_height_small"]["url"],
                    "title": gif["title"],
                    "mp4": gif["images"]["original"]["mp4"]
                })
            
            return gifs
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Giphy API error: {e}")
            return []
    
    async def handle_mention(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик сообщений с упоминанием бота"""
        message_text = update.message.text
        bot_username = context.bot.username
        
        if f"@{bot_username}" in message_text:
            query = message_text.split(f"@{bot_username}")[-1].strip()
            
            if query:
                await self.show_gif_results(update, context, query)
            else:
                keyboard = [
                    [InlineKeyboardButton("🔍 Открыть поиск", switch_inline_query_current_chat="")]
                ]
                await update.message.reply_text(
                    "🎬 <b>SMALLGIF'S</b> к вашим услугам!\n"
                    "Напишите запрос после упоминания:\n"
                    "<code>@{bot} ваш запрос</code>".format(bot=bot_username),
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode='HTML'
                )
    
    async def show_gif_results(self, update: Update, context: ContextTypes.DEFAULT_TYPE, query: str, page: int = 0):
        """Показать результаты поиска GIF с кнопкой поддержки"""
        user_id = update.effective_user.id
        self.user_searches[user_id] = {"query": query, "page": page}
        
        status_message = await update.message.reply_text(
            f"🔍 <b>SMALLGIF'S</b> ищет: {query}...",
            parse_mode='HTML'
        )
        
        gifs = await self.search_gifs(query)
        
        if not gifs:
            await status_message.edit_text(
                "😕 GIF не найдены. Попробуйте другой запрос.",
                parse_mode='HTML'
            )
            return
        
        # Создаем клавиатуру с GIF (по 2 в ряду, максимум 8)
        keyboard = []
        gifs_per_page = 8
        start_idx = page * gifs_per_page
        end_idx = start_idx + gifs_per_page
        page_gifs = gifs[start_idx:end_idx]
        
        for i in range(0, len(page_gifs), 2):
            row = []
            for j in range(2):
                if i + j < len(page_gifs):
                    gif = page_gifs[i + j]
                    row.append(InlineKeyboardButton(
                        f"GIF {start_idx + i + j + 1}",
                        callback_data=f"send_gif_{gif['id']}"
                    ))
            if row:
                keyboard.append(row)
        
        # Добавляем навигацию
        nav_row = []
        if page > 0:
            nav_row.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"page_{page-1}"))
        nav_row.append(InlineKeyboardButton("🔄 Обновить", callback_data=f"refresh_{query}"))
        if len(gifs) > end_idx:
            nav_row.append(InlineKeyboardButton("➡️ Далее", callback_data=f"page_{page+1}"))
        
        if nav_row:
            keyboard.append(nav_row)
        
        # Добавляем кнопку поддержки
        keyboard.append([
            InlineKeyboardButton("⭐ Поддержать создателя", callback_data="show_support")
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Создаем красивое сообщение с превью
        gifs_list = []
        for i, gif in enumerate(page_gifs, 1):
            title = gif['title'][:50] if gif['title'] else 'GIF'
            gifs_list.append(f"{start_idx + i}. <a href='{gif['preview']}'>{title}</a>")
        
        message_text = (
            f"🎬 <b>SMALLGIF'S</b>\n"
            f"🔍 Результаты по запросу: <b>{query}</b>\n"
            f"📄 Страница {page + 1}\n\n"
            f"Нажмите на кнопку, чтобы отправить GIF:\n\n"
        )
        
        await status_message.edit_text(
            message_text,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик нажатий на кнопки"""
        query = update.callback_query
        await query.answer()
        
        callback_data = query.data
        user_id = update.effective_user.id
        
        if callback_data.startswith("send_gif_"):
            # Отправляем выбранный GIF
            gif_id = callback_data.replace("send_gif_", "")
            gif_url = f"https://media.giphy.com/media/{gif_id}/giphy.gif"
            
            try:
                await query.message.reply_animation(
                    animation=gif_url,
                    caption=f"🎬 GIF от SMALLGIF'S\n🔍 Найдено @{context.bot.username}"
                )
            except Exception as e:
                logger.error(f"Error sending GIF: {e}")
                await query.message.reply_text(
                    "❌ Не удалось отправить GIF. Попробуйте другой."
                )
        
        elif callback_data.startswith("page_"):
            new_page = int(callback_data.replace("page_", ""))
            user_data = self.user_searches.get(user_id)
            
            if user_data:
                await query.message.delete()
                fake_message = query.message
                await self.show_gif_results_inline(fake_message, context, user_data["query"], new_page)
        
        elif callback_data.startswith("refresh_"):
            search_query = callback_data.replace("refresh_", "")
            user_data = self.user_searches.get(user_id)
            
            if user_data:
                await query.message.delete()
                fake_message = query.message
                await self.show_gif_results_inline(fake_message, context, search_query, user_data.get("page", 0))
        
        elif callback_data == "show_support":
            await self.show_support_message(query)
    
    async def show_gif_results_inline(self, message, context, query, page=0):
        """Обновление результатов поиска (для callback)"""
        gifs = await self.search_gifs(query)
        
        if not gifs:
            await message.reply_text("😕 GIF не найдены. Попробуйте другой запрос.")
            return
        
        keyboard = []
        gifs_per_page = 8
        start_idx = page * gifs_per_page
        end_idx = start_idx + gifs_per_page
        page_gifs = gifs[start_idx:end_idx]
        
        for i in range(0, len(page_gifs), 2):
            row = []
            for j in range(2):
                if i + j < len(page_gifs):
                    gif = page_gifs[i + j]
                    row.append(InlineKeyboardButton(
                        f"GIF {start_idx + i + j + 1}",
                        callback_data=f"send_gif_{gif['id']}"
                    ))
            if row:
                keyboard.append(row)
        
        nav_row = []
        if page > 0:
            nav_row.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"page_{page-1}"))
        nav_row.append(InlineKeyboardButton("🔄 Обновить", callback_data=f"refresh_{query}"))
        if len(gifs) > end_idx:
            nav_row.append(InlineKeyboardButton("➡️ Далее", callback_data=f"page_{page+1}"))
        
        if nav_row:
            keyboard.append(nav_row)
        
        keyboard.append([
            InlineKeyboardButton("⭐ Поддержать создателя", callback_data="show_support")
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message_text = (
            f"🎬 <b>SMALLGIF'S</b>\n"
            f"🔍 Результаты по запросу: <b>{query}</b>\n"
            f"📄 Страница {page + 1}\n\n"
            f"Нажмите на кнопку для отправки GIF"
        )
        
        await message.reply_text(
            message_text,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    async def show_support_message(self, query):
        """Показать сообщение поддержки с мини-приложением"""
        support_text = (
            "⭐ <b>Поддержать SMALLGIF'S</b>\n\n"
            "Ваша поддержка помогает развивать бота!\n"
            "Вы можете отправить Telegram Stars создателю.\n\n"
            "👇 Нажмите кнопку ниже, чтобы открыть меню поддержки:"
        )
        
        # Создаем WebApp кнопку
        web_app_url = f"https://your-domain.com/stars-app"  # URL вашего веб-приложения
        
        keyboard = [
            [InlineKeyboardButton(
                "💝 Отправить звезды", 
                web_app=WebAppInfo(url=web_app_url)
            )],
            [InlineKeyboardButton(
                "💰 Купить звезды", 
                url="https://t.me/dogstar_bot"
            )]
        ]
        
        await query.message.reply_text(
            support_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )
    
    async def web_app_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик данных из мини-приложения"""
        data = json.loads(update.effective_message.web_app_data.data)
        
        if data.get('action') == 'send_stars':
            amount = data.get('amount', 0)
            
            # Отправляем инвойс на Stars
            await update.effective_message.reply_text(
                f"✨ <b>Спасибо за поддержку!</b>\n\n"
                f"Вы отправили: <b>{amount} ⭐</b>\n"
                f"Создатель: @{CREATOR_USERNAME}\n\n"
                f"💝 Ваша поддержка очень важна для развития SMALLGIF'S!",
                parse_mode='HTML'
            )
            
            # Здесь можно добавить логику для реальной оплаты через Telegram Stars API
    
    def run(self):
        """Запуск бота"""
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Добавляем обработчики
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("search", self.search_command))
        application.add_handler(CommandHandler("support", lambda u, c: self.show_support_message(u.callback_query if u.callback_query else None)))
        application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND & filters.Entity("mention"), 
            self.handle_mention
        ))
        application.add_handler(CallbackQueryHandler(self.button_callback))
        application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, self.web_app_data))
        
        # Запускаем бота
        print("🚀 SMALLGIF'S бот запущен!")
        print(f"🤖 Бот: @{application.bot.username}")
        print("=" * 40)
        application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    bot = SmallGIFsBot()
    bot.run()

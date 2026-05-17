import logging
import requests
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from keep_alive import run_keep_aliv

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===== КОНФИГУРАЦИЯ =====
BOT_TOKEN = "8678518649:AAHjfB6Z9QTytmSRej2hDbV3hxGbokY1wdc"
GIPHY_API_KEY = "YOUR_GIPHY_API_KEY"
CREATOR_USER_ID = 7969057973  # Ваш Telegram ID
CREATOR_USERNAME = "lilmopss"  # Ваш username без @

# Настройки порта (PythonAnywhere использует порт из переменной окружения)
PORT = int(os.environ.get('PORT', 8080))

class StarsAppHandler(BaseHTTPRequestHandler):
    """HTTP обработчик для мини-приложения Stars"""
    
    def do_GET(self):
        if self.path == '/' or self.path == '/stars':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html_content = self.get_stars_html()
            self.wfile.write(html_content.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def get_stars_html(self):
        return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>SMALLGIF'S - Поддержка создателя</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 15px;
            color: white;
            overflow-x: hidden;
        }
        
        .container {
            max-width: 450px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            margin-bottom: 25px;
            padding: 25px 20px;
            background: rgba(255, 255, 255, 0.12);
            border-radius: 25px;
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        
        .bot-name {
            font-size: 36px;
            font-weight: 800;
            background: linear-gradient(135deg, #FFD700, #FFA500);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
            letter-spacing: 1px;
        }
        
        .stars-animation {
            font-size: 70px;
            animation: float 3s ease-in-out infinite;
            display: inline-block;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px) rotate(0deg); }
            25% { transform: translateY(-15px) rotate(-5deg); }
            75% { transform: translateY(-15px) rotate(5deg); }
        }
        
        .title {
            font-size: 24px;
            font-weight: 700;
            margin: 15px 0 10px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        
        .subtitle {
            font-size: 14px;
            opacity: 0.9;
            margin-bottom: 10px;
            line-height: 1.5;
            font-weight: 300;
        }
        
        .stars-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
            margin-bottom: 20px;
        }
        
        .star-option {
            background: rgba(255, 255, 255, 0.12);
            backdrop-filter: blur(10px);
            border: 2px solid rgba(255, 255, 255, 0.25);
            border-radius: 20px;
            padding: 22px 15px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        
        .star-option::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            opacity: 0;
            transition: opacity 0.3s;
        }
        
        .star-option:hover::before {
            opacity: 1;
        }
        
        .star-option:active {
            transform: scale(0.95);
        }
        
        .star-option.selected {
            background: linear-gradient(135deg, rgba(255, 215, 0, 0.35), rgba(255, 165, 0, 0.35));
            border-color: #FFD700;
            box-shadow: 0 0 30px rgba(255, 215, 0, 0.5);
            transform: scale(1.05);
        }
        
        .star-option.selected .star-icon {
            animation: spin 0.6s ease-in-out;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg) scale(1); }
            50% { transform: rotate(180deg) scale(1.3); }
            100% { transform: rotate(360deg) scale(1); }
        }
        
        .star-count {
            font-size: 34px;
            font-weight: 800;
            margin-bottom: 5px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        
        .star-icon {
            font-size: 28px;
            margin-bottom: 8px;
            display: inline-block;
        }
        
        .price-tag {
            font-size: 13px;
            opacity: 0.85;
            margin-top: 8px;
            background: rgba(255, 255, 255, 0.2);
            padding: 4px 12px;
            border-radius: 20px;
            display: inline-block;
        }
        
        .custom-section {
            background: rgba(255, 255, 255, 0.12);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 20px;
            padding: 18px;
            margin-bottom: 18px;
        }
        
        .custom-label {
            font-size: 14px;
            margin-bottom: 12px;
            opacity: 0.9;
            text-align: center;
            font-weight: 500;
        }
        
        .custom-input {
            background: rgba(255, 255, 255, 0.15);
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 15px;
            padding: 14px 18px;
            width: 100%;
            color: white;
            font-size: 20px;
            text-align: center;
            outline: none;
            transition: all 0.3s;
            font-weight: 600;
        }
        
        .custom-input::placeholder {
            color: rgba(255, 255, 255, 0.5);
            font-weight: 400;
        }
        
        .custom-input:focus {
            border-color: #FFD700;
            background: rgba(255, 255, 255, 0.25);
            box-shadow: 0 0 20px rgba(255, 215, 0, 0.3);
        }
        
        .send-button {
            background: linear-gradient(135deg, #FFD700, #FFA500);
            color: #333;
            border: none;
            border-radius: 18px;
            padding: 18px;
            width: 100%;
            font-size: 20px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            text-transform: uppercase;
            letter-spacing: 2px;
            box-shadow: 0 8px 25px rgba(255, 165, 0, 0.4);
            position: relative;
            overflow: hidden;
        }
        
        .send-button::after {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            transform: translate(-50%, -50%);
            transition: width 0.6s, height 0.6s;
        }
        
        .send-button:active::after {
            width: 300px;
            height: 300px;
        }
        
        .send-button:not(:disabled):hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 35px rgba(255, 165, 0, 0.6);
        }
        
        .send-button:active {
            transform: translateY(-1px);
        }
        
        .send-button:disabled {
            background: rgba(255, 255, 255, 0.2);
            color: rgba(255, 255, 255, 0.5);
            box-shadow: none;
            cursor: not-allowed;
        }
        
        .success-message {
            margin-top: 15px;
            text-align: center;
            font-size: 14px;
            opacity: 0;
            transition: all 0.5s;
            transform: translateY(10px);
        }
        
        .success-message.show {
            opacity: 1;
            transform: translateY(0);
        }
        
        .creator-info {
            text-align: center;
            margin-top: 25px;
            padding: 18px;
            background: rgba(255, 255, 255, 0.12);
            border-radius: 20px;
            backdrop-filter: blur(10px);
            font-size: 13px;
            opacity: 0.85;
            border: 1px solid rgba(255, 255, 255, 0.2);
            line-height: 1.6;
        }
        
        .heart {
            color: #FF6B6B;
            animation: heartbeat 1.5s ease-in-out infinite;
            display: inline-block;
        }
        
        @keyframes heartbeat {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.2); }
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
                Ваша поддержка помогает развивать бота<br>и добавлять новые функции!
            </div>
        </div>
        
        <div class="stars-grid">
            <div class="star-option" onclick="selectStars(10, this)">
                <div class="star-icon">⭐</div>
                <div class="star-count">10</div>
                <div class="price-tag">~ 0.99$</div>
            </div>
            <div class="star-option" onclick="selectStars(25, this)">
                <div class="star-icon">🌟</div>
                <div class="star-count">25</div>
                <div class="price-tag">~ 1.99$</div>
            </div>
            <div class="star-option" onclick="selectStars(50, this)">
                <div class="star-icon">💫</div>
                <div class="star-count">50</div>
                <div class="price-tag">~ 3.99$</div>
            </div>
            <div class="star-option" onclick="selectStars(100, this)">
                <div class="star-icon">✨</div>
                <div class="star-count">100</div>
                <div class="price-tag">~ 7.99$</div>
            </div>
        </div>
        
        <div class="custom-section">
            <div class="custom-label">💝 Или введите свою сумму:</div>
            <input type="number" 
                   class="custom-input" 
                   id="customStars" 
                   placeholder="Количество звезд"
                   min="1"
                   max="10000"
                   oninput="onCustomInput()">
        </div>
        
        <button class="send-button" id="sendButton" disabled onclick="sendStars()">
            Выберите количество звезд
        </button>
        
        <div class="success-message" id="successMessage">
            ✨ Спасибо за поддержку! Звезды отправлены!
        </div>
        
        <div class="creator-info">
            Создатель бота: <strong>@""" + CREATOR_USERNAME + """</strong><br>
            <span class="heart">❤️</span> Спасибо, что помогаете развиваться!
        </div>
    </div>
    
    <script>
        let tg = window.Telegram.WebApp;
        let selectedStars = 0;
        
        // Расширяем приложение на весь экран
        tg.expand();
        tg.ready();
        
        // Настройка темы
        tg.setHeaderColor('#667eea');
        tg.setBackgroundColor('#667eea');
        
        function selectStars(count, element) {
            selectedStars = count;
            document.getElementById('customStars').value = '';
            
            // Убираем выделение со всех кнопок
            document.querySelectorAll('.star-option').forEach(opt => {
                opt.classList.remove('selected');
            });
            
            // Выделяем выбранную
            if (element) {
                element.classList.add('selected');
            }
            
            updateButton();
        }
        
        function onCustomInput() {
            let input = document.getElementById('customStars');
            let value = parseInt(input.value);
            
            if (value && value > 0) {
                selectedStars = value;
                document.querySelectorAll('.star-option').forEach(opt => {
                    opt.classList.remove('selected');
                });
            } else {
                selectedStars = 0;
            }
            
            updateButton();
        }
        
        function updateButton() {
            let button = document.getElementById('sendButton');
            
            if (selectedStars > 0) {
                button.disabled = false;
                button.textContent = `Отправить ${selectedStars} ⭐`;
                button.style.animation = 'pulse 0.6s ease-in-out';
                setTimeout(() => button.style.animation = '', 600);
            } else {
                button.disabled = true;
                button.textContent = 'Выберите количество звезд';
            }
        }
        
        function sendStars() {
            if (!selectedStars || selectedStars < 1) return;
            
            let button = document.getElementById('sendButton');
            let message = document.getElementById('successMessage');
            
            button.disabled = true;
            button.textContent = '⏳ Отправка...';
            
            // Отправляем данные в Telegram
            try {
                tg.sendData(JSON.stringify({
                    action: 'send_stars',
                    amount: selectedStars,
                    bot: 'SMALLGIF\\'S'
                }));
                
                // Показываем сообщение об успехе
                message.classList.add('show');
                
                // Восстанавливаем кнопку
                button.textContent = '✅ Отправлено!';
                button.style.background = 'linear-gradient(135deg, #4CAF50, #45a049)';
                
                // Закрываем мини-приложение
                setTimeout(() => {
                    tg.close();
                }, 2000);
                
            } catch (error) {
                button.disabled = false;
                button.textContent = '❌ Ошибка, попробуйте снова';
                console.error('Error sending stars:', error);
            }
        }
        
        // Обработка нажатия клавиши Enter в поле ввода
        document.getElementById('customStars').addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && selectedStars > 0) {
                sendStars();
            }
        });
    </script>
</body>
</html>
"""
    
    def log_message(self, format, *args):
        pass  # Отключаем логи HTTP запросов

class SmallGIFsBot:
    def __init__(self):
        self.user_searches = {}
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        welcome_text = """
🎬 <b>SMALLGIF'S</b> - Ваш персональный GIF-поисковик!

🚀 <b>Как использовать:</b>
• В любом чате: <code>@{bot_username} запрос</code>
• Команда: /search запрос
• Поддержка: /support

💡 <b>Пример:</b> <code>@{bot_username} смешной кот</code>

✨ Создатель: @{creator}
        """.format(
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
    
    async def support_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /support"""
        await self.show_support_message(update, context)
    
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
                    [InlineKeyboardButton("🔍 Открыть SMALLGIF'S", switch_inline_query_current_chat="")]
                ]
                await update.message.reply_text(
                    f"🎬 <b>SMALLGIF'S</b> к вашим услугам!\n"
                    f"Напишите запрос после упоминания:\n"
                    f"<code>@{bot_username} ваш запрос</code>",
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode='HTML'
                )
    
    async def show_gif_results(self, update: Update, context: ContextTypes.DEFAULT_TYPE, query: str, page: int = 0):
        """Показать результаты поиска GIF"""
        user_id = update.effective_user.id
        self.user_searches[user_id] = {"query": query, "page": page}
        
        status_message = await update.message.reply_text(
            f"🔍 <b>SMALLGIF'S</b> ищет: {query}...",
            parse_mode='HTML'
        )
        
        gifs = await self.search_gifs(query)
        
        if not gifs:
            await status_message.edit_text(
                "😕 GIF не найдены.\nПопробуйте другой запрос.",
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
        
        message_text = (
            f"🎬 <b>SMALLGIF'S</b>\n"
            f"🔍 Результаты: <b>{query}</b>\n"
            f"📄 Страница {page + 1}\n\n"
            f"Нажмите на кнопку, чтобы отправить GIF"
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
                    caption=f"🎬 GIF от SMALLGIF'S\n🔍 @{context.bot.username}"
                )
            except Exception as e:
                logger.error(f"Error sending GIF: {e}")
                await query.message.reply_text("❌ Не удалось отправить GIF. Попробуйте другой.")
        
        elif callback_data.startswith("page_"):
            new_page = int(callback_data.replace("page_", ""))
            user_data = self.user_searches.get(user_id)
            
            if user_data:
                await query.message.delete()
                fake_message = query.message
                fake_update = type('obj', (object,), {
                    'effective_user': update.effective_user,
                    'message': fake_message
                })
                await self.show_gif_results(fake_update, context, user_data["query"], new_page)
        
        elif callback_data.startswith("refresh_"):
            search_query = callback_data.replace("refresh_", "")
            user_data = self.user_searches.get(user_id)
            
            if user_data:
                await query.message.delete()
                fake_message = query.message
                fake_update = type('obj', (object,), {
                    'effective_user': update.effective_user,
                    'message': fake_message
                })
                await self.show_gif_results(fake_update, context, search_query, user_data.get("page", 0))
        
        elif callback_data == "show_support":
            await self.show_support_message(query, context)
    
    async def show_support_message(self, update_or_query, context=None):
        """Показать сообщение поддержки"""
        support_text = """
⭐ <b>Поддержать SMALLGIF'S</b>

Ваша поддержка помогает развивать бота!
Вы можете отправить Telegram Stars создателю.

👇 Нажмите кнопку ниже:
        """
        
        # URL для мини-приложения (замените на ваш PythonAnywhere URL)
        app_url = f"https://mrbaget228.pythonanywhere.com"
        
        keyboard = [
            [InlineKeyboardButton(
                "💝 Отправить звезды", 
                web_app=WebAppInfo(url=app_url)
            )],
            [InlineKeyboardButton(
                "💰 Купить звезды", 
                url="https://t.me/dogstar_bot"
            )]
        ]
        
        if hasattr(update_or_query, 'message'):
            await update_or_query.message.reply_text(
                support_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )
        else:
            await update_or_query.message.reply_text(
                support_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )
    
    async def web_app_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик данных из мини-приложения"""
        data = json.loads(update.effective_message.web_app_data.data)
        
        if data.get('action') == 'send_stars':
            amount = data.get('amount', 0)
            
            # Отправляем подтверждение
            await update.effective_message.reply_text(
                f"✨ <b>Спасибо за поддержку!</b>\n\n"
                f"Вы отправили: <b>{amount} ⭐</b>\n"
                f"Создатель: @{CREATOR_USERNAME}\n\n"
                f"💝 Ваша поддержка очень важна для SMALLGIF'S!\n"
                f"Благодаря вам бот будет становиться лучше!",
                parse_mode='HTML'
            )
            
            # Здесь можно добавить логику реальной оплаты
    
    def run(self):
        """Запуск бота и веб-сервера"""
        # Запускаем веб-сервер в отдельном потоке
        web_server = HTTPServer(('0.0.0.0', PORT), StarsAppHandler)
        web_thread = Thread(target=web_server.serve_forever)
        web_thread.daemon = True
        web_thread.start()
        
        print(f"🌐 Веб-сервер запущен на порту {PORT}")
        print(f"📱 URL мини-приложения: https://mrbaget228.pythonanywhere.com")
        
        # Запускаем бота
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Добавляем обработчики
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("search", self.search_command))
        application.add_handler(CommandHandler("support", self.support_command))
        application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND & filters.Entity("mention"), 
            self.handle_mention
        ))
        application.add_handler(CallbackQueryHandler(self.button_callback))
        application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, self.web_app_data))
        
        # Запускаем бота
        print("🚀 SMALLGIF'S бот запущен!")
        print(f"🤖 Бот: @{application.bot.username}")
        print("=" * 50)
        
        # Используем webhook для лучшей производительности
        # или polling для тестирования
        application.run_polling(allowed_updates=Update.ALL_TYPES)

def run_web_server():
    """Отдельная функция для запуска веб-сервера"""
    server = HTTPServer(('0.0.0.0', PORT), StarsAppHandler)
    print(f"🌐 Stars App доступен на порту {PORT}")
    server.serve_forever()

if __name__ == "__main__":
    # Проверяем наличие токенов
    if BOT_TOKEN == "8678518649:AAHjfB6Z9QTytmSRej2hDbV3hxGbokY1wdc":
        print("❌ Ошибка: Укажите BOT_TOKEN в коде!")
        exit(1)
    if GIPHY_API_KEY == "YOUR_GIPHY_API_KEY":
        print("❌ Ошибка: Укажите GIPHY_API_KEY в коде!")
        exit(1)
    if CREATOR_USERNAME == "lilmopss":
        print("⚠️ Предупреждение: Укажите CREATOR_USERNAME в коде!")
    
    bot = SmallGIFsBot()
    bot.run()

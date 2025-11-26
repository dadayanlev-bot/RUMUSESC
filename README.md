 # RUMUS BOT  
Telegram бот для кастомной экосистемы RUMUS.  

### Запуск локально:
1. Создать окружение
2. Установить зависимости
3. Создать переменную TOKEN
4. python main.py

### Render Deployment (Worker):
- Create New > Background Worker
- Build command: pip install -r requirements.txt
- Start command: python main.py
- Add env var: TOKEN=your_bot_token

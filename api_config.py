class APIConfig:
    def __init__(self, logger):
        self.config = {
            "TELEGRAM_API": "7703234311:AAECQlbQ6HmGW_FJ6puo3H94944bXcpVhAU",
            "SQL_HOST": "localhost",
            "SQL_DATABASE": "strangerbot",      # Change if database name is different
            "SQL_USER": "postgres",
            "SQL_PASSWORD": "Lalit@12345",
            "SQL_PORT": "5432",
            "ADMIN_ID": 1264035473    # ✅ Your real Telegram user ID
        }
        self.logger = logger

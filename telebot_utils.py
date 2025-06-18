import logging
import os
import psycopg2  # type: ignore
import telebot  # type: ignore
from threading import Lock

class Telebot_utils:
    def __init__(self) -> None:
        logging.basicConfig(level=logging.INFO)

        # ✅ Using single DATABASE_URL environment variable
        self.conn = psycopg2.connect(os.environ.get("DATABASE_URL"))

        self.api = os.environ.get("BOT_TOKEN")
        admin_id_env = os.environ.get("ADMIN_ID")
        self.admin_id = int(admin_id_env) if admin_id_env else 123456789  # fallback admin ID
        self.c = self.conn.cursor()
        self.lock = Lock()
        self.queue = []
        self.chating = []
        self.pairs = {}
        self.temppairs = {}
        self.bot = telebot.TeleBot(self.api)

    def log_user(self, chat_id, username: str, user_first: str, user_last: str):
        self.c.execute("SELECT * FROM botuser WHERE user_id = %s;", (chat_id,))
        results = self.c.fetchall()
        if len(results) == 0:
            self.c.execute(
                "INSERT INTO botuser (user_id, username, user_first, user_last) VALUES (%s, %s, %s, %s);",
                (chat_id, username, user_first, user_last),
            )
            self.conn.commit()
            return True
        else:
            return False

    def returnall(self, chat_id: int):
        if chat_id == self.admin_id:
            self.c.execute("SELECT * FROM botuser;")
            db = str(self.c.fetchall())
            return db
        else:
            return False

    def returnreported(self, chat_id: int):
        if chat_id == self.admin_id:
            self.c.execute("SELECT * FROM reportlist;")
            rl = str(self.c.fetchall())
            return rl
        else:
            return False

    def found(self, chat_id: int):
        if chat_id in self.chating:
            return True
        else:
            self.chating.append(chat_id)

    def requeue(self, chat_id: int):
        try:
            self.chating.remove(chat_id)
        except Exception as e:
            self.bot.send_message(self.admin_id, f"debug {chat_id} : {e} : requeue")

    def getid(self, chat_id: int):
        return self.pairs.get(chat_id, chat_id)

    def remove_queue(self, chat_id: int):
        if chat_id in self.queue:
            with self.lock:
                self.queue.remove(chat_id)

    def exit(self, chat_id: int, chat_to: int):
        try:
            del self.pairs[chat_id]
            del self.pairs[chat_to]
        except Exception as e:
            self.bot.send_message(self.admin_id, f"debug {chat_id} : {e} : exit")

    def matchmake(self, chat_id: int):
        if chat_id in self.queue:
            return False
        with self.lock:
            if self.temppairs.get(chat_id):
                self.deletmpairs(chat_id)
            self.queue.append(chat_id)
            if len(self.queue) == 2:
                partner_id = self.queue[0]
                self.pairs[chat_id] = partner_id
                self.pairs[partner_id] = chat_id
                self.temppairs[chat_id] = partner_id
                self.temppairs[partner_id] = chat_id
                self.queue.clear()
        return True

    def deletmpairs(self, chat_id: int):
        if chat_id in self.temppairs:
            del self.temppairs[chat_id]

    def inchating(self, chat_id: int):
        return chat_id in self.chating

    def report1(self, chat_id: int):
        if self.inchating(chat_id):
            self.reportlog(self.getid(chat_id), chat_id)
            return True
        elif self.temppairs.get(chat_id):
            self.reportlog(self.temppairs[chat_id], chat_id)
            return True
        else:
            return False

    def reportlog(self, reported: int, reporter: int):
        self.c.execute(
            "INSERT INTO reportlist (reported_id, reporter_id) VALUES (%s, %s);",
            (reported, reporter),
        )
        self.conn.commit()

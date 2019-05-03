from datetime import datetime
import sqlite3


class ChatRepositorySqlite:

    def __init__(self, database=':memory:'):
        self.connection = sqlite3.connect(database)

        cursor = self.connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users
            (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email NVARCHAR(256) NOT NULL,
                password NVARCHAR(256) NOT NULL,
                family_name TEXT NULL,
                given_names TEXT NULL,
                nick_name TEXT NULL,
                UNIQUE (email)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS rooms
            (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name NVARCHAR(256) NOT NULL,
                description NVARCHAR(256) NOT NULL,
                UNIQUE (name)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS messages
            (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                content_type NVARCHAR(256) NOT NULL,
                content      BLOB NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS chats
            (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                room_id    INTEGER   NOT NULL,
                created    TIMESTAMP NOT NULL,
                sender_id  INTEGER   NOT NULL,
                message_id INTEGER   NOT NULL,
                UNIQUE (room_id, sender_id, created),
                FOREIGN KEY (room_id)    REFERENCES rooms(id),
                FOREIGN KEY (sender_id)  REFERENCES users(id),
                FOREIGN KEY (message_id) REFERENCES messages(id)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations
            (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id   INTEGER NOT NULL,
                receiver_id INTEGER NOT NULL,
                created     TIMESTAMP NOT NULL,
                message_id  INTEGER NOT NULL,
                UNIQUE (sender_id, receiver_id, created),
                FOREIGN KEY (sender)     REFERENCES profiles(email),
                FOREIGN KEY (receiver)   REFERENCES profiles(email),
                FOREIGN KEY (message_id) REFERENCES messages(id)
            )
            """
        )
        # chats(room_name, sent_time, from_email, text)
        self.connection.commit()


    def create_user(self, email, password, family_name=None, given_names=[], nick_name=None):
        self.create_user(email, password)
        self.create_profile(email, family_name, given_names, nick_name)


    def read_user(self, email):
        password = self.read_password(email)
        profile = self.read_profile(email)
        return {'password': password, 'profile': profile}


    def update_user(self, email, password, family_name=None, given_names=[], nick_name=None):
        self.update_user(email, password)
        self.update_profile(email, family_name, given_names, nick_name)


    def delete_user(self, email):
        self.delete_profile(email)
        self.delete_user(email)


    def create_password(self, email, password):
        cursor = self.connection.cursor()
        cursor.execute(
            "insert into passwords(email, password) values (?,?)",
            (email, password)
        )
        self.connection.commit()


    def read_password(self, email):
        cursor = self.connection.cursor()
        cursor.execute(
            "select email, password from passwords where email = ?",
            (email,)
        )
        return cursor.fetchall()


    def update_password(self, email, password):
        cursor = self.connection.cursor()
        cursor.execute(
            "update passwords set password=? where email = ?",
            (password, email)
        )
        self.connection.commit()


    def delete_password(self, email):
        cursor = self.connection.cursor()
        cursor.execute(
            "delete passwords where email = ?",
            (email,)
        )
        self.connection.commit()


    def create_profile(self, email, family_name=None, given_names=[], nick_name=None):
        given_names = ",".join(given_names) if len(given_names) > 0 else None
        cursor = self.connection.cursor()
        cursor.execute(
            "insert into profiles(email, family_name, given_names, nick_name) values (?,?,?,?)",
            (email, family_name, given_names, nick_name)
        )
        self.connection.commit()


    def read_profile(self, email):
        cursor = self.connection.cursor()
        cursor.execute(
            "select email, family_name, given_names, nick_name from profiles where email = ?",
            (email,)
        )
        return cursor.fetchall()


    def update_profile(self, email, family_name, given_names, nick_name):
        cursor = self.connection.cursor()
        cursor.execute(
            "update profiles set family_name=?, given_names=?, nick_name=? where email = ?",
            (family_name, given_names, nick_name, email)
        )
        self.connection.commit()


    def delete_profile(self, email):
        cursor = self.connection.cursor()
        cursor.execute(
            "delete profiles where email = ?",
            (email,)
        )
        self.connection.commit()


    def create_room(self, name, description):
        cursor = self.connection.cursor()
        cursor.execute(
            "insert into rooms(name, description) values (?,?)",
            (name, description)
        )
        self.connection.commit()


    def read_room(self, name):
        cursor = self.connection.cursor()
        cursor.execute(
            "select name, description from rooms where name = ?",
            (name,)
        )
        return cursor.fetchall()


    def update_room(self, name, description):
        cursor = self.connection.cursor()
        cursor.execute(
            "update rooms set description=? where name=?",
            (description, name)
        )
        self.connection.commit()


    def delete_room(self, name):
        cursor = self.connection.cursor()
        cursor.execute(
            "delete rooms where name=?",
            (name,)
        )
        self.connection.commit()


    def append_chat(self, room_name, from_email, text):
        cursor = self.connection.cursor()
        cursor.execute(
            "insert into chats(room_name, sent_time, from_email, text) values (?,?)",
            (room_name, datetime.now(), from_email, text)
        )
        self.connection.commit()


    def read_chats(self, room_name, count=10):
        cursor = self.connection.cursor()
        cursor.execute(
            "select room_name, sent_time, from_email, text from chats where room_name = ? order by sent_time desc limit ?",
            (room_name, count)
        )
        return cursor.fetchall()


    def append_message(self, from_email, to_email, text):
        pass


    def read_messages(self, from_email, to_email, count=100):
        pass

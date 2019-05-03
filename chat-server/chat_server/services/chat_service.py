class ChatService:

    async def register(self, email, password):
        pass
    

    async def login(self, email, password):
        pass


    async def logout(self, email):
        pass


    async def update_password(self, email, old_password, new_password):
        pass


    async def update_profile(self, email, first_name, last_name, nick_name):
        pass


    async def message_history(self, room_or_user, count):
        pass


    async def monitor_messages(self, room_or_person):
        pass


    async def send_message(self, room_or_person, message):
        pass

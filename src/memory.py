class Conversation:
    def __init__(self):
        self.messages = []

    def add_user(self, text):
        self.messages.append({"role": "user", "content": text})

    def add_assistant(self, text):
        self.messages.append({"role": "assistant", "content": text})

    def as_messages(self, system_prompt: str):
        return [{"role": "system", "content": system_prompt}] + self.messages
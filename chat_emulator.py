import time
import random
from datetime import datetime

# -----------------------------
# Message Object
# -----------------------------
class Message:
    def __init__(self, sender, text):
        self.sender = sender
        self.text = text
        self.timestamp = datetime.now()

    def __str__(self):
        ts = self.timestamp.strftime("%H:%M:%S")
        return f"[{ts}] {self.sender}: {self.text}"


# -----------------------------
# Expanded Bot Response Engine
# -----------------------------
def generate_expanded_reply(user_text):
    curiosity = [
        "That's interesting — what made you think of that?",
        "I’m curious, how long have you felt that way?",
        "Really? I’d love to hear more about it.",
        "What part of that stands out the most to you?"
    ]

    humor = [
        "Haha, okay that actually made me laugh.",
        "I wasn’t ready for that one.",
        "You’re wild for saying that.",
        "That’s comedy gold right there."
    ]

    reflective = [
        "I get what you're saying. It reminds me of how people often feel when they're dealing with something unexpected.",
        "That makes sense. Sometimes things hit harder than we expect.",
        "I hear you. It’s one of those thoughts that sticks with you.",
        "It sounds like you’ve been thinking about this for a while."
    ]

    supportive = [
        "I get it — that can be tough.",
        "You’re not alone in feeling that way.",
        "That’s completely valid.",
        "I’m here with you — keep going."
    ]

    playful = [
        "Oh? Go on, I’m listening.",
        "Bold statement. I respect it.",
        "Now *that* is a take.",
        "You’re bringing energy today."
    ]

    templates = [
        f"So you're saying: '{user_text}' — that’s actually pretty fascinating.",
        f"Let me think about that… okay, yeah, I see where you're coming from.",
        f"That's one way to look at it. Another angle might be totally different though.",
        f"I didn’t expect you to say '{user_text}', but I’m glad you did."
    ]

    all_responses = curiosity + humor + reflective + supportive + playful + templates

    return random.choice(all_responses)


# -----------------------------
# Chat Emulator
# -----------------------------
class ChatEmulator:
    def __init__(self, users):
        self.users = users
        self.history = []

    def send_message(self, sender, text):
        msg = Message(sender, text)
        self.history.append(msg)
        print(msg)

    def bot_reply(self, bot_name, user_text):
        time.sleep(random.uniform(0.5, 1.5))  # typing delay
        reply = generate_expanded_reply(user_text)
        self.send_message(bot_name, reply)

    def run(self, human_name, bot_name):
        print("=== Chat Emulator Started ===")
        print("Type 'quit' to exit.\n")

        while True:
            user_input = input(f"{human_name}: ")
            if user_input.lower().strip() == "quit":
                print("\n=== Chat Ended ===")
                break

            self.send_message(human_name, user_input)
            self.bot_reply(bot_name, user_input)


# -----------------------------
# Main Entry Point
# -----------------------------
if __name__ == "__main__":
    emulator = ChatEmulator(users=["You", "Bot"])
    emulator.run(human_name="You", bot_name="Bot")


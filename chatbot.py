class MyChatbot:
    def __init__(self):
        pass

    def get_response(self, message):
        responses = [
            "Hello! I'm a mock chatbot.",
            "You said: " + message,
            "Here's another message.",
            "And one more."
        ]
        return responses

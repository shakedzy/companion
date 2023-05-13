import openai
from typing import Generator
from memory import Memory
from config import Config

class Chatbot:
    def __init__(self, config: Config, memory: Memory):
        self._memory = memory
        self._model = config.model.name
        self._temperature = config.model.temperature
        self._memory.add("system",
                         f"""You are a French teacher named {config.bot.name}. You are on a 1-on-1 session with your
                             student, {config.user.name}. {config.user.name}'s French level is {config.language.level}.
                             Your task is to assist your student in advancing their French.
                             IMPORTANT: If your student makes a mistake, be it typo or grammar, you MUST first correct
                             your student and only then reply.""")
        # self._memory.add("user", "Bonjour!")

    def get_response(self, message) -> Generator:
        response = openai.ChatCompletion.create(
            model=self._model,
            temperature=self._temperature,
            stream=True,
            messages=self._memory.get_chat_history()
        )
        return self._generate_response(response)

    def _generate_response(self, response: Generator) -> Generator:
        for chunk in response:
            yield chunk['choices'][0]['delta'].get('content', '')

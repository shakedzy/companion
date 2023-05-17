import openai
from iso639 import Lang
from typing import Generator
from memory import Memory
from config import Config

SYSTEM_PROMPT = """You are a {language} teacher named {teacher_name}. You are on a 1-on-1 session with your
                   student, {user_name}. {user_name}'s {language} level is {level}.
                   Your task is to assist your student in advancing their {language}.
                   - When the session begins, offer a suitable session for {user_name}, unless asked for 
                   something else.
                   - {user_name}'s native language is {user_language}. {user_name} might address you in their own
                   language when felt their {language} is not well enough. When that happens, first translate their
                   message to {language}, and then reply.
                   - IMPORTANT: If your student makes any mistake, be it typo or grammar, you MUST first correct
                   your student and only then reply.
                   - You are only allowed to speak {language}."""

class Chatbot:
    def __init__(self, config: Config, memory: Memory):
        self._memory = memory
        self._model = config.model.name
        self._temperature = config.model.temperature
        lang = Lang(config.language.learning).name
        user_lang = Lang(config.language.native).name
        self._memory.add("system", SYSTEM_PROMPT.format(
            teacher_name=config.bot.name, user_name=config.user.name, language=lang, user_language=user_lang,
            level=config.language.level
        ))

    def get_response(self) -> Generator:
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

import openai
from iso639 import Lang
from typing import Generator
from python.memory import Memory
from python.config import Config
from python.language import is_text_of_language

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

INITIAL_MESSAGE = """Greet me, and then suggest 3 optional subjects for our lesson suiting my level. 
                     You must reply in {language}."""


class Chatbot:
    def __init__(self, config: Config, memory: Memory):
        self._memory = memory
        self._model = config.model.name
        self._temperature = config.model.temperature
        self._language = config.language.learning
        lang = Lang(config.language.learning).name
        user_lang = Lang(config.language.native).name
        self._memory.add("system", SYSTEM_PROMPT.format(
            teacher_name=config.bot.name, user_name=config.user.name, language=lang, user_language=user_lang,
            level=config.language.level
        ))

    def get_response(self, is_initial_message=False) -> Generator:
        history = self._memory.get_chat_history()
        if is_initial_message:
            history.append({"role": "user", "content": INITIAL_MESSAGE.format(language=self._language)})
        elif not is_text_of_language(history[-1]["content"], language_code=self._language):
            history[-1]["content"] += f"\n---\nNOTE: You MUST reply in {Lang(self._language).name}"
        response = openai.ChatCompletion.create(
            model=self._model,
            temperature=self._temperature,
            stream=True,
            messages=history
        )
        return self._generate_response(response)

    def _generate_response(self, response: Generator) -> Generator:
        for chunk in response:
            yield chunk['choices'][0]['delta'].get('content', '')

from typing import List

class Memory:
    _memory: List[dict] = list()
    _updates: List[dict] = list()

    def __getitem__(self, index):
        return self._memory[index]

    def __repr__(self):
        return self._memory

    def __str__(self):
        return str(self._memory)

    def __len__(self):
        return len(self._memory)

    def add(self, role, message, recording=None, user_recording=None):
        message = ' '.join(message.split())
        mem = {"role": role, "content": message, "recording": recording or list(), "user_recording": user_recording}
        updates = [u for u in self._updates if u["index"] == len(self._memory)]
        [u.pop("index") for u in updates]
        for u in updates:
            u["recording"] = u["recording"] or []
            mem.update(u)
        self._memory.append(mem)

    def update(self, index, **kwargs):
        if index < len(self._memory):
            self._memory[index].update(kwargs)
        else:
            update = kwargs
            update["index"] = index
            self._updates.append(update)

    def get_chat_history(self):
        return [{"role": message["role"], "content": ' '.join(message["content"].split())} for message in self._memory]

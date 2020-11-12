from abc import ABC
from discord import Message, Embed


class Dialog(ABC):
    def __init__(self, *args, **kwargs):
        self._embed: Embed = None
        self.message: Message = None
        self.color: hex = kwargs.get("color") or kwargs.get("colour") or 0x000000


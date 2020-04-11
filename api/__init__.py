from enum import unique, IntEnum
import string

class PromptRequest:

    @unique
    class Mode(IntEnum):
        INT = 0
        TEXT = 1
        LOWER = 2
        UPPER = 3
        KEY_OPTIONS = 4
        MIXED = 5

    MODE_CHARACTER_SETS = {
        Mode.INT: string.digits,
        Mode.TEXT: string.ascii_letters,
        Mode.MIXED: string.digits + string.ascii_letters,
        Mode.UPPER: string.ascii_uppercase,
        Mode.LOWER: string.ascii_lowercase
    }

    def __init__(self, prompt, name, mode=Mode.TEXT, options: dict = None):
        self.result = None
        self.entry = ''
        self.name = name
        self.mode = mode
        self.options = options
        self.prompt = prompt + f'({self.mode.name.capitalize() if self.mode != PromptRequest.Mode.KEY_OPTIONS else ", ".join([f"{k}: {v.name}" for k, v in self.options.items()])}' \
                               f'{" " + repr(self.options["range"]) if self.mode == PromptRequest.Mode.INT and self.options is not None else ""})'
        self.display = self.prompt

    def on_loop(self, c):
        if self.result is None:
            if c == '<BACKSPACE>':
                if len(self.entry) > 0:
                    self.entry = self.entry[:-1]
            elif c in ['<Ctrl-j>', '<PADENTER>'] and self.mode != PromptRequest.Mode.KEY_OPTIONS:
                if self.entry == '':
                    return
                if self.mode == PromptRequest.Mode.INT:
                    self.entry = int(self.entry)
                    if self.mode == PromptRequest.Mode.INT and self.options is not None:
                        if self.entry not in self.options['range']:
                            self.entry = ''
                            self.display = self.prompt + ' ' + str(self.entry)
                            return
                self.result = self.entry
            if self.mode == PromptRequest.Mode.KEY_OPTIONS:
                if c in self.options:
                    self.entry += c
                    if self.mode == PromptRequest.Mode.KEY_OPTIONS:
                        self.result = self.options[self.entry]
            else:
                if c in self.MODE_CHARACTER_SETS[self.mode]:
                    self.entry += c
                    if type(self.options) is dict:
                        if 'length' in self.options:
                            if len(self.entry) > self.options['length']:
                                self.entry = self.entry[:self.options['length']]
            self.display = self.prompt + ' ' + str(self.entry)
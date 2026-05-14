from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship


class Token(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    word: str = Field(index=True, unique=True, nullable=False)

    token_entities: List["TokenEntity"] = Relationship(back_populates="token")


class TokenEntity(SQLModel, table=True):
    __tablename__ = "token_entity"

    id: Optional[int] = Field(default=None, primary_key=True)
    token_id: int = Field(foreign_key="token.id")
    token_type: str
    entity_id: int
    entity_type: str

    token: Token = Relationship(back_populates="token_entities")


KEYWORD_ADD = "keyword:add"
KEYWORD_DEL = "keyword:del"
KEYWORD_LIST = "keyword:list"
KEYWORD_DATASHEET = "keyword:datasheet"
KEYWORD_FIND = "keyword:find"
KEYWORD_HELP = "keyword:help"
KEYWORD_QUIT = "keyword:quit"
PART_ID = "part:identifier"
PART_DESCRIPT = "part:description"
PART_QTY = "part:qty"
CAT_ID = "category:identifier"
OP_SLASH = "operator:slash"
OP_PLUS = "operator:plus"
NUMBER = "value:number"
STRING = "value:string"

_grammar = {
    KEYWORD_ADD: {PART_ID: {PART_QTY: {PART_DESCRIPT: None}}, CAT_ID: lambda: _grammar[CAT_ID]},
    KEYWORD_LIST: {CAT_ID: lambda: _grammar[CAT_ID]},
    KEYWORD_DATASHEET: {CAT_ID: lambda: _grammar[CAT_ID]},
    KEYWORD_DEL: {CAT_ID: lambda: _grammar[CAT_ID]},
    CAT_ID: {None: None, OP_SLASH: lambda: _grammar[CAT_ID], PART_ID: lambda: _grammar[PART_ID]},
    PART_ID: {None: None, OP_PLUS: {NUMBER: None}},
}

LEXICON = {
    "add": [KEYWORD_ADD],
    "del": [KEYWORD_DEL],
    "list": [KEYWORD_LIST],
    "datasheet": [KEYWORD_DATASHEET],
    "find": [KEYWORD_FIND],
    "help": [KEYWORD_HELP],
    "h": [KEYWORD_HELP],
    "quit": [KEYWORD_QUIT],
    "exit": [KEYWORD_QUIT],
    "q": [KEYWORD_QUIT],
    "/": [OP_SLASH],
    "+": [OP_PLUS],
}


def _get_word_types(word):
    types = LEXICON.get(word, [])

    if word.isnumeric():
        types.append(NUMBER)
    elif word.isalpha():
        types.append(STRING)

    return types


def parse(sentence):
    words = sentence.split(" ")
    found = False
    legal_types = _grammar

    while len(words) > 0:
        found = False
        word = words.pop(0)
        word_types = _get_word_types(word)

        for legal_type in legal_types or []:
            if legal_type in word_types:
                legal_types = legal_types[legal_type]
                found = True
                break

    return legal_types if found else {}


def add_to_lexicon(word, type_):
    LEXICON.setdefault(word, []).append(type_)


"""
def next_token(sentence):
    words = sentence.split(" ")
    grm = _grammar

    for word in words:

        if word in lex.keys():



        token_type = _lexicon.get(word)
        nxt = self._next[token_type]() if callable(self._next[token_type]) else self._next[token_type]

    return nxt
"""
"""
def push(self, token):
    self._next = self._next[token]() if callable(self._next[token]) else self._next[token]
    return self.next
"""

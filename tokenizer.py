from enum import Enum
import re

TokenType = Enum('TokenType', 'word delimiter punctuation')
State = Enum('State', 'uninitialized word delimiter punctuation')

xstr = lambda s: s or ""


def is_space(c):
    spaces = " \t\n\r\n"
    return c in spaces


def is_punctuation(c):
    punctuation = ",.;()\"\'-"
    return c in punctuation


def is_alphabet(c):
    return True if re.match("[а-яА-Яa-zA-Z0-9%$№#@\\-]", xstr(c)) else False


class Token:
    def __init__(self, token_type, data):
        self.token_type = token_type
        self.data = data

    def __str__(self):
        return f"Token{{type={self.token_type}, data={self.data}}}"


def uninitialized(c, state, state_data):
    if is_punctuation(c):
        yield State.punctuation, str(c), False
    elif is_alphabet(c):
        yield State.word, str(c), False
    elif is_space(c):
        yield State.delimiter, str(c), False


def word(c, state, state_data):
    if is_alphabet(c):
        yield State.word, xstr(state_data) + str(c), False
    else:
        yield from uninitialized(c, state, state_data)


def delimiter(c, state, state_data):
    if is_space(c):
        yield State.delimiter, xstr(state_data) + xstr(c), False
    else:
        yield from uninitialized(c, state, state_data)


def punctuation(c, state, state_data):
    if is_punctuation(c):
        yield State.punctuation, xstr(c), True
    else:
        yield from uninitialized(c, state, state_data)


state_processor = {
    State.word: word,
    State.delimiter: delimiter,
    State.punctuation: punctuation,
    State.uninitialized: uninitialized
}


def file_to_chars(file):
    for line in file:
        for char in line:
            yield char


def tokenize(chars):
    state = State.uninitialized
    state_data = None

    def make_token(state, before_state_data):
        if state == State.word:
            yield Token(token_type=TokenType.word, data=before_state_data)
        if state == State.delimiter:
            yield Token(token_type=TokenType.delimiter, data=before_state_data)
        if state == State.punctuation:
            yield Token(token_type=TokenType.punctuation, data=before_state_data)

    for c in chars:
        for new_state, new_state_data, emmit in state_processor[state](c, state, state_data):
            before_state = state
            before_state_data = state_data
            if before_state != new_state or emmit:
                yield from make_token(before_state, before_state_data)
            state = new_state
            state_data = new_state_data
    yield from make_token(state, state_data)

import pymorphy2
import pymorphy2_dicts_ru
import random

from synonym_dictionary_maker import read_dictionary
from tokenizer import tokenize, TokenType, Token, file_to_chars

morph = pymorphy2.MorphAnalyzer()

def find_synonim(word, syn):
    req_grammemes = word.tag.grammemes
    lexeme = morph.parse(syn)[0].lexeme
    max_compability = lexeme[0]
    max_compability_intersect = 0
    for l in lexeme:
        union = l.tag.grammemes & req_grammemes
        if (len(union) > max_compability_intersect):
            max_compability_intersect = len(union)
            max_compability = l
    return max_compability.word

def apply_dict(tokens, target_dict):
    replaces=dict((item['synonyms'][0], item) for item in target_dict)
    for token in tokens:
        if token.token_type == TokenType.word:
            word = morph.parse(token.data)
            if len(word) == 0:
                yield token
            else:
                word = word[0]
                normalized_word = word.normalized.word
                if normalized_word in replaces:
                    dictionary_item = replaces[normalized_word]
                    if random.random() < dictionary_item['probability']:
                        synonyms=dictionary_item['synonyms'][1:]
                        is_capitalized=token.data.istitle()
                        data=find_synonim(word, random.choice(synonyms))
                        if is_capitalized:
                            data=data.capitalize()
                        yield Token(token_type=TokenType.word, data=data)
                    else:
                        yield token
                else:
                    yield token
        else:
            yield token


def main():
    import argparse
    import sys

    parser = argparse.ArgumentParser(description='Add some integers.')
    parser.add_argument('--dictionary', action='store',
                        required=True,
                        nargs=1,
                        help='source synonym dictionary')
    parser.add_argument('--input', action='store',
                        required=False,
                        default=None,
                        nargs=1,
                        help='input file(default stdin)')
    parser.add_argument('--output', action='store',
                        default=None,
                        required=False,
                        nargs=1,
                        help='output file(default stdout)')
    parser.add_argument('--default-replace-probability', action='store',
                        default=[1.0],
                        type=float,
                        required=False,
                        nargs=1,
                        help='default probability for dictionary replacing')
    parser.add_argument('--shake-probability', action='store',
                        default=[0.0],
                        required=False,
                        nargs=1,
                        help='default probability for word shaking')
    args = parser.parse_args()
    tokens = tokenize(file_to_chars(open(args.input[0]) if args.input else sys.stdin))
    output_file = open(args.output[0], mode='w') if args.output else sys.stdout
    with open(args.dictionary[0]) as target_dict_file:
        target_tokens=apply_dict(tokens, read_dictionary(target_dict_file, args.default_replace_probability[0]))
        for token in target_tokens:
            print(token.data, file=output_file, end='', flush=True)


if __name__ == "__main__":
    main()

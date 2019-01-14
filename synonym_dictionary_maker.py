import re

from tokenizer import tokenize, TokenType, file_to_chars
import pymorphy2

morph = pymorphy2.MorphAnalyzer()

DEFAULT_SYN_DICTIONARY = './syn-dict.txt'


def have_digit(str):
    digits = "0123456789"
    for d in digits:
        if d in str:
            return True
    return False


def try_parse(value, default, type):
    try:
        return type(value)
    except ValueError:
        return default


synonyms_line_pattern = re.compile("^(?:(?=\D)[\w|\\|])*$")


def read_dictionary(file, default_probability=1.0):
    for line in file:
        # remove phrases and digits
        synonyms_string, *probability = line.strip().split(';')
        if synonyms_line_pattern.search(synonyms_string):
            yield {
                'synonyms': synonyms_string.strip().split('|'),
                'probability': try_parse(probability[0], default_probability, float) if len(
                    probability) > 0 else default_probability
            }


word_pattern = re.compile("^(?:(?=\D)\w)*$")


def filtrate_tokens(chars):
    for token in tokenize(chars):
        if token.token_type == TokenType.word \
                and word_pattern.search(token.data):
            word = morph.parse(token.data)[0]
            grammemes = word.tag.grammemes
            if 'PREP' not in grammemes \
                    and 'NPRO' not in grammemes \
                    and 'CONJ' not in grammemes \
                    and 'PRCL' not in grammemes:
                yield word.normalized.word


def get_normalized_set(text):
    return frozenset(filtrate_tokens(text))

def same_pos(word1, word2):
    word1=morph.parse(word1)
    word2=morph.parse(word2)
    if len(word1) > 0 and len(word2) > 0:
        return word1[0].tag.POS == word2[0].tag.POS
    else:
        return False

def reduce_syn_dic(chars, syn_dict):
    words = set(get_normalized_set(chars))
    for item in syn_dict:
        synonyms = item['synonyms']
        if len(words) == 0:
            break
        synonym = synonyms[0]
        if synonym in words:
            words.remove(synonym)
            synonyms = [s for s in synonyms if same_pos(s, synonym)]
            if len(synonyms) > 0:
                yield {
                    'synonyms': [synonym, *(s for s in synonyms if s != synonym)],
                    **item
                }


def print_dictionary(file, dictionary):
    for item in dictionary:
        print('{0};{1}'.format('|'.join(item['synonyms']), str(item['probability'])), file=file)


def main():
    import argparse
    import sys

    parser = argparse.ArgumentParser(description='Add some integers.')
    parser.add_argument('--dictionary', action='store',
                        default=[DEFAULT_SYN_DICTIONARY],
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
    args = parser.parse_args()
    input_file = open(args.input[0]) if args.input else sys.stdin
    output_file = open(args.output[0], mode='w') if args.output else sys.stdout
    with open(args.dictionary[0]) as dict_file:
        reduced_dictionary = reduce_syn_dic(file_to_chars(input_file), read_dictionary(dict_file))
        print_dictionary(output_file, reduced_dictionary)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3

# Filter blank line-separated sentence-per-line text documents.

import sys
import os
import re

from string import punctuation
from langdetect import detect


# Regex definition for --min-words option
FI_WORD_RE = re.compile(r'[a-zåäö]{2,}')


FREQUENT_FI_WORDS = set([
    'aika',
    'aikana',
    'aina',
    'ainakin',
    'ei',
    'eikä',
    'eivät',
    'eli',
    'en',
    'enemmän',
    'ennen',
    'ensi',
    'eri',
    'esimerkiksi',
    'että',
    'ettei',
    'hän',
    'hänen',
    'he',
    'hyvä',
    'hyvin',
    'ihan',
    'ja',
    'jälkeen',
    'jo',
    'joka',
    'jonka',
    'jopa',
    'jos',
    'jossa',
    'jotka',
    'kaikki',
    'kaksi',
    'kanssa',
    'kaupungin',
    'kertoo',
    'koko',
    'kolme',
    'koska',
    'kuin',
    'kuitenkin',
    'kun',
    'kyllä',
    'lähes',
    'lisäksi',
    'mitä',
    'muassa',
    'mukaan',
    'mutta',
    'muun',
    'myös',
    'ne',
    'niin',
    'noin',
    'nyt',
    'ole',
    'olen',
    'oli',
    'olisi',
    'olivat',
    'olla',
    'ollut',
    'on',
    'osa',
    'ovat',
    'paljon',
    'pitää',
    'poliisi',
    'saa',
    'sai',
    'sanoo',
    'se',
    'sekä',
    'sen',
    'siinä',
    'sillä',
    'sitä',
    'sitten',
    'suomen',
    'suomessa',
    'tai',
    'tällä',
    'tämä',
    'tämän',
    'tänä',
    'tässä',
    'tulee',
    'tuli',
    'uusi',
    'vaan',
    'vaikka',
    'vain',
    'vielä',
    'viime',
    'voi',
    'vuoden',
    'vuonna',
    'vuotta',
    'yksi',
    'yli',
])


def argparser():
    from argparse import ArgumentParser
    ap = ArgumentParser(description='Filter documents.')
    ap.add_argument('-a', '--avg-len', default=None, type=int,
                    help='minimum average sentence length (lowercase words)')
    ap.add_argument('-d', '--digit-ratio', default=None, type=float,
                    help='maximum ratio of digit characters')
    ap.add_argument('-f', '--frequent-ratio', default=None, type=float,
                    help='minimum ratio of frequent Finnish words')
    ap.add_argument('-i', '--invert', default=False, action='store_true',
                    help='invert filter criteria')
    ap.add_argument('-l', '--langdetect', default=False, action='store_true',
                    help='run langdetect to filter to Finnish')
    ap.add_argument('-p', '--punct-ratio', default=None, type=float,
                    help='maximum ratio of punctuation characters')
    ap.add_argument('-s', '--min-sents', default=None, type=int,
                    help='minimum number of sentences')
    ap.add_argument('-S', '--max-sents', default=None, type=int,
                    help='maximum number of sentences')
    ap.add_argument('-t', '--min-toks', default=None, type=int,
                    help='minimum number of tokens')
    ap.add_argument('-T', '--max-toks', default=None, type=int,
                    help='maximum number of tokens')
    ap.add_argument('-u', '--upper-ratio', default=None, type=float,
                    help='maximum ratio of uppercase characters')
    ap.add_argument('-w', '--min-words', default=None, type=int,
                    help='minimum number of lowercase Finnish words')
    ap.add_argument('file', nargs='+')
    return ap


def num_toks(sentences):
    return sum(len(s.split()) for s in sentences)


def num_words(sentences):
    return sum(len(FI_WORD_RE.findall(s)) for s in sentences)


def avg_len(sentences):
    return num_words(sentences) / len(sentences)


def char_count(sentences):
    return sum(len(s) for s in sentences)


def uppercase_ratio(sentences):
    return sum(c.isupper() for s in sentences for c in s)/char_count(sentences)


def digit_ratio(sentences):
    return sum(c.isdigit() for s in sentences for c in s)/char_count(sentences)


def punctuation_ratio(sentences):
    punct = set(punctuation)
    return sum(c in punct for s in sentences for c in s)/char_count(sentences)


def frequent_ratio(sentences):
    words = [w for s in sentences for w in FI_WORD_RE.findall(s)]
    return sum(w in FREQUENT_FI_WORDS for w in words)/len(words)


def detect_lang(sentences):
    try:
        return detect(' '.join(sentences))
    except:
        return None


def filter_sentences(sentences, options):
    if options.avg_len is not None and avg_len(sentences) < options.avg_len:
        return True
    if options.min_sents is not None and len(sentences) < options.min_sents:
        return True
    if options.max_sents is not None and len(sentences) > options.max_sents:
        return True
    if options.min_toks is not None and num_toks(sentences) < options.min_toks:
        return True
    if options.max_toks is not None and num_toks(sentences) > options.max_toks:
        return True
    if (options.punct_ratio is not None and 
        punctuation_ratio(sentences) > options.punct_ratio):
        return True
    if (options.upper_ratio is not None and 
        uppercase_ratio(sentences) > options.upper_ratio):
        return True
    if (options.digit_ratio is not None and 
        digit_ratio(sentences) > options.digit_ratio):
        return True
    if (options.min_words is not None and 
        num_words(sentences) < options.min_words):
        return True
    if (options.frequent_ratio is not None and
        frequent_ratio(sentences) < options.frequent_ratio):
        return True
    if options.langdetect and detect_lang(sentences) != 'fi':
        return True
    return False


def process_sentences(sentences, options):
    skip = filter_sentences(sentences, options)
    if options.invert:
        skip = not skip
    if not skip:
        for s in sentences:
            print(s)
        if sentences:
            print()


def process(fn, options):
    with open(fn) as f:
        sentences = []
        for l in f:
            l = l.rstrip()
            if l and not l.isspace():
                sentences.append(l)
            else:
                if sentences:
                    process_sentences(sentences, options)
                sentences = []
        if sentences:
            process_sentences(sentences, options)


def main(argv):
    args = argparser().parse_args(argv[1:])
    for fn in args.file:
        print('processing {} ...'.format(os.path.basename(fn)),
              file=sys.stderr)
        process(fn, args)
        print('completed {}.'.format(os.path.basename(fn)),
              file=sys.stderr)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))

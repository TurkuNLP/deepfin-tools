#!/usr/bin/env python3

import sys
import os
import fileinput
import re

from string import punctuation

from langdetect import detect, DetectorFactory

# Make langdetect deterministic
DetectorFactory.seed = 0

FI_WORD_RE = re.compile(r'\b[a-zA-ZåäöÅÄÖ][a-zåäö]+\b')

NON_FI_LETTER = re.compile(r'[^\W\d_a-zA-ZåäöÅÄÖ]')


PUNCT = set(punctuation)


def argparser():
    from argparse import ArgumentParser
    ap = ArgumentParser(description='Filter sentences.')
    ap.add_argument('-d', '--digit-ratio', default=None, type=float,
                    help='maximum ratio of digit characters')
    ap.add_argument('-f', '--foreign-ratio', default=None, type=float,
                    help='maximum ratio of non-Finnish alphabetic characters')
    ap.add_argument('-i', '--invert', default=False, action='store_true',
                    help='invert filter criteria')
    ap.add_argument('-l', '--langdetect', default=False, action='store_true',
                    help='run langdetect to filter to Finnish')
    ap.add_argument('-L', '--limit', default=None, type=int,
                    help='limit number of documents to process')    
    ap.add_argument('-p', '--punct-ratio', default=None, type=float,
                    help='maximum ratio of punctuation characters')
    ap.add_argument('-t', '--min-toks', default=None, type=int,
                    help='minimum number of tokens')
    ap.add_argument('-T', '--max-toks', default=None, type=int,
                    help='maximum number of tokens')
    ap.add_argument('-w', '--min-words', default=None, type=int,
                    help='minimum number of Finnish words')
    ap.add_argument('-W', '--max-words', default=None, type=int,
                    help='maximum number of Finnish words')
    ap.add_argument('-u', '--upper-ratio', default=None, type=float,
                    help='maximum ratio of uppercase characters')
    ap.add_argument('file', nargs='*')
    return ap


def uppercase_ratio(sentence):
    return sum(c.isupper() for c in sentence)/len(sentence)


def digit_ratio(sentence):
    return sum(c.isdigit() for c in sentence)/len(sentence)


def punctuation_ratio(sentence):
    return sum(c in PUNCT for c in sentence)/len(sentence)


def num_toks(sentence):
    return len(sentence.split())


def num_words(sentence):
    return len(FI_WORD_RE.findall(sentence))


def foreign_ratio(sentence):
    return len(NON_FI_LETTER.findall(sentence))/len(sentence)


def filter_sentence(sentence, options):
    if (options.punct_ratio is not None and
        punctuation_ratio(sentence) > options.punct_ratio):
        return True
    if (options.upper_ratio is not None and
        uppercase_ratio(sentence) > options.upper_ratio):
        return True
    if (options.digit_ratio is not None and
        digit_ratio(sentence) > options.digit_ratio):
        return True
    if (options.foreign_ratio is not None and
        foreign_ratio(sentence) > options.foreign_ratio):
        return True
    if (options.min_toks is not None and 
        num_toks(sentence) < options.min_toks):
        return True
    if (options.max_toks is not None and 
        num_toks(sentence) > options.max_toks):
        return True
    if (options.min_words is not None and 
        num_words(sentence) < options.min_words):
        return True
    if (options.max_words is not None and 
        num_words(sentence) > options.max_words):
        return True
    if options.langdetect:
        try:
            lang = detect(sentence)
        except:
            lang = None
        if lang != "fi":
            return True
    return False


def process(fn, options):
    with open(fn) as f:
        for l in f:
            l = l.rstrip()
            skip = filter_sentence(l, options)
            if options.invert:
                skip = not skip
            if not skip:
                print(l)


def main(argv):
    args = argparser().parse_args(argv[1:])
    if args.limit is not None:
        raise NotImplementedError
    for fn in args.file:
        process(fn, args)
    if len(args.file) == 0:
        process('/dev/stdin', args)    # sorry
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))

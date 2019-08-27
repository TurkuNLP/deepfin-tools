#!/usr/bin/env python3

import sys
import os
import pickle

from random import random

from common import Word, is_document_boundary


def argparser():
    from argparse import ArgumentParser
    ap = ArgumentParser(description='Sample CoNLL-U data')
    ap.add_argument('ratio', type=float)
    ap.add_argument('data', nargs='+')
    return ap


def process_document(sentences, options):
    if random() > options.ratio:
        return
    for comments, words in sentences:
        for c in comments:
            print(c)
        for w in words:
            print('\t'.join(w))
        print()


def sample(fn, options):
    sentences, comments, words = [], [], []
    with open(fn) as f:
        for ln, l in enumerate(f, start=1):
            l = l.rstrip('\n')
            if not l or l.isspace():
                sentences.append((comments, words))
                comments, words = [], []
            elif l.startswith('#'):
                if is_document_boundary(l):
                    if sentences:
                        process_document(sentences, options)
                    sentences = []
                comments.append(l)
            else:
                words.append(Word(*l.split('\t')))
        if sentences:
            process_document(sentences, options)
        

def main(argv):
    args = argparser().parse_args(argv[1:])
    for fn in args.data:
        sample(fn, args)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))

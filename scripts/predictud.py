#!/usr/bin/env python3

# Make predictions based on text from CoNLL-U data.

import sys
import os
import gzip
import re

from collections import Counter
from logging import warning, error

from common import Word, load_model


TEXT_COMMENT = '# text = '


def argparser():
    from argparse import ArgumentParser
    ap = ArgumentParser()
    ap.add_argument('-f', '--filter', metavar='CLASS', default=None,
                    help='filter documents with CLASS')
    ap.add_argument('-T', '--threshold', default=None, type=float,
                    help='only filter when abs(decision) > THRESHOLD')
    ap.add_argument('-t', '--tokenized', default=False, action='store_true',
                    help='use tokenized text (default raw)')
    ap.add_argument('model')
    ap.add_argument('data', nargs='+')
    return ap


def get_raw_text(comments):
    text_lines = [c for c in comments if c.startswith(TEXT_COMMENT)]
    if len(text_lines) != 1:
        raise ValueError('{} text lines'.format(len(text_lines)))
    text_line = text_lines[0]
    return text_line[len(TEXT_COMMENT):]


def get_document_text(sentences, options):
    texts = []
    for comments, words in sentences:
        if options.tokenized:
            texts.append(' '.join(w.form for w in words))
        else:
            texts.append(get_raw_text(comments))
    return ' '.join(texts)


def process_document(sentences, clf, vecf, options):
    text = get_document_text(sentences, options)
    X = vecf.transform([text])
    class_ = clf.predict(X)
    value = clf.decision_function(X)
    if ((options.filter is not None and options.filter == class_) and
        (options.threshold is None or abs(value) > options.threshold)):
        return 0
    else:
        print('# predicted_class = {}'.format(class_))
        print('# predicted_value = {}'.format(value))
        for comments, words in sentences:
            for c in comments:
                print(c)
            for w in words:
                print('\t'.join(w))
            print()
        return 1


def is_document_boundary(comment):
    return (comment.startswith('# doc_id = ') or
            comment.startswith('# <doc '))


def process_stream(f, name, *args):
    total_count, output_count = 0, 0
    document_id, document_info, sentences = None, None, []
    comments, words = [], []
    for ln, l in enumerate(f, start=1):
        l = l.rstrip('\n')
        if not l or l.isspace():
            sentences.append((comments, words))
            comments, words = [], []
        elif l.startswith('#'):
            if is_document_boundary(l):
                if sentences:
                    output_count += process_document(sentences, *args)
                    total_count += 1
                sentences = []
            comments.append(l)
        else:
            words.append(Word(*l.split('\t')))
    if sentences:
        output_count += process_document(sentences, *args)
        total_count += 1
    print('{}: output {}/{} ({:.1%})'.format(
        os.path.basename(name), output_count, total_count,
        output_count/total_count), file=sys.stderr)


def process(fn, *args):
    if not fn.endswith('.gz'):
        with open(fn) as f:
            return process_stream(f, fn, *args)
    else:
        with gzip.open(fn, 'rt') as f:
            return process_stream(f, fn, *args)


def main(argv):
    args = argparser().parse_args(argv[1:])
    clf, vecf = load_model(args.model)
    for fn in args.data:
        print('processing {} ...'.format(os.path.basename(fn)),
              file=sys.stderr)
        process(fn, clf, vecf, args)
        print('completed {}.'.format(os.path.basename(fn)),
              file=sys.stderr)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))

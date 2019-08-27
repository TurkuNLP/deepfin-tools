#!/usr/bin/env python3

# Filter CoNLL-U documents.

import sys
import os
import gzip
import re

from collections import Counter, defaultdict
from logging import warning, error

from common import Word, load_model
from filterdocs import argparser, filter_sentences


TEXT_COMMENT = '# text = '


def get_raw_text(comments):
    text_lines = [c for c in comments if c.startswith(TEXT_COMMENT)]
    if len(text_lines) != 1:
        raise ValueError('{} text lines'.format(len(text_lines)))
    text_line = text_lines[0]
    return text_line[len(TEXT_COMMENT):]


def get_sentence_texts(sentences, options):
    texts = []
    for comments, words in sentences:
        if getattr(options, 'tokenized', None):
            texts.append(' '.join(w.form for w in words))
        else:
            texts.append(get_raw_text(comments))
    return texts


def process_document(sentences, stats, options):
    sentence_texts = get_sentence_texts(sentences, options)
    fail = filter_sentences(sentence_texts, options)
    if fail is None:
        result = 'pass-all'
        skip = False
    else:
        result = 'fail-{}'.format(fail)
        skip = True
    stats[result] += 1
    if options.invert:
        skip = not skip
    if skip:
        return 0
    else:
        print('# filter_result = {}'.format(result))
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


def process_stream(f, name, options):
    stats = defaultdict(int)
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
                    output_count += process_document(sentences, stats, options)
                    total_count += 1
                sentences = []
                if options.limit is not None and total_count >= options.limit:
                    break
            comments.append(l)
        else:
            words.append(Word(*l.split('\t')))
        if ln % 100000 == 0:
            print('processed {} lines ({} docs) ...'.format(ln, total_count),
                  file=sys.stderr, flush=True)
    if sentences:
        output_count += process_document(sentences, stats, options)
        total_count += 1
    for k, v in stats.items():
        print('{}:{}\t{}'.format(os.path.basename(name), k, v),
              file=sys.stderr, flush=True)
    print('{}: output {}/{} ({:.1%})'.format(
        os.path.basename(name), output_count, total_count,
        output_count/total_count), file=sys.stderr, flush=True)


def process(fn, *args):
    if not fn.endswith('.gz'):
        with open(fn) as f:
            return process_stream(f, fn, *args)
    else:
        with gzip.open(fn, 'rt') as f:
            return process_stream(f, fn, *args)


def main(argv):
    args = argparser().parse_args(argv[1:])
    for fn in args.file:
        print('processing {} ...'.format(os.path.basename(fn)),
              file=sys.stderr, flush=True)
        process(fn, args)
        print('completed {}.'.format(os.path.basename(fn)),
              file=sys.stderr, flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))

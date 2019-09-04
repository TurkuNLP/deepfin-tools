#!/usr/bin/env python3

# Filter CoNLL-U documents based on sentence statistics.

import sys
import os
import gzip
import re

from collections import Counter, defaultdict
from logging import warning, error

from common import Word, is_document_boundary
from filtersents import filter_sentence
from filteruddocs import get_sentence_texts


NOUN_UPOS = set(['NOUN', 'PROPN'])

VERB_UPOS = set(['VERB', 'AUX'])


def argparser():
    from filtersents import argparser as fs_argparser
    ap = fs_argparser()
    ap.add_argument('-r', '--reject-ratio', default=0.5, type=float,
                    help='maximum ratio of rejected to all sentences')
    ap.add_argument('-m', '--max-reject', default=None, type=int,
                    help='maximum number of rejected sentences')
    ap.add_argument('-n', '--min-nouns', default=None, type=int,
                    help='minimum number of nouns')
    ap.add_argument('-v', '--min-verbs', default=None, type=int,
                    help='minimum number of verbs')
    return ap


def upos_count(words, upos):
    return sum(w.upos in upos for w in words)


def filter_on_parse(words, options):
    if (options.min_nouns is not None and
        upos_count(words, NOUN_UPOS) < options.min_nouns):
        return True
    if (options.min_verbs is not None and
        upos_count(words, VERB_UPOS) < options.min_verbs):
        return True
    return False


def process_document(sentences, stats, options):
    sentence_texts = get_sentence_texts(sentences, options)
    failed, passed = 0, 0
    for sentence, sentence_text in zip(sentences, sentence_texts):
        comments, words = sentence
        if filter_sentence(sentence_text, options):
            comments.append('# sentfilter = reject-text')
            failed += 1
        elif filter_on_parse(words, options):
            comments.append('# sentfilter = reject-parse')
            failed += 1
        else:
            comments.append('# sentfilter = pass')
            passed += 1
    ratio = failed / (failed+passed)
    if ((ratio < options.reject_ratio) and
        (options.max_reject is None or failed < options.max_reject)):
        result = 'pass'
        skip = False
    else:
        result = 'fail'
        skip = True
    stats[result] += 1
    if options.invert:
        skip = not skip
    if skip:
        return 0
    else:
        print('# sentfilter_result = {} ({}/{} = {:.1%})'.format(
                result, failed, failed+passed, ratio))
        for comments, words in sentences:
            for c in comments:
                print(c)
            for w in words:
                print('\t'.join(w))
            print()
        return 1


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

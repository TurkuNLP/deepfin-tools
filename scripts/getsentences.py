#!/usr/bin/env python3

# Get sentences from CoNLL-U data.

import sys
import os
import gzip
import re

from collections import Counter, namedtuple
from logging import warning, error


TEXT_COMMENT = '# text = '


DOC_COLLECTION_RE = re.compile(r'^#\s+<doc\s+collection="([^"]+)"\s+url="(.*)">')

DOC_CRAWL_RE = re.compile(r'^#\s+<doc\s+id="([^"]+)"\s.*?\burl="(.*?)"\s+langdiff="([^"]+)"\s*>')

DOC_CRAWL2_RE = re.compile(r'^#\s+<doc\b.*\bfile="([^"]+)".*\burn="<(.*?)>".*>')

DOC_CRAWL3_RE = re.compile(r'^#\s+<doc\b.*\burn="<(.*?)>".*\bfile="([^"]+)".*>')

# https://universaldependencies.org/format.html
CONLLU_FIELDS = [
    'id',
    'form',
    'lemma',
    'upos',
    'xpos',
    'feats',
    'head',
    'deprel',
    'deps',
    'misc',
]


Word = namedtuple('Word', CONLLU_FIELDS)


LABEL_COMMENTS = [
    '# filter_result =',
    '# sentfilter_result =',
    '# predicted_class =',
    '# predicted_value =',
    '# sentfilter =',
]


def argparser():
    from argparse import ArgumentParser
    ap = ArgumentParser(description='Get text from CoNLL-U data')
    ap.add_argument('-l', '--labels', default=False, action='store_true',
                    help='include document label comments')
    ap.add_argument('-t', '--tokenized', default=False, action='store_true',
                    help='get tokenized text (default raw)')
    ap.add_argument('data', nargs='+')
    return ap


def get_text(comments):
    text_lines = [c for c in comments if c.startswith(TEXT_COMMENT)]
    if len(text_lines) != 1:
        raise ValueError('{} text lines'.format(len(text_lines)))
    text_line = text_lines[0]
    return text_line[len(TEXT_COMMENT):]


def get_label_comments(comments):
    return [
        c for c in comments 
        if any(c.startswith(l) for l in LABEL_COMMENTS)
    ]

def process_document(sentences, options):
    for i, (comments, words) in enumerate(sentences):
        if options.labels and i == 0:
            for c in get_label_comments(comments):
                print(c)
        if options.tokenized:
            raise NotImplementedError
        else:
            print(get_text(comments))
    print()


def is_document_boundary(comment):
    return (comment.startswith('# doc_id = ') or
            comment.startswith('# <doc '))


def process_stream(f, options):
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
                    process_document(sentences, options)
                sentences = []
            comments.append(l)
        else:
            words.append(Word(*l.split('\t')))
    if sentences:
        process_document(sentences, options)


def process(fn, options):
    if not fn.endswith('.gz'):
        with open(fn) as f:
            return process_stream(f, options)
    else:
        with gzip.open(fn, 'rt') as f:
            return process_stream(f, options)


def main(argv):
    args = argparser().parse_args(argv[1:])
    for fn in args.data:
        print('processing {} ...'.format(os.path.basename(fn)),
              file=sys.stderr)
        process(fn, args)
        print('completed {}.'.format(os.path.basename(fn)),
              file=sys.stderr)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))

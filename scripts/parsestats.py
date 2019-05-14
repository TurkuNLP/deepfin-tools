#!/usr/bin/env python3

# Special-purpose scripts for getting statistics from parsebank data.

import sys
import os
import gzip
import re
import json
import urllib.parse

from collections import Counter, namedtuple
from logging import warning, error


DOC_COLLECTION_RE = re.compile(r'^#\s+<doc\s+collection="([^"]+)"\s+url="(.*)">')

DOC_CRAWL_RE = re.compile(r'^#\s+<doc\s+id="([^"]+)"\s.*?\burl="(.*?)"\s+langdiff="([^"]+)"\s*>')

DOC_CRAWL2_RE = re.compile(r'^#\s+<doc\b.*\bfile="([^"]+)".*\burn="<(.*?)>".*>')

DOC_CRAWL3_RE = re.compile(r'^#\s+<doc\b.*\burn="<(.*?)>".*\bfile="([^"]+)".*>')

URL_RE = re.compile(r'^s?http://', re.U)

TAG_RE = re.compile(r'^[<\[]/?[a-z]+', re.U)    # "<html", "</html", "[bold", ...

WORD_RE = re.compile(r'^[a-zA-ZäöÄÖ-]+$', re.U)

NUMBER_RE = re.compile(r'^-?[0-9][0-9,. -]*$', re.U)

WORDNUM_RE = re.compile(r'^[a-zA-ZäöÄ0-9-][a-zA-ZäöÄÖ0-9,.-]*$', re.U)    # "1200-luku"

PUNCT_RE = re.compile(r'^[.,:;()\[\]%]+$', re.U)

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


def argparser():
    from argparse import ArgumentParser
    ap = ArgumentParser(description='Take statistics from CoNLL-U data')
    ap.add_argument('data', nargs='+')
    return ap


def sentence_statistics(sentences):
    stats = Counter()
    for i in ['sent-len', 'word-len', 'upos-count', 'dep-count']:
        stats[i] = Counter()
    stats['sent-num'] = len(sentences)

    for comments, words in sentences:
        stats['sent-len'][len(words)] += 1
        stats['token-count'] += 1
        for w in words:
            stats['word-len'][len(w.form)] += 1
            stats['upos-count'][w.upos] += 1
            stats['dep-count'][w.deprel] += 1
            if URL_RE.match(w.form):
                stats['url-count'] += 1
            elif TAG_RE.match(w.form):
                stats['tag-count'] += 1
            elif WORD_RE.match(w.form):
                stats['word-count'] += 1
            elif NUMBER_RE.match(w.form):
                stats['number-count'] += 1
            elif WORDNUM_RE.match(w.form):
                stats['wordnum-count'] += 1
            elif PUNCT_RE.match(w.form):
                stats['punct-count'] += 1
            else:
                stats['other-count'] += 1
    return stats


def process_document(document_id, document_info, sentences):
    document_id = document_id.replace('\t', ' ').replace('\n', ' ')
    document_info = document_info.replace('\t', ' ').replace('\n', ' ')
    stats = sentence_statistics(sentences)
    print('{}\t{}\t{}'.format(document_id, document_info,
                              json.dumps(stats, sort_keys=True)))


def is_document_boundary(comment):
    return comment.startswith('# <doc ')


def parse_document_comment(comment):
    m = DOC_COLLECTION_RE.match(comment)
    if m:
        coll, page = m.group(1), m.group(2)
        if coll == 'wiki':
            page = urllib.parse.quote(page.replace(' ', '_'))
        id_ = '{}/{}'.format(coll, page)
        langdiff = '_'
        return id_, langdiff
    m = DOC_CRAWL_RE.match(comment)
    if m:
        id_, langdiff = '{}/{}'.format(m.group(1), m.group(2)), m.group(3)
        return id_, langdiff
    m = DOC_CRAWL2_RE.match(comment)
    if m:
        id_, langdiff = '{}/{}'.format(m.group(1), m.group(2)), '_'
        return id_, langdiff
    m = DOC_CRAWL3_RE.match(comment)
    if m:
        id_, langdiff = '{}/{}'.format(m.group(2), m.group(1)), '_'
        return id_, langdiff
    error('Failed to parse document comment: "{}"'.format(comment))
    return '<UNKNOWN>', '<UNKNOWN>'


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
                    process_document(document_id, document_info, sentences)
                document_id, document_info = parse_document_comment(l)
                sentences = []
            comments.append(l)
        else:
            words.append(Word(*l.split('\t')))
    if sentences:
        process_document(document_id, document_info, sentences)


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

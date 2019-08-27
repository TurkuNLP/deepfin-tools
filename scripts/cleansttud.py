#!/usr/bin/env python3

# Clean up STT sentences.

import sys
import os
import re
import gzip

from logging import warning

from common import Word

TAG_LINE_RE = re.compile(r'^[a-zäöå0-9, ]+$')

PUBLISHER_RE = re.compile(r'.*\(STT.*')

AUTHOR_RE = re.compile(r'^\s*(-+\s*)?\S+\s*$')

TAIL_WARN_LENGTH = 5

COMMENT_START = '//'
COMMENT_END = '//'

TEXT_COMMENT = '# text = '

DOCSTART_COMMENTS = [
    '# doc_id = ',
    '# zipfilename = ',
    '# filename = ',
]


def argparser():
    from argparse import ArgumentParser
    ap = ArgumentParser(description='Clean up STT sentences.')
    ap.add_argument('file', nargs='+')
    return ap


def text(sentence):
    comments, words = sentence
    text_lines = [c for c in comments if c.startswith(TEXT_COMMENT)]
    if len(text_lines) != 1:
        raise ValueError('{} text lines'.format(len(text_lines)))
    text_line = text_lines[0]
    return text_line[len(TEXT_COMMENT):]


def texts(sentences):
    return [text(s) for s in sentences]


def docstart_comments(sentences):
    if not sentences:
        return []
    first_comments, first_words = sentences[0]
    start_comments = [
        c for c in first_comments 
        if any(c.startswith(s) for s in DOCSTART_COMMENTS)
    ]
    return start_comments


def process_sentences(sentences):
    # Remove tags and comment lines from document, print out rest.
    # Document example:
    # """
    # puolueet
    # kiinan puoluekokous
    # ///jatkettu versio///
    # Kahdeksan voimahahmoa jättämässä puolueen johtopaikat Kiinassa
    # Peking, 16.
    # 10. (STT—Reuter—TT—AFP)
    # """

    start_comments = docstart_comments(sentences)

    # skip initial tag lines
    i = 0
    while i < len(sentences) and TAG_LINE_RE.match(text(sentences[i])):
        i += 1
    if i >= len(sentences):
        warning('Document without content: """\n{}\n"""'.format(
            '\n'.join(texts(sentences))))
        return []

    # find start of body text, demarcated by publisher tag (e.g. "(STT)")
    j = i
    while j < len(sentences) and not PUBLISHER_RE.match(text(sentences[j])):
        j += 1
    if j < len(sentences):
        header = sentences[i:j+1]
        body = sentences[j+1:]
    else:
        # happens too often to warn
        # warning('Document without tag: """\n{}\n"""'.format(
        #    '\n'.join(texts(sentences))))
        header = []
        body = sentences[i:]

    # strip trailing non-body content
    i = len(body)-1
    while i >= 0:
        if PUBLISHER_RE.match(text(body[i])):
            if len(body[i:]) > TAIL_WARN_LENGTH:
                warning('stripping long tail: {}'.format(texts(body[i:])))
            body = body[:i]
        i -= 1
    while len(body) > 0 and AUTHOR_RE.match(text(body[-1])):
        body = body[:-1]

    # transfer document start comments if skipped
    if body and not docstart_comments(body):
        for c in start_comments:
            print(c)

    for comments, words in body:
        for c in comments:
            print(c)
        for w in words:
            print('\t'.join(w))
        print()


def is_document_boundary(comment):
    return comment.startswith('# doc_id = ') or comment.startswith('# <doc ')
        

def process_stream(f, options):
    sentences, comments, words = [], [], []
    for ln, l in enumerate(f, start=1):
        l = l.rstrip('\n')
        if not l or l.isspace():
            sentences.append((comments, words))
            comments, words = [], []
        elif l.startswith('#'):
            if is_document_boundary(l):
                if sentences:
                    process_sentences(sentences)
                sentences = []
            comments.append(l)
        else:
            words.append(Word(*l.split('\t')))
    if sentences:
        process_sentences(sentences)


def process(fn, options):
    if not fn.endswith('.gz'):
        with open(fn) as f:
            return process_stream(f, options)
    else:
        with gzip.open(fn, 'rt') as f:
            return process_stream(f, options)


def main(argv):
    args = argparser().parse_args(argv[1:])
    for fn in args.file:
        process(fn, args)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))

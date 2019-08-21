#!/usr/bin/env python3

# Clean up STT sentences.

import sys
import os
import re

from logging import warning


TAG_LINE_RE = re.compile(r'^[a-zäöå0-9, ]+$')

PUBLISHER_RE = re.compile(r'.*\(STT.*')

AUTHOR_RE = re.compile(r'^\s*(-+\s*)?\S+\s*$')

TAIL_WARN_LENGTH = 5

COMMENT_START = '//'
COMMENT_END = '//'


def argparser():
    from argparse import ArgumentParser
    ap = ArgumentParser(description='Clean up STT sentences.')
    ap.add_argument('file', nargs='+')
    return ap


def cleanup(sentences):
    # Remove tags and comment lines from document.
    # Document example:
    # """
    # puolueet
    # kiinan puoluekokous
    # ///jatkettu versio///
    # Kahdeksan voimahahmoa jättämässä puolueen johtopaikat Kiinassa
    # Peking, 16.
    # 10. (STT—Reuter—TT—AFP)
    # """

    # skip initial tag lines
    i = 0
    while i < len(sentences) and TAG_LINE_RE.match(sentences[i]):
        i += 1
    if i >= len(sentences):
        warning('Document without content: """\n{}\n"""'.format(
            '\n'.join(sentences)))
        return []

    # find start of body text, demarcated by publisher tag (e.g. "(STT)")
    j = i
    while j < len(sentences) and not PUBLISHER_RE.match(sentences[j]):
        j += 1
    if j < len(sentences):
        header = sentences[i:j+1]
        body = sentences[j+1:]
    else:
        # happens too often to warn
        # warning('Document without tag: """\n{}\n"""'.format(
        #    '\n'.join(sentences)))
        header = []
        body = sentences[i:]

    # strip trailing non-body content
    i = len(body)-1
    while i >= 0:
        if PUBLISHER_RE.match(body[i]):
            if len(body[i:]) > TAIL_WARN_LENGTH:
                warning('stripping long tail: {}'.format(body[i:]))
            body = body[:i]
        i -= 1
    while len(body) > 0 and AUTHOR_RE.match(body[-1]):
        body = body[:-1]

    return body


def process(fn, options):
    with open(fn) as f:
        sentences = []
        for l in f:
            l = l.rstrip()
            if l and not l.isspace():
                sentences.append(l)
            else:
                sentences = cleanup(sentences)
                for s in sentences:
                    print(s)
                if sentences:
                    print()
                sentences = []


def main(argv):
    args = argparser().parse_args(argv[1:])
    for fn in args.file:
        process(fn, args)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))

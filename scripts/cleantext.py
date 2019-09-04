#!/usr/bin/env python3

import sys
import unicodedata
import re

from ftfy import fix_text


# Common markdown-style tags
MARKDOWN_TAG_RE = re.compile(r'\[\/?(?:quote|muokkaa)\b[^\[\]]*\]', re.I)

# Common HTML tags
HTML_TAG_RE = re.compile(r'<\/?(?:div|p|span|br|font|b|a)\b[^<>]*>', re.I)

# Regex definition for --min-words option
FI_LC_WORD_RE = re.compile(r'\b[a-zåäö]{2,}\b')

FI_ALNUM = re.compile(r'[a-zåäö0-9]', re.I)

# https://stackoverflow.com/a/93029
ALL_CHARS = (chr(i) for i in range(sys.maxunicode))

CONTROL_CHARS = ''.join(c for c in ALL_CHARS 
                        if unicodedata.category(c) == 'Cc')

CONTROL_CHAR_RE = re.compile('[{}]'.format(re.escape(CONTROL_CHARS)))


def argparser():
    from argparse import ArgumentParser
    ap = ArgumentParser(description='Clean sentece-per-line text')
    ap.add_argument('-w', '--min-words', default=2, type=int,
                    help='minimum number of lowercase words (head/tail trim)')
    ap.add_argument('-f', '--fix-text', default=False, action='store_true',
                    help='run ftfy.fix_text() on text')
    ap.add_argument('file', nargs='+')
    return ap


def lc_word_count(s):
    return len(FI_LC_WORD_RE.findall(s))


def remove_tags(sentences, options):
    cleaned = []
    # remove common markdown and HTML tags
    for s in sentences:
        s = MARKDOWN_TAG_RE.sub('', s)
        s = HTML_TAG_RE.sub('', s)
        if s and not s.isspace():
            cleaned.append(s)
    return cleaned


def trim_head_tail(sentences, options):
    # remove header/trailer lines lacking minimum number of words
    i = 0
    while (i < len(sentences) and
           lc_word_count(sentences[i]) < options.min_words):
        i += 1
    header, sentences = sentences[:i], sentences[i:]
    j = len(sentences) - 1
    while j >= 0 and lc_word_count(sentences[j]) < options.min_words:
        j -= 1
    sentences, trailer = sentences[:j+1], sentences[j+1:]
    return sentences


def remove_noalnum(sentences, options):
    # remove lines without Finnish alphanumeric characters
    return [s for s in sentences if FI_ALNUM.search(s) is not None]


def fix_texts(sentences, options):
    return [fix_text(s) for s in sentences]


def strip_control_chars(sentences, options):
    return [CONTROL_CHAR_RE.sub('', s) for s in sentences]


def process(fn, options):
    sentences = []
    with open(fn) as f:
        for ln, l in enumerate(f, start=1):
            l = l.rstrip('\n')
            if l and not l.isspace():
                sentences.append(l)
            else:
                sentences = remove_tags(sentences, options)
                sentences = trim_head_tail(sentences, options)
                sentences = remove_noalnum(sentences, options)
                if options.fix_text:
                    sentences = fix_texts(sentences, options)
                sentences = strip_control_chars(sentences, options)
                if sentences:
                    for s in sentences:
                        print(s)
                    print(l)
                sentences = []


def main(argv):
    args = argparser().parse_args(argv[1:])
    for fn in args.file:
        process(fn, args)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))

#!/usr/bin/env python

# Split text with sentence per line and documents separated by blank lines

import sys
import os


def argparser():
    from argparse import ArgumentParser
    ap = ArgumentParser(description='Split text by document')
    ap.add_argument('-w', '--width', default=3, type=int,
                    help='minimum number of digits in part identifier')
    ap.add_argument('-d', '--max-documents', default=100000, type=int)
    ap.add_argument('-s', '--max-sentences', default=None, type=int)
    ap.add_argument('-t', '--max-tokens', default=None, type=int)
    ap.add_argument('file')
    return ap


def output_filename(fn, part, options):
    odir = os.path.dirname(fn)
    base = os.path.splitext(os.path.basename(fn))[0]
    part = str(part).zfill(options.width)
    ofn = '{}-part{}.txt'.format(base, part)
    return os.path.join(odir, ofn)


def process(fn, options):
    part, out = 1, None
    documents, sentences, tokens = 0, 0, 0
    with open(fn) as f:
        for l in f:
            if out is None:
                outfn = output_filename(fn, part, options)
                print('Writing {} ...'.format(outfn), file=sys.stderr)
                out = open(outfn, 'w')
            l = l.rstrip()
            print(l, file=out)
            if not l or l.isspace():
                doc_boundary = True
                documents += 1
            else:
                doc_boundary = False
                sentences += 1
                tokens += len(l.split())
            if (doc_boundary and 
                ((options.max_documents is not None and
                  documents >= options.max_documents) or
                 (options.max_sentences is not None and 
                  sentences >= options.max_sentences) or
                 (options.max_tokens is not None and
                  tokens >= options.max_tokens))):
                part += 1
                documents, sentences, tokens = 0, 0, 0
                out.close()
                out = None
    if out is not None:
        out.close()


def main(argv):
    args = argparser().parse_args(argv[1:])
    process(args.file, args)        
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))

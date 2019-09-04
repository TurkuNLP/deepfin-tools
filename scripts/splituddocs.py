#!/usr/bin/env python

# Split UD data by document boundaries


import sys
import os

from common import is_document_boundary


def argparser():
    from argparse import ArgumentParser
    ap = ArgumentParser(description='Split text by document')
    ap.add_argument('-w', '--width', default=3, type=int,
                    help='minimum number of digits in part identifier')
    ap.add_argument('-d', '--max-documents', default=100000, type=int)
    ap.add_argument('file')
    return ap


def output_filename(fn, part, options):
    odir = os.path.dirname(fn)
    base = os.path.splitext(os.path.basename(fn))[0]
    part = str(part).zfill(options.width)
    ofn = '{}-part{}.conllu'.format(base, part)
    return os.path.join(odir, ofn)


def process(fn, options):
    part, out, documents = 1, None, 0
    with open(fn) as f:
        for l in f:
            l = l.rstrip()
            if is_document_boundary(l):
                documents += 1
            if documents > options.max_documents:
                part += 1
                documents = 1
                out.close()
                out = None
            if out is None:
                outfn = output_filename(fn, part, options)
                print('Writing {} ...'.format(outfn), file=sys.stderr)
                out = open(outfn, 'w')
            print(l, file=out)
    if out is not None:
        out.close()


def main(argv):
    args = argparser().parse_args(argv[1:])
    process(args.file, args)        
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))

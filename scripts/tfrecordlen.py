#!/usr/bin/env python3

# Print number of records in .tfrecord file(s).

import sys

import tensorflow as tf

from math import log
from logging import warning, error


metric_prefix = ['', 'k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']


def argparser():
    from argparse import ArgumentParser
    ap = ArgumentParser(
        description='Print number of records in .tfrecord file(s)')
    ap.add_argument('-H', '--human-readable', default=False, 
                    action='store_true',
                    help='print human-readable sized (e.g. 1M)')
    ap.add_argument('file', nargs='+')
    return ap


def human_readable(num, format_string='{:.1f}{}'):
    exp = int(log(num, 1000))
    val = num / 1000**exp
    return format_string.format(val, metric_prefix[exp])


def tfrecord_length(fn):
    it = tf.python_io.tf_record_iterator(fn)
    length = 0
    try:
        for _ in it:
            length += 1
    except tf.errors.DataLossError as e:
        print('WARNING: {}: {}'.format(fn, e), file=sys.stderr)
    return length


def format_len(n, options):
    if not options.human_readable:
        return str(n)
    else:
        return human_readable(n)


def main(argv):
    args = argparser().parse_args(argv[1:])
    total = 0
    for fn in args.file:
        try:
            n = tfrecord_length(fn)
        except:
            error('failed to get number of records from {}'.format(fn))
            raise #continue
        if len(args.file) == 1:
            print(format_len(n, args))
        else:
            print('{}\t{}'.format(format_len(n, args), fn))
        total += n
    if len(args.file) > 1:
        print('{}\ttotal'.format(format_len(total, args)))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))

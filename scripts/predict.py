#!/usr/bin/env python3

import sys
import os

from common import load_examples, load_model


def argparser():
    from argparse import ArgumentParser
    ap = ArgumentParser(description='Predict classes for text with SVM')
    ap.add_argument('-t', '--truncate', metavar='LEN', default=None, type=int)
    ap.add_argument('data')
    ap.add_argument('model')
    return ap


def main(argv):
    args = argparser().parse_args(argv[1:])
    examples = load_examples(args.data)
    clf, vecf = load_model(args.model)
    X = vecf.transform([e.text for e in examples])
    for e, c, s in zip(examples, clf.predict(X), clf.decision_function(X)):
        text = e.text if args.truncate is None else e.text[:args.truncate]
        print('{}\t{}\t{}\t{}\t{}'.format(e.id_, e.class_, c, s, text))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))

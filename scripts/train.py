#!/usr/bin/env python3

import sys
import os
import pickle

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC

from common import load_examples, save_model


def argparser():
    from argparse import ArgumentParser
    ap = ArgumentParser(description='Train SVM for text classification')
    ap.add_argument('data')
    ap.add_argument('model')
    return ap


def main(argv):
    args = argparser().parse_args(argv[1:])
    examples = load_examples(args.data)

    vecf = TfidfVectorizer(analyzer='word', token_pattern=r'\S+',
                           lowercase=False, ngram_range=(1,3))

    texts = [e.text for e in examples]
    X = vecf.fit_transform(texts)
    Y = [e.class_ for e in examples]
    
    clf = LinearSVC(C=1.0)
    clf.fit(X, Y)

    save_model(args.model, clf, vecf)
    
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))

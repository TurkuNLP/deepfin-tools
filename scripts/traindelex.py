#!/usr/bin/env python3

import sys
import os
import pickle

from collections import defaultdict

from sklearn.feature_extraction import DictVectorizer
from sklearn.svm import LinearSVC

from common import load_conllu, featurize_documents, save_model


def argparser():
    from argparse import ArgumentParser
    ap = ArgumentParser(description='Train SVM using delexicalized features')
    ap.add_argument('positive')
    ap.add_argument('negative')
    ap.add_argument('model')
    return ap


def main(argv):
    args = argparser().parse_args(argv[1:])

    positive = load_conllu(args.positive)
    negative = load_conllu(args.negative)
    posf = featurize_documents(positive)
    negf = featurize_documents(negative)
    vecf = DictVectorizer()

    X = vecf.fit_transform(posf + negf)
    Y = ['pos'] * len(posf) + ['neg'] * len(negf)

    clf = LinearSVC(C=1.0)
    clf.fit(X, Y)

    save_model(args.model, clf, vecf)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))

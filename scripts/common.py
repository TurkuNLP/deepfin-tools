import re
import pickle

from collections import namedtuple
from logging import error


# Suppress warning
# /usr/local/lib/python3.5/dist-packages/sklearn/feature_extraction/text.py:1039: FutureWarning: Conversion of the second argument of issubdtype from `float` to `np.floating` is deprecated. In future, it will be treated as `np.float64 == np.dtype(float).type`.
#   if hasattr(X, 'dtype') and np.issubdtype(X.dtype, np.float):
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


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


class Example(object):
    def __init__(self, id_, class_, text):
        self.id_ = id_
        self.class_ = class_
        self.text = text

    def __str__(self):
        return '\t'.join([self.id_, self.class_, self.text])


def read_tsv(fn, limit=None):
    data = []
    with open(fn) as f:
        for ln, l in enumerate(f, start=1):
            if limit is not None and ln > limit:
                break
            l = l.rstrip('\n')
            data.append(l.split('\t'))
    return data


def load_examples(fn):
    fields = read_tsv(fn)
    examples = []
    for ln, f in enumerate(fields, start=1):
        try:
            examples.append(Example(*f))
        except:
            error('line {}: {}'.format(ln, f))
            raise
    return examples


def save_model(fn, clf, vecf):
    with open('{}.clf'.format(fn), 'wb') as f:
        pickle.dump(clf, f)
    with open('{}.vecf'.format(fn), 'wb') as f:
        pickle.dump(vecf, f)


def load_model(fn):
    with open('{}.clf'.format(fn), 'rb') as f:
        clf = pickle.load(f)
    with open('{}.vecf'.format(fn), 'rb') as f:
        vecf = pickle.load(f)
    return clf, vecf

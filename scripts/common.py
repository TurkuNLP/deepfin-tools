import sys
import re
import pickle
import gzip

from collections import namedtuple, defaultdict
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


FORM_REs = [
    ('url', re.compile(r'^s?http://', re.U)),
    ('tag', re.compile(r'^[<\[]/?[a-z]+', re.U)),
    ('char', re.compile(r'^[a-zA-ZåäöÅÄÖ]$', re.U)),
    ('upper', re.compile(r'^[A-ZÅÄÖ]+$', re.U)),
    ('word', re.compile(r'^[a-zA-ZåäöÅÄÖ-]+$', re.U)),
    ('number', re.compile(r'^-?[0-9][0-9,. -]*$', re.U)),
    ('wordnum', re.compile(r'^[a-zA-ZåäöÅÄÖ0-9-][a-zA-ZåäöÅÄÖ0-9,.-]*$', re.U)),
    ('punct', re.compile(r'^[.,:;()\[\]%]+$', re.U)),
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


def is_document_boundary(comment):
    return comment.startswith('# doc_id = ') or comment.startswith('# <doc ')


def read_conllu(f, fn, stats=None):
    if stats is None:
        stats = defaultdict(int)
    documents, sentences, comments, words = [], [], [], []
    for ln, l in enumerate(f, start=1):
        l = l.rstrip('\n')
        if not l or l.isspace():
            sentences.append((comments, words))
            comments, words = [], []
        elif l.startswith('#'):
            if is_document_boundary(l):
                if sentences:
                    documents.append(sentences)
                sentences = []
            comments.append(l)
        else:
            words.append(Word(*l.split('\t')))
        if ln % 100000 == 0:
            print('read {} lines, {} docs from {} ...'.format(
                    ln, len(documents), fn), file=sys.stderr, flush=True)
    if sentences:
        documents.append(sentences)
    return documents


def load_conllu(fn, stats=None):
    if not fn.endswith('.gz'):
        with open(fn) as f:
            return read_conllu(f, fn, stats)
    else:
        with gzip.open(fn, 'rt') as f:
            return read_conllu(f, fn, stats)


def featurize_document(document):
    s_stats, w_stats, w_total = defaultdict(int), defaultdict(int), 0
    for comments, words in document:
        for w in words:
            w_stats['upos-{}'.format(w.upos)] += 1
            w_stats['dep-{}'.format(w.deprel)] += 1
            w_stats['len-{}'.format(len(w.form))] += 1
            if w.feats != '_':
                for f in w.feats.split('|'):
                    w_stats['feat-{}'.format(f)] += 1
            for k, r in FORM_REs:
                if r.match(w.form):
                    w_stats['form-{}'.format(k)] += 1
                    break
            else:
                w_stats['form-other'] += 1
            w_total += 1
    for k, v in w_stats.items():
        w_stats[k] = v/w_total
    return w_stats
    

def featurize_documents(documents):
    return [featurize_document(d) for d in documents]


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

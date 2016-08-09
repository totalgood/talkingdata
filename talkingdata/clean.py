#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from collections import Mapping
import re

import six

import pandas as pd

from .constant import DATA_DIR


def run():
    tables = load_all()
    return clean_all(*tables)

def most_frequent(df, category_label='category', index_label='device_id'):
    """Return a Series with the most frequent categorical value from the indicated column"""
    most_freq = []
    devices = list(set(df[index_label])]
    for i in devices:
        most_freq += max(((v, k) for (k, v) in Counter(df[df[index_label] == i][category_label]).items()))[-1]
    return pd.Series(most_freq, index=devices, name='most_frequent_' + category_label)

def load_all(data_path=DATA_DIR):
    """Load all data tables into Pandas DataFrames"""
    data_path = data_path.rstrip('/') + '/'

    # 460k many-to-many rels
    # app_id (113k) -> label_id (507): 1 duplicate connection
    app_labels = pd.read_csv(data_path + 'app_labels.csv.zip')

    # 3.2M events, each with a unique event_id
    # event_id (1,2,3...) device_id (SN) timestamp longitude latitude (deg)
    # so it may be possible to cluster device_id brands by location and then assign the 529 duplicate device IDs to unique brands/models
    events = pd.read_csv(data_path + 'events.csv.zip', index_col='event_id')

    # 33M many-to-many relationships betwen events and apps
    # event_id app_id is_installed is_active
    app_events = pd.read_csv(data_path + 'app_events.csv.zip', index_col='event_id')

    # 187k phones, most with a unique device_id (529 devic_id numbers seem to have been reused by different brands)
    # device_id phone_brand   device_model
    phone = pd.read_csv(data_path + 'phone_brand_device_model.csv.zip', index_col='device_id')

    # 930 label_id label_categories (string descriptions)
    label_categories = pd.read_csv(data_path + 'label_categories.csv.zip', index_col='label_id')

    # gender age group (gender+age_group)
    train = pd.read_csv(data_path + 'gender_age_train.csv.zip', index_col='device_id')

    # groups = list(set(train.group))
    # groups = [re.match('(F|M)([0-9]{2})([-+])([0-9]{0,2})', g).groups() for g in groups]
    # groups = [(int(g == 'M'), int(a0 if a1 or sign == '+' else 0), int(a0 if not a1 and sign == '-' else a1))
    #           for (g, a0, sign, a1) in groups]

    test = pd.read_csv(data_path + 'gender_age_test.csv.zip', index_col='device_id')

    return app_labels, events, app_events, phone, label_categories, train, test


def clean_all(app_labels, events, app_events, phone, label_categories, train, test):
    """Normalize/vectorize data types and values to be more RAM efficient"""
    train['gender'] = (train.gender == 'M').astype(pd.np.int8)
    groups = pd.DataFrame([parse_group(g) for g in train.group],
                          columns=['gender', 'min_age', 'max_age'],
                          index=train.index).astype(pd.np.int8)
    num_inconsistent = sum(~(groups.gender == train.gender))
    assert num_inconsistent == 0, "There were {} inconsistent genders in the groups and gender columns".format(num_inconsistent)
    assert (groups.min_age < groups.max_age).all(), "Not all min_age values were less than max_age!"
    del train['groups']
    train['min_age'] = groups.min_age, groups.max_age
    return app_labels, events, app_events, phone, label_categories, train, test


def parse_group(s):
    """Return (gender: 0|1=F|M, minimum_age, maximum_age)

    M=1,F=0, '22-'=(0, 22), '43+'=(43, 99)
    """
    g, a0, sign, a1 = re.match('(F|M)([0-9]{2})([-+])([0-9]{0,2})', s).groups()
    return (int(g == 'M'), int(a0 if a1 or sign == '+' else 0), int(99 if sign == '+' else a0 if sign == '-' else a1))


def make_group_vocab(groups):
    """Parse gender plus min and max age from marketing cohorts/group strings and return a vocab dict

    >>> groups = 'M22- M29-31 M23-26 F24-26 F33-42 F27-28 F29-32 F43+ M32-38 F23- M39+ M27-28'.split()
    >>> (make_group_vocab(groups) ==
    ...   {'M22-': (1, 0, 22), 'F24-26': (0, 24, 24), 'F33-42': (0, 33, 33),
    ...    'F27-28': (0, 27, 27), 'M23-26': (1, 23, 23), 'F23-': (0, 0, 23),
    ...    'M39+': (1, 39, 99), 'F43+': (0, 43, 99), 'F29-32': (0, 29, 29),
    ...    'M27-28': (1, 27, 27), 'M32-38': (1, 32, 32), 'M29-31': (1, 29, 29)})
    True
    """
    return dict([(g, parse_group(g)) for g in set(groups)])


def make_vocab(texts, normalize=lambda x: str(x).lower().strip()):
    """Convert gender strings into integers and return translation dict

    >>> make_vocab(list('MFMMF')) == {'F': 0, 'M': 1}
    True
    """
    return dict([(t, i) for (i, t) in enumerate(sorted(set(texts)))])
    if callable(normalize):
        normalization = dict([(t, normalize(t)) for t in texts])
        vocab = make_vocab([normalize(t) for t in set(texts)], normalize=normalization)
    elif isinstance(normalize, Mapping):
        denormalization = dict((v, k) for (k, v) in six.iteritems(normalization))
        vocab = make_vocab(dict([normalize(t) for t in texts], normalize=None))
        vocab.update([(denormalization[k], v) for (k, v) in six.iteritems(vocab)])
        return vocab
    else:
        return dict([(t, i) for (i, t) in enumerate(set(texts))])

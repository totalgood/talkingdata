#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from collections import Mapping
import re

import six

import pandas as pd

DP = '/var/local/data/kaggle/2016-09-31-Talking-Data/'

# 460k many-to-many rels
# app_id (113k) -> label_id (507): 1 duplicate connection
app_labels = pd.read_csv(DP + 'app_labels.csv.zip')

# 3.2M events, each with a unique event_id
# event_id (1,2,3...) device_id (SN) timestamp longitude latitude (deg)
# so it may be possible to cluster device_id brands by location and then assign the 529 duplicate device IDs to unique brands/models
events = pd.read_csv(DP + 'events.csv.zip', index_col='event_id')

# 33M many-to-many relationships betwen events and apps
# event_id app_id is_installed is_active
app_events = pd.read_csv(DP + 'app_events.csv.zip', index_col='event_id')

# 187k phones, most with a unique device_id (529 devic_id numbers seem to have been reused by different brands)
# device_id phone_brand   device_model
phone = pd.read_csv(DP + 'phone_brand_device_model.csv.zip', index_col='device_id')

# 930 label_id label_categories (string descriptions)
label_categories = pd.read_csv(DP + 'label_categories.csv.zip', index_col='label_id')

# gender age group (gender+age_group)
train = pd.read_csv(DP + 'gender_age_train.csv.zip', index_col='device_id')

train['gender'] = (train.gender == 'M').astype(pd.np.int8)
# groups = list(set(train.group))
# groups = [re.match('(F|M)([0-9]{2})([-+])([0-9]{0,2})', g).groups() for g in groups]
# groups = [(int(g == 'M'), int(a0 if a1 or sign == '+' else 0), int(a0 if not a1 and sign == '-' else a1))
#           for (g, a0, sign, a1) in groups]


def parse_group(s):
    """Return (gender: 0|1=F|M, minimum_age, maximum_age)

    M=1,F=0, '22-'=(0, 22), '45+'=(45, 99)
    """
    g, a0, sign, a1 = re.match('(F|M)([0-9]{2})([-+])([0-9]{0,2})', s).groups()
    return (int(g == 'M'), int(a0 if a1 or sign == '+' else 0), int(a0 if not a1 and sign == '-' else a1))


def make_group_vocab(groups):
    """Parse gender plus min and max age from marketing cohorts/group strings and return a vocab dict

    >>> groups = 'M22- M29-31 M23-26 F24-26 F33-42 F27-28 F29-32 F43+ M32-38 F23- M39+ M27-28'.split()
    >>> make_group_vocab(groups)

    """
    return dict([(g, parse_group(g)) for g in set(groups)])


def make_vocab(texts, normalize=lambda x: str(x).lower().strip()):
    """Convert gender strings into integers and return translation dict

    >>> make_vocab(list('MFMMF'))
    {'f': 0, 'm': 1}
    """
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


test = pd.read_csv(DP + 'gender_age_test.csv.zip', index_col='device_id')

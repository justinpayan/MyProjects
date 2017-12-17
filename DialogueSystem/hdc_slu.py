#!/usr/bin/env python
# encoding: utf8
# This code is PEP8-compliant. See http://www.python.org/dev/peps/pep-0008.

from __future__ import unicode_literals

import copy
import codecs
from ast import literal_eval
from itertools import chain

from alex.components.asr.utterance import Utterance, UtteranceHyp
from alex.components.slu.base import SLUInterface
from alex.components.slu.da import DialogueActItem, DialogueActConfusionNetwork, DialogueAct

# if there is a change in search parameters from_stop, to_stop, time, then
# reset alternatives


def any_word_in(utterance, words):
    words = words if not isinstance(words, basestring) else words.strip().split()
    for alt_expr in words:
        if alt_expr in utterance.utterance:
            return True
    return False


def all_words_in(utterance, words):
    words = words if not isinstance(words, basestring) else words.strip().split()
    for alt_expr in words:
        if alt_expr not in utterance.utterance:
            return False
    return True


def phrase_in(utterance, words):
    return phrase_pos(utterance, words) != -1


def last_phrase_pos(utterance, words):
    """Returns the last position of a given phrase in the given utterance, or -1 if not found.

    :rtype: int
    """
    list_utterance = utterance.utterance if not isinstance(utterance, list) else utterance
    list_words = words.utterance if not isinstance(words, basestring) else words.strip().split()
    # reverse to start search from the end
    utterance = Utterance(' '.join(list_utterance[::-1]))
    words = Utterance(' '.join(list_words[::-1]))

    index = utterance.find(words)
    if index == -1:
        return -1
    else:
        return len(utterance.utterance) - index - 1


def phrase_pos(utterance, words):
    """Returns the position of the given phrase in the given utterance, or -1 if not found.

    :rtype: int
    """
    utterance = utterance if not isinstance(utterance, list) else Utterance(' '.join(utterance))
    words = words if not isinstance(words, basestring) else words.strip().split()
    return utterance.find(words)


def any_combination_in(utterance, phrases1, phrases2):
    for p1 in phrases1:
        for p2 in phrases2:
            if phrase_pos(utterance, p1 + ' ' + p2) != -1:
                return True
    return False


def last_phrase_span(utterance, phrases):
    """Returns the span (start, end+1) of the last phrase from the given list
    that is found in the utterance. Returns (-1, -1) if no phrase is found.

    :param utterance: The utterance to search in
    :param phrases: a list of phrases to be tried (in the given order)
    :rtype: tuple
    """
    for phrase in phrases:
        pos = last_phrase_pos(utterance, phrase)
        if pos != -1:
            return pos, pos + len(phrase.split())
    return -1, -1


def first_phrase_span(utterance, phrases):
    """Returns the span (start, end+1) of the first phrase from the given list
    that is found in the utterance. Returns (-1, -1) if no phrase is found.

    :param utterance: The utterance to search in
    :param phrases: a list of phrases to be tried (in the given order)
    :rtype: tuple
    """
    for phrase in phrases:
        pos = phrase_pos(utterance, phrase)
        if pos != -1:
            return pos, pos + len(phrase.split())
    return -1, -1


def any_phrase_in(utterance, phrases):
    return first_phrase_span(utterance, phrases) != (-1, -1)


def ending_phrases_in(utterance, phrases):
    """Returns True if the utterance ends with one of the phrases

    :param utterance: The utterance to search in
    :param phrases: a list of phrases to search for
    :rtype: bool
    """

    utterance = utterance if not isinstance(utterance, list) else Utterance(' '.join(utterance))
    utterance_len = len(utterance)

    for phrase in phrases:
        phr_pos = phrase_pos(utterance, phrase)
        if phr_pos is not -1 and phr_pos + len(phrase.split()) is utterance_len:
            return True
    return False


class DAIBuilder(object):
    """
    Builds DialogueActItems with proper alignment to corresponding utterance words.
    When words are successfully matched using DAIBuilder, their indices in the utterance are
    added to alignment set of the DAI as a side-effect.
    """

    def __init__(self, utterance, abutterance_lenghts=None):
        """
        :param utterance: utterance to search words in
        :type utterance: Utterance
        :param abutterance_lenghts: numbers of utterance words that correspond to each abutterance word.
            I.e.: an element is 1 if respective abutterance word is unabstracted utterance words
        :type abutterance_lenghts: list[int]
        """
        self._utterance = utterance if not isinstance(self, list) else Utterance(' '.join(utterance))
        self.utt2abutt_idxs = range(len(utterance)) if not abutterance_lenghts else \
            list(chain.from_iterable([idx] * abutterance_lenghts[idx]
                                     for idx in range(len(abutterance_lenghts))))
        self._alignment = set()

    def build(self, act_type=None, slot=None, value=None):
        """
        Produce DialogueActItem based on arguments and alignment from this DAIBuilder state.
        """
        dai = DialogueActItem(act_type, slot, value, alignment={self.utt2abutt_idxs[i] for i in self._alignment})
        self.clear()
        return dai

    def clear(self):
        self._alignment = set()

    def _words_in(self, qualifier, words):
        words = words if not isinstance(words, basestring) else words.strip().split()
        if qualifier(word in self._utterance.utterance for word in words):
            indices = [i for i, word in enumerate(self._utterance.utterance) if word in words]
            self._alignment.update(indices)
            return True
        else:
            return False

    def any_word_in(self, words):
        return self._words_in(any, words)

    def all_words_in(self, words):
        return self._words_in(all, words)

    def phrase_pos(self, words, sub_utt=None):
        """Returns the position of the given phrase in the given utterance, or -1 if not found.

        :rtype: int
        """
        utt = Utterance(self._utterance[sub_utt[0]:sub_utt[1]]) if sub_utt else self._utterance
        words = words if not isinstance(words, basestring) else words.strip().split()
        return utt.find(words)

    def first_phrase_span(self, phrases, sub_utt=None):
        """Returns the span (start, end+1) of the first phrase from the given list
        that is found in the utterance. Returns (-1, -1) if no phrase is found.

        :param phrases: a list of phrases to be tried (in the given order)
        :rtype: tuple
        """
        for phrase in phrases:
            pos = self.phrase_pos(phrase, sub_utt)
            if pos != -1:
                self._alignment.update(range(pos, pos + len(phrase.split())))
                return pos, pos + len(phrase)
        return -1, -1

    def any_phrase_in(self, phrases, sub_utt=None):
        return self.first_phrase_span(phrases, sub_utt) != (-1, -1)

    def phrase_in(self, phrase, sub_utt=None):
        return self.any_phrase_in([phrase], sub_utt)

    def any_combination_in(self, phrases1, phrases2):
        for p1 in phrases1:
            for p2 in phrases2:
                if self.first_phrase_span([p1 + ' ' + p2]) != (-1, -1):
                    return True
        return False

    def ending_phrases_in(self, phrases):
        """Returns True if the utterance ends with one of the phrases

        :param phrases: a list of phrases to search for
        :rtype: bool
        """
        utterance = self._utterance if not isinstance(self, list) else Utterance(' '.join(self._utterance))
        for phrase in phrases:
            pos = self.phrase_pos(phrase)
            if pos is not -1 and pos + len(phrase.split()) is len(utterance):
                self._alignment.update(range(pos, pos + len(phrase.split())))
                return True
        return False


class OurSLU(SLUInterface):

    def __init__(self, preprocessing, cfg):
        super(OurSLU, self).__init__(preprocessing, cfg)
        self.cldb = self.preprocessing.cldb
        if 'utt2da' in cfg['SLU'][OurSLU]:
            self.utt2da = self._load_utt2da(cfg['SLU'][OurSLU]['utt2da'])
        else:
            self.utt2da = {}

    def _load_utt2da(self, filename):
        """
        Load a dictionary mapping utterances directly to dialogue acts for the utterances
        that are either too complicated or too unique to be parsed by HDC SLU rules.

        :param filename: path to file with a list of utterances transcriptions and corresponding dialogue acts
        :return: a dictionary from utterance to dialogue act
        :rtype: dict
        """
        utt2da = {}
        with codecs.open(filename, 'r', 'UTF-8') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, val = line.split('\t')
                    utt2da[unicode(key)] = val
        return utt2da

    def abstract_utterance(self, utterance):
        """
        Return a list of possible abstractions of the utterance.

        :param utterance: an Utterance instance
        :return: a list of abstracted utterance, form, value, category label tuples
        """
        abs_utts = copy.deepcopy(utterance)
        category_labels = set()
        abs_utt_lengths = [1] * len(abs_utts)
        start = 0
        while start < len(utterance):
            end = len(utterance)
            while end > start:
                f = tuple(utterance[start:end])

                if f in self.cldb.form2value2cl:
                    entities = self.cldb.form2value2cl[f]
                    slot_names = [(slot, name) for name in entities for slot in entities[name]]
                    slots = [slot for slot, _ in slot_names]

                    def replace_slot(abs_utts, slot, slot_names):
                        name = [n for s, n in slot_names if s == slot].pop()
                        return abs_utts.replace(f, (slot.upper() + '=' + name,))

                    if 'street' in slots:
                        abs_utts = replace_slot(abs_utts, 'street', slot_names)
                        category_labels.add('STREET')
                    else:
                        slot = slots.pop()
                        abs_utts = replace_slot(abs_utts, slot, slot_names)
                        category_labels.add(slot.upper())
                    abs_utt_lengths[start] = len(f)

                    # skip all substring for this form
                    start = end
                    break
                end -= 1
            else:
                start += 1
        # normalize abstract utterance lengths
        norm_abs_utt_lengths = []
        i = 0
        while i < len(abs_utt_lengths):
            l = abs_utt_lengths[i]
            norm_abs_utt_lengths.append(l)
            i += l
        return abs_utts, category_labels, norm_abs_utt_lengths

    def __repr__(self):
        return "OurSLU({preprocessing}, {cfg})".format(preprocessing=self.preprocessing, cfg=self.cfg)

    def parse_street(self, abutterance, cn):
        """ Detects street in the input abstract utterance.

        :param abutterance: the input abstract utterance.
        :param cn: The output dialogue act item confusion network.
        """

        # regular parsing
        phr_wp_types = [('from', set(['from', 'beginning', 'start', 'starting', 'origin', 'standing in', 'standing at',  # of, off
                                      'originated', 'originating', 'origination', 'initial', 'i am at', 'i am in',
                                      'leave', ])),
                        ('to', set(['to', 'into', 'in', 'end', 'ending', 'terminal', 'final',
                                    'target', 'output', 'exit', 'destination', 'be at'])),
                        ('via', set(['via', 'through', 'transfer', 'transferring', 'interchange', ]))]

        # here we support more than one initial and destination point!
        self.parse_waypoint(abutterance, cn, 'STREET=', 'street', phr_wp_types)

        # get bare street slot and try to infer from/to/via from previous occurrence of street
        dais = [dai_hyp[1] for dai_hyp in cn.items()]
        last_nonbare_street_idx = -1
        for index, dai in enumerate(dais):
            # remember occurrences of street (with direction)
            if dai.name.endswith('_street'):
                last_nonbare_street_idx = index
            # skip if the slot is not bare 'street' or if we do not know any previous direction
            if dai.name != 'street' or last_nonbare_street_idx == -1:
                continue
            # replace the direction with the previous one
            prob = cn.get_prob(dai)
            cn.remove(dai)
            dai.name = dais[last_nonbare_street_idx].name
            cn.add(prob, dai)
            last_nonbare_street_idx = index

        # here we tag each street with its sequential number
        dais = [dai_hyp[1] for dai_hyp in cn.items()]

        def fix_second_street(slot_name):
            street_indices = [i for i, dai in enumerate(dais) if dai.name == slot_name][1:]
            number = 2
            for i in street_indices:  # all slots are from_street2
                prob = cn.get_prob(dais[i])
                cn.remove(dais[i])
                cn.add(prob, DialogueActItem(dais[i].dat, dais[i].name + str(number), dais[i].value))

        fix_second_street('from_street')
        fix_second_street('to_street')

    def parse_route(self, abutterance, cn):
        """Detects the bus route in the input abstract utterance.

        :param abutterance: the input abstract utterance.
        :param cn: The output dialogue act item confusion network.
        """

        u = abutterance

        #preps_abs = set(["at", "time", "past", "after", "between", "before", "in", "around", "about", "for"])
        #preps_rel = set(["in", ])

        for i, w in enumerate(u):
            if w.startswith("ROUTE="):
                value = w[6:]
		cn.add_merge(1.0, DialogueActItem('inform', 'route', value))
        

    def parse_poi(self, abutterance, cn):
        """ Detects points of interest (monuments) in the input abstract utterance.

        :param abutterance: the input abstract utterance.
        :param cn: The output dialogue act item confusion network.
        """

        # for i, w in enumerate(abutterance):
        #     if w.startswith("STATE="):
        #         value = w[6:]
        #         cn.add(1.0, DialogueActItem("inform", 'in_state', value))

        # regular parsing
        phr_wp_types = [('from', set(['from', 'beginning', 'start', 'starting', 'origin',  # of, off
                                      'originated', 'originating', 'origination', 'initial', ])),  # I'm at, I'm in ?
                        ('to', set(['to', 'into', 'end', 'ending', 'terminal', 'final',
                                    'target', 'output', 'exit', 'destination', ])),
                        ('via', set(['via', 'through', 'transfer', 'transferring', 'interchange'])),
                        ('in', set(['for', 'after', 'in', 'at'])),  # ? ['pro', 'po']
                        ]

        self.parse_waypoint(abutterance, cn, 'POI=', 'poi', phr_wp_types, phr_in=['in', 'at'])

    def parse_neighborhood(self, abutterance, cn):
        """ Detects neighborhoods in the input abstract utterance.

        :param abutterance: the input abstract utterance.
        :param cn: The output dialogue act item confusion network.
        """

        # regular parsing
        phr_wp_types = [('from', set(['from', 'beginning', 'start', 'starting', 'origin',  # of, off
                                      'originated', 'originating', 'origination', 'initial', ])),  # I'm at, I'm in ?
                        ('to', set(['to', 'into', 'end', 'ending', 'terminal', 'final',
                                    'target', 'output', 'exit', 'destination', ])),
                        ('via', set(['via', 'through', 'transfer', 'transferring', 'interchange'])),
                        ('in', set(['for', 'after', 'in', 'at'])),  # ? ['pro', 'po']
                        ]

        self.parse_waypoint(abutterance, cn, 'NEIGHBORHOOD=', 'neighborhood', phr_wp_types, phr_in=['in', 'at'])

    def parse_waypoint(self, abutterance, cn, wp_id, wp_slot_suffix, phr_wp_types, phr_in=None):
        """Detects stops or cities in the input abstract utterance
        (called through parse_city or parse_stop).

        :param abutterance: the input abstract utterance.
        :param cn: The output dialogue act item confusion network.
        :param wp_id: waypoint slot category label (e.g. "STOP=", "CITY=")
        :param wp_slot_suffix: waypoint slot suffix (e.g. "stop", "city")
        :param phr_wp_types: set of phrases for each waypoint type
        :param phr_in: phrases for 'in' waypoint type
        """
        u = abutterance
        N = len(u)

        # simple "not" cannot be included as it collides with negation. "I do not want this [,] go from Brooklyn"
        phr_dai_types = [('confirm', set(['it departs', 'departs from', 'depart from',  # 'leave', 'leaves',
                                          'is the starting', ]), set()),
                         ('deny',
                          set(['not from', 'not at', 'not in', 'not on', 'not to', 'not into', 'and not',
                               'not the', 'rather than', 'cancel the']),  # don't, doesn't?
                          set(['not'
                               ' at all' 'not wish', 'not this way', 'no not that', 'not need help',
                               'not want', ]))]
        last_wp_pos = 0

        for i, w in enumerate(u):
            if w.startswith(wp_id):
                wp_name = w[len(wp_id):]
                wp_types = set()
                dai_type = 'inform'

                # test short preceding context to find the stop type (from, to, via)
                wp_precontext = {}
                for cur_wp_type, phrases in phr_wp_types:
                    wp_precontext[cur_wp_type] = last_phrase_span(u[max(last_wp_pos, i - 6):i], phrases)
                wp_types |= self._get_closest_wp_type(wp_precontext)
                # test short following context (0 = from, 1 = to, 2 = via)
                if not wp_types:
                    if any_phrase_in(u[i:i + 3], phr_wp_types[0][1] | phr_wp_types[2][1]):
                        wp_types.add('to')
                    elif any_phrase_in(u[i:i + 3], phr_wp_types[1][1]):
                        wp_types.add('from')
                # test longer following context - hack for catching "_ is the terminal station."
                if not wp_types:
                    if any_phrase_in(u[i:i + 5], phr_wp_types[0][1]):  # and not another STOP= (wp_type asi?) in i, i + 6 -> ok, jinak to nad tímhle
                        wp_types.add('from')
                    elif any_phrase_in(u[i:i + 5], phr_wp_types[1][1]):
                        wp_types.add('to')
                # resolve context according to further preceding/following waypoint name (assuming from-to)
                if not wp_types:
                    if i >= 1 and u[i - 1].startswith(wp_id):
                        wp_types.add('to')
                    elif i <= N - 2 and u[i + 1].startswith(wp_id):
                        wp_types.add('from')
                # using 'in' slot if the previous checks did not work and we have phrases for 'in'
                if not wp_types and phr_in is not None and any_phrase_in(u[max(last_wp_pos, i - 5): i], phr_in):
                    wp_types.add('in')

                # test utterance type
                for cur_dai_type, phrases_pos, phrases_neg in phr_dai_types:
                    if any_phrase_in(u[last_wp_pos:i], phrases_pos) and not any_phrase_in(u[last_wp_pos:i], phrases_neg):
                        dai_type = cur_dai_type
                        break

                # add waypoint to confusion network (standard case: just single type is decided)
                if len(wp_types) == 1:
                    # TODO: remove this hack - way: zapisovat do uterance - replace STREET with FROM_STREET, a pak tady bych mohl hledat v kontextu 2 slov, jeslti se nevyskytuje FROM_*
                    if 'in' in wp_types:  # catching following instances: from/to street/stop in city/borough -> from_stop & from_city
                        wp_precontext['in'] = (-1, -1)
                        next_wp_type = self._get_closest_wp_type(wp_precontext)
                        if next_wp_type:
                            for j in [1, 2, ]:
                                if i >= j and '=' in u[i - j] and u[i - j].split('=')[0].lower() in ['stop', 'street'] and wp_slot_suffix in ['city', 'borough']:
                                    wp_types.pop()
                                    wp_types = next_wp_type
                                    break
                    cn.add_merge(1.0, DialogueActItem(dai_type, wp_types.pop() + '_' + wp_slot_suffix, wp_name, alignment={i}))
                # backoff 1: add both 'from' and 'to' waypoint slots
                elif 'from' in wp_types and 'to' in wp_types:
                    cn.add_merge(0.501, DialogueActItem(dai_type, 'from_' + wp_slot_suffix, wp_name, alignment={i}))
                    cn.add_merge(0.499, DialogueActItem(dai_type, 'to_' + wp_slot_suffix, wp_name, alignment={i}))
                # backoff 2: let the DM decide in context resolution
                else:
                    cn.add_merge(1.0, DialogueActItem(dai_type, wp_slot_suffix, wp_name, alignment={i}))

                last_wp_pos = i + 1

    def _get_closest_wp_type(self, wp_precontext):
        """Finds the waypoint type that goes last in the context (if same end points are
        encountered, the type with a longer span wins).

        :param wp_precontext: Dictionary waypoint type -> span (start, end+1) in the preceding \
            context of the waypoint mention
        :returns: one-member set with the best type (if there is one with non-negative position), \
            or empty set on failure
        :rtype: set
        """
        best_type = None
        best_pos = (-2, -1)
        for cur_type, cur_pos in wp_precontext.iteritems():
            if cur_pos[1] > best_pos[1] or cur_pos[1] == best_pos[1] and cur_pos[0] < best_pos[0]:
                best_type = cur_type
                best_pos = cur_pos
        if best_type is not None:
            return set([best_type])
        return set()

    def parse_number(self, abutterance):
        """Detect a number in the input abstract utterance

        Number words that form time expression are collapsed into a single TIME category word.
        Recognized time expressions (where FRAC, HOUR and MIN stands for fraction, hour and minute numbers respectively):
            - quarter to/past HOUR
            - half past HOUR
            - FRAC (an/of an) hour*
            - HOUR hour* and a FRAC
            - HOUR and a FRAC hour*
            - HOUR hour* and MIN minute*
            - HOUR hour* MIN
            - HOUR hour*/o'clock/sharp
            - HOUR [0]MIN
            - at/around/after/about HOUR
            - MIN minute*
            - in an hour/in a minute

        Words of NUMBER category are assumed to be in format parsable to int or float

        :param abutterance: the input abstract utterance.
        :type abutterance: Utterance
        """
        def parse_number(word):
            return literal_eval(word[len("NUMBER="):])

        def hour_number(word):
            if not word.startswith("NUMBER="):
                return False
            num = parse_number(word)
            return isinstance(num, int) and 0 <= num < 24

        def minute_number(word):
            if not word.startswith("NUMBER="):
                return False
            num = parse_number(word)
            return isinstance(num, int) and 0 <= num < 60

        def fraction_number(word):
            if not word.startswith("NUMBER="):
                return False
            num = parse_number(word)
            return isinstance(num, float)

        u = abutterance
        i = 0
        while i < len(u):

            if fraction_number(u[i]):
                fraction_num = int(parse_number(u[i]) * 60)  # 15 or 30
                # half past/quarter to/quarter past HOUR
                if i < len(u) - 2 and hour_number(u[i + 2]):
                    hour_num = parse_number(u[i + 2])
                    minute_num = fraction_num
                    if fraction_num == 15 and u[i + 1] == 'to':  # quarter to HOUR
                        minute_num *= 3
                        hour_num -= 1
                    u[i:i + 3] = ["TIME_{len}={hour}:{min}".format(len=3, hour=hour_num, min=minute_num)]
                # half an hour
                elif i < len(u) - 2 and fraction_num == 30 and u[i + 1] == 'an' and u[i + 2] == 'hour':
                    u[i:i + 3] = ["TIME_{len}=0:30".format(len=3)]
                # quarter of an hour
                elif i < len(u) - 3 and u[i + 1] == 'of' and u[i + 2] == 'an' and u[i + 3] == 'hour':
                    u[i:i + 4] = ["TIME_{len}=0:{min}".format(len=4, min=fraction_num)]

            elif hour_number(u[i]):
                hour_num = parse_number(u[i])
                # HOUR hour* and a FRAC
                if i < len(u) - 4 and u[i + 1].startswith('hour') and u[i + 2] == 'and' and u[i + 3] == 'a' and fraction_number(u[i + 4]):
                    fraction_num = int(parse_number(u[i + 4]) * 60)
                    u[i:i + 5] = ["TIME_{len}={hour}:{min}".format(len=5, hour=hour_num, min=fraction_num)]
                # HOUR and a FRAC hour*
                elif i < len(u) - 4 and u[i + 1] == 'and' and u[i + 2] == 'a' and fraction_number(u[i + 3]) and u[i + 4].startswith('hour'):
                    fraction_num = int(parse_number(u[i + 3]) * 60)
                    u[i:i + 5] = ["TIME_{len}={hour}:{min}".format(len=5, hour=hour_num, min=fraction_num)]
                # HOUR hour* and MIN minute*
                elif i < len(u) - 4 and u[i + 2] == 'and' and minute_number(u[i + 3]) and u[i + 4].startswith('minute'):
                    u[i:i + 5] = ["TIME_{len}={hour}:{min:0>2d}".format(len=5, hour=hour_num, min=parse_number(u[i + 3]))]
                # HOUR hour* MIN
                elif i < len(u) - 3 and u[i + 1].startswith("hour") and minute_number(u[i + 2]):
                    u[i:i + 4] = ["TIME_{len}={hour}:{min:0>2d}".format(len=4, hour=hour_num, min=parse_number(u[i + 2]))]
                else:
                    # HOUR hours*/o'clock/in ...
                    if i < len(u) - 1:
                        if u[i + 1] in ['hour', 'hours', "o'clock", 'sharp']:
                            u[i:i + 2] = ["TIME_{len}={hour}:00".format(len=2, hour=hour_num)]
                        elif u[i + 1].startswith("AMPM="):
                            u[i] = "TIME_1={hour}:00".format(hour=hour_num)
                        # HOUR MINUTE
                        elif minute_number(u[i + 1]):
                            minute_num = parse_number(u[i + 1])
                            # HOUR MIN
                            u[i:i + 2] = ["TIME_{len}={hour}:{min:0>2d}".format(len=2, hour=hour_num, min=minute_num)]
                    # at/in... HOUR (if not matched already)
                    if (i > 0 and not u[i].startswith("TIME") and
                            u[i - 1] in ['at', 'around', 'after', 'about']):
                        u[i] = "TIME_{len}={hour}:00".format(len=1, hour=parse_number(u[i]))

            if minute_number(u[i]):
                # MIN minute*
                if i < len(u) - 1 and u[i + 1].startswith("minute"):
                    u[i:i + 2] = ["TIME_{len}=0:{min:0>2d}".format(len=2, min=parse_number(u[i]))]

            # in _ minute/hour
            elif i > 1 and 'in' in u[i - 2:i - 1]:  # in an hour/in a minute
                if u[i] == 'hour':
                    u[i] = "TIME_1=1:00"
                elif u[i] == 'minute':
                    u[i] = "TIME_1=0:01"
            # hour and a half:
            if i < len(u) - 3 and u[i] == "hour" and u[i + 1] == 'and' and u[i + 2] == 'a' and fraction_number(u[i + 3]):
                u[i:i + 4] = ["TIME_{len}=1:30".format(len=4)]
            i += 1

    def parse_time(self, abutterance, cn):
        """Detects the time in the input abstract utterance.

        :param abutterance: the input abstract utterance.
        :param cn: The output dialogue act item confusion network.
        """

        u = abutterance

        #preps_abs = set(["at", "time", "past", "after", "between", "before", "in", "around", "about", "for"])
        #preps_rel = set(["in", ])

        test_context = [('confirm', 'departure',
                         ['it leaves', 'it departures', 'it starts', 'is starting', 'is leaving', 'is departuring',
                          'departure point'],
                         []),
                        ('confirm', 'arrival',
                         ['it arrives', 'is arriving', 'will arrive', 'is coming', 'it comes', 'will come',
                          'arrival is'],  # will reach
                         []),
                        ('confirm', '',
                         ['it is', 'you think', 'positive'],
                         []),
                        ('deny', 'departure',
                         ['not leaving', 'not leave', 'not departing', 'not departure', 'not starting',
                          'not start', 'not want to go from', 'not from', 'not going from', 'not want to go from'],
                         []),
                        ('deny', 'arrival',
                         ['not arriving', 'not arrive', 'not come', 'not coming', 'not want to arrive',
                          'not want to come', 'not want to go to', 'not want to arrive', 'not going to',],
                         []),
                        ('deny', '',
                         ['no', 'not want', 'negative', 'cancel the', 'not going'],
                         []),
                        ('inform', 'departure',
                         ['TASK=find_connection', 'departure', 'departing', 'departs', 'departs from', 'leaving',
                          'leaves', 'starts', 'starting', 'goes', 'would go', 'will go', 'VEHICLE=tram',
                          'want to go', 'want to leave', 'want to take', 'want to travel', 'how can i get',
                          'wanted to go', 'wanted to leave', 'wanted to take', 'wanted to travel',
                          'how do i get', 'would like to go', 'i am at', 'i am in', ],
                         ['arrival', 'arrive', 'arriving', 'want to be at', 'wanted to be at', 'like to be at', ]),
                        ('inform', 'arrival',
                         ['arrival', 'arrive', 'get to', 'to get', 'arriving', 'want to be at', 'wanted to be at', 'like to be at', ],
                         []),
                        ('inform', '',
                         [],
                         []),
                        ]

        count_times = 0
        for i, w in enumerate(u):
            if w.startswith("TIME_") or w.startswith("TIME="):
                count_times += 1

        last_time_type = ''
        last_time = 0

        for i, w in enumerate(u):
            if w.startswith("TIME_") or w.startswith("TIME="):
                if w.startswith("TIME_"):
                    num_len = int(w[5])
                    value = w[7:]
                else:
                    num_len = 1
                    value = w[5:]
                time_rel = False

                if any_phrase_in(u[max(i-3,0):i], ['in', 'in a', 'in the', 'in the next', 'in the following']):
                        time_rel = True

                if count_times > 1:
                    j, k = last_time, i
                else:
                    j, k = 0, len(u)

                if value == "now":
                    if any_phrase_in(u[j:k], ['so what', 'what is the time', 'whats the time', 'can not hear', 'no longer telling me']):
                        continue
                    else:
                        time_rel = True

                for act_type, time_type, phrases_pos, phrases_neg in test_context:
                    if any_phrase_in(u[j:k], phrases_pos) and not any_phrase_in(u, phrases_neg):
                        break

                if count_times > 1 and not time_type:
                    # use the previous type if there was time before this one
                    time_type = last_time_type
                last_time_type = time_type

                slot = (time_type + ('_time_rel' if time_rel else '_time')).lstrip('_')
                cn.add_merge(1.0, DialogueActItem(act_type, slot, value, alignment=set(range(i, i + num_len))))
                last_time = i + 1

    def parse_date_rel(self, abutterance, cn):
        """Detects the relative date in the input abstract utterance.

        :param abutterance: the input abstract utterance.
        :param cn: The output dialogue act item confusion network.
        """

        u = abutterance

        confirm = phrase_in(u, ['it', 'does'])
        deny = any_phrase_in(u, ["do not", 'not want', 'cancel the',])

        for i, w in enumerate(u):
            if w.startswith("DATE_REL="):
                value = w[9:]

                if confirm:
                    cn.add_merge(1.0, DialogueActItem("inform", 'date_rel', value, alignment={i}))
                elif deny:
                    cn.add_merge(1.0, DialogueActItem("inform", 'date_rel', value, alignment={i}))
		    cn.add_merge(1.0, DialogueActItem("negate"))
                else:
                    cn.add_merge(1.0, DialogueActItem("inform", 'date_rel', value, alignment={i}))

    def parse_ampm(self, abutterance, cn):
        """Detects the ampm in the input abstract utterance.

        :param abutterance: the input abstract utterance.
        :param cn: The output dialogue act item confusion network.
        """

        u = abutterance

        confirm = phrase_in(u, ['it', 'does'])
        deny = any_phrase_in(u, ["do not", 'not want', 'cancel the',])

        for i, w in enumerate(u):
            if w.startswith("AMPM="):
                value = w[5:]

                if not (phrase_in(u, 'good night')):
                    if confirm:
                        cn.add_merge(1.0, DialogueActItem("inform", 'ampm', value, alignment={i}))
                    elif deny:
                        cn.add_merge(1.0, DialogueActItem("inform", 'ampm', value, alignment={i}))
			cn.add_merge(1.0, DialogueActItem("negate"))
                    else:
                        cn.add_merge(1.0, DialogueActItem("inform", 'ampm', value, alignment={i}))

    def parse_non_speech_events(self, utterance, cn):
        """
        Processes non-speech events in the input utterance.

        :param utterance: the input utterance
        :param cn: The output dialogue act item confusion network.
        :return: None
        """
        u = utterance

        if len(u.utterance) == 0 or "_silence_" == u or "__silence__" == u or "_sil_" == u:
            cn.add_merge(1.0, DialogueActItem("null", alignment={0}))

        if "_noise_" == u or "_laugh_" == u or "_ehm_hmm_" == u or "_inhale_" == u:
            cn.add_merge(1.0, DialogueActItem("null", alignment={0}))

        if "_other_" == u or "__other__" == u:
            cn.add_merge(1.0, DialogueActItem("null", alignment={0}))

    def parse_meta(self, utterance, abutt_lenghts, cn):
        """
        Detects all dialogue acts which do not generalise its slot values using CLDB.

        NOTE: Use DAIBuilder ('dai' variable) to match words and build DialogueActItem,
            so that the DAI is aligned to corresponding words. If matched words are not
            supposed to be aligned, use PTICSHDCSLU matching method instead.
            Make sure to list negative conditions first, so the following positive
            conditions are not added to alignment, when they shouldn't. E.g.:
            (not any_phrase_in(u, ['dobrý den', 'dobrý večer']) and dai.any_word_in("dobrý"))

        :param utterance: the input utterance
        :param cn: The output dialogue act item confusion network.
        :return: None
        """
        u = utterance
        dai = DAIBuilder(u, abutt_lenghts)

        if (dai.any_word_in('ahoy hello hey hi greetings') or
                dai.any_phrase_in(['good day', "what's up", 'what is up'])):
            cn.add_merge(1.0, DialogueActItem("hello"))

        if dai.any_word_in("bye byebye seeya goodbye") or \
                dai.any_phrase_in(['good bye', 'take baths', 'see you', 'see ya' 'nothing else', 'no further help needed', ]) or \
                (dai.any_phrase_in(['that is', 'that was', "that's", ]) and dai.any_phrase_in(['all', 'it', ])):

            cn.add_merge(1.0, DialogueActItem("bye"))

        if not dai.any_word_in('connection station option options last offer offered found beginning begin where going time'):
            if dai.any_phrase_in(['repeat', 'that again', 'come again', 'once more', 'say again', 'it again']):
                cn.add_merge(1.0, DialogueActItem("repeat"))

        if (dai.phrase_in("repeat the last sentence") or
                dai.phrase_in("repeat what you've") or
                dai.phrase_in("repeat what you have")):
            cn.add_merge(1.0, DialogueActItem("repeat"))

        if dai.any_word_in("hallo") or \
                dai.all_words_in('not hear you'):

            cn.add_merge(1.0, DialogueActItem('repeat'))

        if (dai.all_words_in("did not understand") or
                dai.all_words_in("didn\'t understand") or
                dai.all_words_in("speek up") or
                dai.all_words_in("can not hear you") or
                (len(u) == 1 and dai.any_word_in("can\'t hear you"))):
            cn.add_merge(1.0, DialogueActItem('repeat'))

        if dai.all_words_in("next bus"): 
            cn.add_merge(1.0, DialogueActItem('nextbus'))

        if dai.all_words_in("previous bus"): 
            cn.add_merge(1.0, DialogueActItem('prevbus'))

        if (dai.any_word_in("yes yeah sure correct") and
                not dai.any_word_in("end over option offer surrender")):
            cn.add_merge(1.0, DialogueActItem("affirm"))

        if not dai.any_phrase_in(['not from', 'not care']):
            if (dai.any_word_in("no not nope nono") or
                    dai.phrase_in('do not want') or
                    len(u) == 2 and dai.all_words_in("not want") or
                    len(u) == 3 and dai.all_words_in("yes do not") or
                    dai.all_words_in("is wrong")):
                cn.add_merge(1.0, DialogueActItem("negate"))

#        if (dai.any_word_in('ok okay well correct fine understand understood') or
#                (dai.any_word_in('right') and not dai.any_word_in('now')) and
#                not dai.any_word_in("yes")):
#            cn.add_merge(1.0, DialogueActItem("ack"))

        if (dai.any_word_in("from begin begins start starting") and
                dai.any_word_in("beginning scratch over") or
                dai.any_phrase_in(['stop talking', 'new entry']) or
                dai.any_word_in("reset restart reboot") or
                not dai.phrase_in('from') and dai.any_phrase_in(['new connection', 'new link'])):
            cn.add_merge(1.0, DialogueActItem("restart"))

        if dai.any_phrase_in(["by day", "of the day"]):
            cn.add_merge(1.0, DialogueActItem('inform', 'ampm', 'pm'))

    def handle_false_abstractions(self, abutterance):
        """
        Revert false positive alarms of abstraction

        :param abutterance: the abstracted utterance
        :return: the abstracted utterance without false positive abstractions
        """
        #

        abutterance = abutterance.replace(('how', 'CITY=Many'), ('how', 'many'))
        abutterance = abutterance.replace(('CITY=Tell', 'me'), ('tell', 'me'))
        abutterance = abutterance.replace('CITY=Best', 'best')
        abutterance = abutterance.replace('CITY=Call', 'call')
        abutterance = abutterance.replace('CITY=Transfer', 'transfer')
        abutterance = abutterance.replace('CITY=Day', 'day')
        abutterance = abutterance.replace('CITY=Ohio', 'STATE=Ohio')
        abutterance = abutterance.replace('CITY=California', 'STATE=California')
        abutterance = abutterance.replace('CITY=Washington', 'STATE=Washington')
        abutterance = abutterance.replace('CITY=Maryland', 'STATE=Maryland')
        abutterance = abutterance.replace('CITY=Nevada', 'STATE=Nevada')
        abutterance = abutterance.replace('CITY=Florida', 'STATE=Florida')
        abutterance = abutterance.replace('CITY=Kansas', 'STATE=Kansas')
        state_of = ['state', 'of']
        city = ['city']
        if state_of in abutterance:
            i = abutterance.index(state_of)
            if i + 2 < len(abutterance) and abutterance[i + 2].startswith('CITY'):
                state_val = abutterance[i + 2][5:]
                abutterance = abutterance.replace(abutterance[i + 2], 'STATE=' + state_val)
        if city in abutterance:
            i = abutterance.index(city)
            if i >= 0 and abutterance[i - 1].startswith('STATE'):
                city_val = abutterance[i - 1][6:]
                abutterance = abutterance.replace(abutterance[i - 1], 'CITY=' + city_val)
            # elif i + 1 < len(abutterance) and abutterance[i + 1].startswith('CITY'):
            #     city_val = abutterance[i + 1][6:]
            #     abutterance = abutterance.replace(abutterance[i + 1], 'CITY=' + city_val)
        return abutterance

    def parse_1_best(self, obs, verbose=False, *args, **kwargs):
        """Parse an utterance into a dialogue act.

        :rtype DialogueActConfusionNetwork
        """

        utterance = obs['utt']

        if isinstance(utterance, UtteranceHyp):
            # Parse just the utterance and ignore the confidence score.
            utterance = utterance.utterance

        if verbose:
            print 'Parsing utterance "{utt}".'.format(utt=utterance)

        res_cn = DialogueActConfusionNetwork()

        dict_da = self.utt2da.get(unicode(utterance), None)
        if dict_da:
            for dai in DialogueAct(dict_da):
                res_cn.add(1.0, dai)
            return res_cn

        utterance = self.preprocessing.normalise_utterance(utterance)
        abutterance, category_labels, abutterance_lenghts = self.abstract_utterance(utterance)

        if verbose:
            print 'After preprocessing: "{utt}".'.format(utt=abutterance)
            print category_labels

        self.parse_non_speech_events(utterance, res_cn)

        utterance = utterance.replace_all(['_noise_'], '').replace_all(['_laugh_'], '').replace_all(['_ehm_hmm_'], '').replace_all(['_inhale_'], '')
        abutterance = abutterance.replace_all(['_noise_'], '').replace_all(['_laugh_'], '').replace_all(['_ehm_hmm_'], '').replace_all(['_inhale_'], '')

        abutterance = self.handle_false_abstractions(abutterance)
        category_labels.add('STATE')
        category_labels.add('NUMBER')

        if len(res_cn) == 0:
            if 'STREET' in category_labels:
                self.parse_street(abutterance, res_cn)
            if 'NEIGHBORHOOD' in category_labels:
                self.parse_neighborhood(abutterance, res_cn)
            if 'POI' in category_labels:
                self.parse_poi(abutterance, res_cn)
            if 'ROUTE' in category_labels:
                self.parse_route(abutterance, res_cn)
            if 'NUMBER' in category_labels:
                self.parse_number(abutterance)
                if any([word.startswith("TIME") for word in abutterance]):
                    category_labels.add('TIME')
            if 'TIME' in category_labels:
                self.parse_time(abutterance, res_cn)
            if 'DATE_REL' in category_labels:
                self.parse_date_rel(abutterance, res_cn)
            if 'AMPM' in category_labels:
                self.parse_ampm(abutterance, res_cn)

            self.parse_meta(utterance, abutterance_lenghts, res_cn)

        return res_cn

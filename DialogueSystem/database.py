#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

if __name__ == '__main__':
    import autopath
import codecs
import os
import re
import sys

from alex.utils.config import online_update, to_project_path


__all__ = ['database']


database = {
    "number": {
        str("1"): [str("one")]
    },
    "time": {
        "now": ["now", "at once", "immediately", "offhand", "at this time", "the closest", "this instant"],
    },
    "date_rel": {
        "today": ["today", "this day", "todays", "this days", "tonight"],
        "tomorrow": ["tomorrow", "tomorrows", "morrow", "morrows"],
        "day_after_tomorrow": ["day after tomorrow", "after tomorrow", "after tomorrows"],
    },
    "ampm": {
        "am": ["forenoon", "a.m.", "a m", "morning","dawn",],
        "pm": ["afternoon", "p.m.", "p m"],
        "evening": ["evening", "dusk", ],
        "night": ["night", "nighttime", "midnight", "tonight"],
    },
    "route": {
    },
    "neighborhood": {
    },
    "street": {
    },
    "poi": {
    },
}

NUMBERS_1 = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", ]
NUMBERS_10 = ["", "ten", "twenty", "thirty", "forty", "fifty", "sixty", ]
NUMBERS_TEEN = ["ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
                "sixteen", "seventeen", "eighteen", "nineteen"]
# NUMBERS_ORD = ["zero", "first", "second", "third", "fourth", "fifth", "sixth", # nultý - zero/prime?
#                "seventh", "eighth", "ninth", "tenth", "eleventh", "twelfth",
#                "thirteenth", "fourteenth", "fifteenth", "sixteenth", "seventeenth",
#                "eighteenth", "nineteenth", "twentieth", "twenty first",
#                "twenty second", "twenty third"]

# name of the file with one stop per line, assumed to reside in the same
# directory as this script
#
# The file is expected to have this format:
#   <value>; <phrase>; <phrase>; ...
# where <value> is the value for a slot and <phrase> is its possible surface
# form.
STREETS_FNAME = "streets.expanded.txt"
NEIGHBORHOODS_FNAME = "neighborhoods.expanded.txt"
ROUTES_FNAME = "routes.expanded.txt"
POIS_FNAME = "pois.expanded.txt"

def db_add(category_label, value, form):
    """A wrapper for adding a specified triple to the database."""
#    category_label = category_label.strip()
#    value = value.strip()
#    form = form.strip()

    if len(value) == 0 or len(form) == 0:
        return

    if value in database[category_label] and isinstance(database[category_label][value], list):
        database[category_label][value] = set(database[category_label][value])

    database[category_label].setdefault(value, set()).add(form)


def spell_number(num):
    """Spells out the number given in the argument. not greater than 69"""
    tens, units = num / 10, num % 10
    tens_str = NUMBERS_10[tens]
    units_str = NUMBERS_1[units]
    if tens == 1:
        return NUMBERS_TEEN[units]
    elif tens:
        if units:
            return "{t} {u}".format(t=tens_str, u=units_str)
        return "{t}".format(t=tens_str)
    else:
        return units_str


def add_numbers():
    """
    Basic approximation of all known explicit number expressions.

    Handles:
        fractions (quarter/half)
        cardinal numbers <1, 59>
    """

    for fraction, fraction_spelling in [(0.25, 'quarter'), (0.5, 'half')]:
        add_db_number(fraction, fraction_spelling)

    for cardinal in xrange(60):
        add_db_number(cardinal, spell_number(cardinal))

    for single_digit in xrange(9):
        add_db_number(single_digit, "zero " + spell_number(single_digit))
        add_db_number(single_digit, "o " + spell_number(single_digit))

def add_db_number(number, spelling):
    """Add a number expression to the database (given number and its spelling)."""
    db_add("number", str(number), spelling)


def preprocess_cl_line(line):
    """Process one line in the category label database file."""
    name, forms = line.strip().split("\t")
    forms = [form.strip() for form in forms.split(';')]
    return name, forms


def add_from_file(category_label, fname):
    """Adds to the database names + surface forms of all category labels listed in the given file.
    The file must contain the category lablel name + tab + semicolon-separated surface forms on each
    line.
    """
    dirname = os.path.dirname(os.path.abspath(__file__))
    with codecs.open(os.path.join(dirname, fname), encoding='utf-8') as stops_file:
        for line in stops_file:
            if line.startswith('#'):
                continue
            val_name, val_surface_forms = preprocess_cl_line(line)
            for form in val_surface_forms:
                db_add(category_label, val_name, form)

def add_routes():
    add_from_file('route', ROUTES_FNAME)

def add_pois():
    add_from_file('poi', POIS_FNAME)

def add_neighborhoods():
    add_from_file('neighborhood', NEIGHBORHOODS_FNAME)

def add_streets():
    """Add street names from the streets file."""
    add_from_file('street', STREETS_FNAME)


def save_c2v2f(file_name):
    c2v2f = []
    for k in database:
        for v in database[k]:
            for f in database[k][v]:
                if re.search('\d', f):
                    continue
                c2v2f.append((k, v, f))

    c2v2f.sort()

    # save the database vocabulary - all the surface forms
    with codecs.open(file_name, 'w', 'UTF-8') as f:
        for x in c2v2f:
            f.write(' => '.join(x))
            f.write('\n')


def save_surface_forms(file_name):
    surface_forms = []
    for k in database:
        for v in database[k]:
            for f in database[k][v]:
                if re.search('\d', f):
                    continue
                surface_forms.append(f)
    surface_forms.sort()

    # save the database vocabulary - all the surface forms
    with codecs.open(file_name, 'w', 'UTF-8') as f:
        for sf in surface_forms:
            f.write(sf)
            f.write('\n')


def save_SRILM_classes(file_name):
    surface_forms = []
    for k in database:
        for v in database[k]:
            for f in database[k][v]:
                if re.search('\d', f):
                    continue
                surface_forms.append("CL_" + k.upper() + " " + f.upper())
    surface_forms.sort()

    # save the database vocabulary - all the surface forms
    with codecs.open(file_name, 'w', 'UTF-8') as f:
        for sf in surface_forms:
            f.write(sf)
            f.write('\n')

########################################################################
#                  Automatically expand the database                   #
########################################################################
add_numbers()
add_streets()
add_neighborhoods()
add_routes()
add_pois()


if __name__ == '__main__':
    if "dump" in sys.argv or "--dump" in sys.argv:
        save_c2v2f('database_c2v2f.txt')
        save_surface_forms('database_surface_forms.txt')
        save_SRILM_classes('database_SRILM_classes.txt')

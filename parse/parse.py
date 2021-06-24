from fuzzywuzzy import fuzz
from fuzzywuzzy import process


def match(text, choices):
    m = process.extractOne(text, choices)
    return m

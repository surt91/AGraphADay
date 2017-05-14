from fuzzywuzzy import fuzz
from fuzzywuzzy import process


def match(text, choices):
    m = process.extractOne(text, choices, scorer=fuzz.partial_ratio)
    return m

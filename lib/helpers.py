import random
import string


def random_string(length):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(length))


def get_dict_wo_key(dictionary, key):
    """Returns a **shallow** copy of the dictionary without a key."""
    _dict = dictionary.copy()
    _dict.pop(key, None)
    return _dict

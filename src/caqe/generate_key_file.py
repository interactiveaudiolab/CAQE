#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generates `secret_keys.py` which contains the crypto keys for sessions and CSRF. Run on the command line, e.g.:

    $ python generate_key_file.py

"""

import random
import string

KEY_LENGTH = 32  # Key must be this length


def main():
    with open('secret_keys.py', 'w') as f:
        f.writelines('\n'.join(['# DO NOT PUT UNDER VERSION CONTROL',
                                'SESSION_KEY = \'%s\'' % ''.join([random.choice(string.hexdigits) for
                                                                  _ in xrange(KEY_LENGTH)]),
                                'CSRF_SECRET_KEY = \'%s\'' % ''.join([random.choice(string.hexdigits) for
                                                                      _ in xrange(KEY_LENGTH)]),
                                'AWS_ACCESS_KEY_ID = \'<INSERT YOUR AWS ACCESS KEY ID>\'',
                                'AWS_SECRET_KEY = \'<INSERT YOUR AWS SECRET KEY>\'']),)


if __name__ == "__main__":
    main()

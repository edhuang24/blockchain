# -*- coding: utf-8 -*-

# Write two methods, one called mint and one called verify.
#
# mint
#
# mint should take two arguments: a challenge (random string) and a work_factor (number of leading 0s in the hash).
# It should return a token, which is a random string such that SHA2(challenge || token) starts with at least work_factor many 0s.
# Use hex encoding rather than binary encoding for simplicity. (You’ll want no more than 4 for your work factor.)
# verify
#
# This should take three arguments: the challenge, the work_factor, and the token.
# It should return true or false based on whether the token is valid.

import hashlib
import time
import ipdb

max_nonce = 2 ** 32
cache = []

def mint(challenge, work_factor):
    """function(str, int) -> [str, int, float]

    Takes in a challenge and work_factor/difficulty and returns a token
    that includes the SHA-256 hash result, nonce, and current time in seconds
    """
    current_time = time.ctime()
    for nonce in xrange(max_nonce):
        hash_result = hashlib.sha256(str(challenge) + str(current_time) + str(nonce)).hexdigest()
        print([nonce, current_time, hash_result])

        if hash_result[:work_factor] == "0" * work_factor:
            # print nonce, hash_result
            append_to_cache(hash_result)
            token = [hash_result, nonce, current_time]
            return token

    print("failed to match challenge")
    return None

def verify(challenge, token):
    """function(str, str) -> bool

    Takes in a challenge & token and confirms whether
    the token solves the challenge
    """
    if token[0] in cache:
        return False

    token_hash = hashlib.sha256(str(challenge) + str(token[2]) + str(token[1])).hexdigest()
    if token_hash == token[0]:
        return True
    else:
        return False

def append_to_cache(hash):
    cache.pop(0) if len(cache) >= 5 else None
    cache.append(hash)

# TEST CODE below:
if __name__ == '__main__':
    challenge1 = "adsljassadlkfjalkj"
    # challenge2 = "ioewunlksenemfsdlk"
    # challenge3 = "8974hddlkw9023n342"
    # challenge4 = "435)&#%asdjenrlk+/"
    # challenge5 = "FH4klnf~!#@982{}|<"
    # challenge6 = "hellogoodbyehello!"
    token1 = mint(challenge1, 5)
    print token1
    # token2 = mint(challenge2, 4)
    # token3 = mint(challenge3, 4)
    # token4 = mint(challenge4, 4)
    # token5 = mint(challenge5, 4)
    # token6 = mint(challenge6, 4)
    print verify(challenge1, token1)

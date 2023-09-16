import random
from string import ascii_uppercase, digits

CHARACTER_POOL = ascii_uppercase + digits


def generate_invite_code():
    code = ''.join(random.choices(CHARACTER_POOL, k=6))
    return code
def send_email():
    pass
class CodeExpired(Exception):
    pass
import random, string

def generate(length=8):
    return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(length)])

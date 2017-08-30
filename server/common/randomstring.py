import random, string

def generate(n):
    return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(128)])

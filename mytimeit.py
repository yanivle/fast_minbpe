import time

def timeit(f, name):
    start = time.time()
    res = f()
    print(f'{name} took {time.time() - start:.2f} seconds.')
    return res
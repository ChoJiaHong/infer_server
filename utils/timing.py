import time

def timing_decorator(label):
    def decorator(func):
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            print(f"[Trace] {label}: {(end - start)*1000:.2f} ms")
            return result
        return wrapper
    return decorator

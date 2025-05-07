verbose = False


def log(msg):
    if verbose:
        print(msg)


def log_warning(msg):
    if verbose:
        print("\033[93m" + msg + "\033[0m")


def log_error(msg):
    if verbose:
        print("\033[31m" + msg + "\033[0m")


def log_result(msg):
    if verbose:
        print("\033[32m" + msg + "\033[0m")

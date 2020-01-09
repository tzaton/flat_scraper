import locale
import contextlib


@contextlib.contextmanager
def set_locale(*args, **kwargs):
    """ Change locale """
    old = locale.setlocale(locale.LC_ALL)
    yield locale.setlocale(*args, **kwargs)
    locale.setlocale(locale.LC_ALL, old)

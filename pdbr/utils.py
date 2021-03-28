import atexit
import configparser
import os

from pdbr._pdbr import rich_pdb_klass

try:
    import readline
except ImportError:
    from pyreadline import Readline

    readline = Readline()


def set_history_file(history_file):
    """
    This is just for Pdb,
    For Ipython, look at RichPdb.pt_init
    """

    try:
        readline.read_history_file(history_file)
        readline.set_history_length(1000)
    except FileNotFoundError:
        pass

    atexit.register(readline.write_history_file, history_file)


def set_traceback(theme):
    from rich.traceback import install

    install(theme=theme)


def read_config():
    style = None
    theme = None
    store_history = ".pdbr_history"

    config = configparser.ConfigParser()
    config.sections()
    config.read("setup.cfg")
    if "pdbr" in config:
        if "style" in config["pdbr"]:
            style = config["pdbr"]["style"]
        if "theme" in config["pdbr"]:
            theme = config["pdbr"]["theme"]
        if "use_traceback" in config["pdbr"]:
            if config["pdbr"]["use_traceback"].lower() == "true":
                set_traceback(theme)
        if "store_history" in config["pdbr"]:
            store_history = config["pdbr"]["store_history"]

    history_file = os.path.join(os.path.expanduser("~"), store_history)
    set_history_file(history_file)
    ipython_history_file = f"{history_file}_ipython"

    return style, theme, history_file, ipython_history_file


def debugger_cls(klass=None, context=None, is_celery=False):
    if klass is None:
        try:
            from IPython.terminal.debugger import TerminalPdb

            klass = TerminalPdb
        except BaseException:
            from pdb import Pdb

            klass = Pdb

    RichPdb = rich_pdb_klass(klass, context=context, is_celery=is_celery)
    style, theme, history_file, ipython_history_file = read_config()
    RichPdb._style = style
    RichPdb._theme = theme
    RichPdb._history_file = history_file
    RichPdb._ipython_history_file = ipython_history_file

    return RichPdb


def _pdbr_cls(context=None, return_instance=True):
    klass = debugger_cls(context=context)
    if return_instance:
        return klass()
    return klass


def _rdbr_cls(return_instance=True):
    try:
        from celery.contrib import rdb

        rdb.BANNER = """\
{self.ident}: Type `pdbr_telnet {self.host} {self.port}` to connect

{self.ident}: Waiting for client...
"""
    except ModuleNotFoundError as error:
        raise type(error)("In order to install celery, use pdbr[celery]") from error

    klass = debugger_cls(klass=rdb.Rdb, is_celery=True)
    if return_instance:
        return klass()
    return klass

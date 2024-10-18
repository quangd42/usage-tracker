from .plugin import LoggerPlugin
import subprocess
import sys


try:
    import pynput
except ImportError:
    modules = ['pynput']
    subprocess.call([sys.executable, '-m', 'pip', 'install', '-q'] + modules)
    try:
        import pynput
    except ImportError as e:
        raise ImportError(
            'Could not auto-install pynput. Please `pip install pynput` in your neovim python environment'
        ) from e

__all__ = ['LoggerPlugin']

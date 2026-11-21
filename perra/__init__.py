"""Perra (Persona Radar)"""

__title__ = 'Perra'
__package__ = 'perra'
__author__ = 'codevcn (based on Maigret by Soxoj)'
__author_email__ = 'soxoj@protonmail.com'


from .__version__ import __version__
try:
    from .checking import perra as search
except ImportError as e:
    raise ImportError(
        "Missing required dependency while starting Perra.\n\n"
        "If running from a cloned repository:\n"
        "    pip install -e .\n\n"
        "Or run the setup manager:\n"
        "    python scripts/setup_manager.py install\n\n"
        "Then run Perra as:\n"
        "    python -m perra <username>"
    ) from e
from .perra import main as cli
from .sites import PerraEngine, PerraSite, PerraDatabase
from .notify import QueryNotifyPrint as Notifier

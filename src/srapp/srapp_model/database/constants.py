from typing import *

from model import LocalToRemote

DATABASE_VERSION = 'V1'
DEFAULT_PROJECT = 'projekt_testowy'

SHEARS_SIZE: int = 18
DEFAULT_PROBE_INTERVAL: float = 0.1
EXUDATION_TYPES: Set[str] = {'1', '2', '3'}
WATER_HORIZONS: Set[str] = {'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X'}
SOIL_TYPES: Set[str] = {
    "",
    "Pr",
    "Ps",
    "Pd",
    "Pπ",
    "Po",
    "Pog",
    "Ż",
    "Żg",
    "Pg",
    "Πp",
    "Π",
    "Gp",
    "G",
    "Gπ",
    "Gpz",
    "Gz",
    "Gπz",
    "Ip",
    "I",
    "Iπ",
    "KW",
    "KWg",
    "KR",
    "KRg",
    "KO",
    "Li",
    "Nm",
    "Nmp",
    "Nmg",
    "T",
    "Gy",
    "nN",
    "nB",
    "C",
    "B",
    "D",
    "żl",
    "Gb",
    "H",
    "W",
}
STATUS_EMPTY = 'EMPTY'
STATUSES_REMOTE_TO_LOCAL: LocalToRemote[str, str] = LocalToRemote([
    (STATUS_EMPTY, ''),
    ('TO_REVIEW', 'Do sprawdzenia'),
    ('TODO', 'Do zrobienia'),
    ('DONE', 'Zrobiony'),
    ('TO_CORRECT', 'Do poprawy'),
    ('FORBIDDEN', 'Zakazany'),
    ('OTHER', 'Inny')
])

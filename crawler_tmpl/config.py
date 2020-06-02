from configparser import ConfigParser
from pathlib import Path

config = ConfigParser()
filepath = str(Path(f"{__file__}/../../config.ini").resolve())
config.read(filepath)
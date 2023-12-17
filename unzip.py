import json
import pickle
import platform
import sys
import zipfile
from pathlib import Path
from calibre.utils.config import config_dir

PLUGIN_PATH = Path(config_dir).joinpath('plugins/GR Author Notes.zip')
PY_VERSION = '.'.join(platform.python_version_tuple()[:2])
LIBS_PATH = Path(config_dir).joinpath(f"plugins/gr_author_notes-libs-py{PY_VERSION}")

def load_json_or_pickle(filepath, is_json):
    with zipfile.ZipFile(PLUGIN_PATH) as zf:
        with zf.open(filepath) as f:
            if is_json:
                return json.load(f)
            else:
                return pickle.load(f)

def install_libs():
    pluginzip = zipfile.ZipFile(PLUGIN_PATH)
    filenames = [i for i in pluginzip.namelist() if i.startswith(('bs4', 'certifi', 'idna', 'urllib3', 'requests'))]

    for file in filenames:
        pluginzip.extract(file, LIBS_PATH)
        
    if LIBS_PATH not in sys.path:
        sys.path.insert(0, str(LIBS_PATH))
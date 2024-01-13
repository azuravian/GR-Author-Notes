import platform
import sys
import zipfile
from pathlib import Path

from calibre.constants import ismacos, iswindows # type: ignore
from calibre.utils.config import config_dir # type: ignore

PLUGIN_PATH = Path(config_dir).joinpath('plugins/GR Author Notes.zip')
PY_VERSION = '.'.join(platform.python_version_tuple()[:2])
LIBS_PATH = Path(config_dir).joinpath(f"plugins/gr_author_notes-libs-py{PY_VERSION}")

def install_libs():
    pluginzip = zipfile.ZipFile(PLUGIN_PATH)
    filenames = [i for i in pluginzip.namelist() if i.startswith(('bs4', 'certifi', 'idna', 'urllib3', 'requests', 'googletrans', 'httpcore', 'sniffio', 'h2', 'hyperframe', 'hpack', 'h11', 'httpx', 'hstspreload', 'rfc3986'))]

    for file in filenames:
        pluginzip.extract(file, LIBS_PATH)
        
    if LIBS_PATH not in sys.path:
        sys.path.insert(0, str(LIBS_PATH))

def install_chrome():
    cfolder = LIBS_PATH.joinpath('chromedriver')
    if iswindows:
        chromepath = cfolder.joinpath('chromedriver.exe')
        if chromepath.is_file():
            print(f'chrome found at {chromepath}')
            return chromepath
        driverzip = cfolder.joinpath('chromedriver_win32.zip')
    else:
        chromepath = cfolder.joinpath('chromedriver')
        if chromepath.is_file():
            print(f'chrome found at {chromepath}')
            return chromepath
        if ismacos:
            if sys.platform() == "darwin64":
                print(help)
                driverzip = cfolder.joinpath('chromedriver_mac_arm64.zip')
            else:
                driverzip = cfolder.joinpath('chromedriver_mac64.zip')    
        else:
            driverzip = cfolder.joinpath('chromedriver_linux64.zip')
    with zipfile.ZipFile(driverzip, 'r') as cdriver:
        cdriver.extractall(cfolder)
    return chromepath
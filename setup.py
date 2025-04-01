from setuptools import setup

APP = ['main.py']
DATA_FILES = ['icon.png', 'main.ui', 'resource.qrc']
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'icon.png',
    'plist': {
        'CFBundleName': 'cloud-clipboard-go',
        'CFBundleDisplayName': 'cloud-clipboard-go',
        'CFBundleIdentifier': 'com.jonnyan404.cloudclipboard',
        'CFBundleVersion': 'v0.0.0',
        'CFBundleShortVersionString': 'v0.0.0',
        'NSHighResolutionCapable': True,
    },
    'packages': ['PyQt5'],
    'includes': ['PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets'],
    'qt_plugins': ['styles', 'platforms/libqcocoa.dylib'],
    'exclude': ['matplotlib', 'pandas', 'numpy'],  # 排除不需要的大型包
}

setup(
    app=APP,
    name='cloud-clipboard-go',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
from setuptools import setup

APP = ['main.py']
DATA_FILES = ['icon.png', 'main.ui', 'resource.qrc']
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'icon.png',
    'plist': {
        'CFBundleName': 'Cloud Clipboard',
        'CFBundleDisplayName': 'Cloud Clipboard',
        'CFBundleIdentifier': 'com.jonnyan404.cloudclipboard',
        'CFBundleVersion': 'v0.0.0',  # 将在构建时被替换为实际版本
        'CFBundleShortVersionString': 'v0.0.0',  # 将在构建时被替换为实际版本
        'NSHighResolutionCapable': True,
    },
    'packages': ['PyQt5'],
}

setup(
    app=APP,
    name='Cloud Clipboard',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
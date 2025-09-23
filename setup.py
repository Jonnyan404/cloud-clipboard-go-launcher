from setuptools import setup
import time

APP = ['main.py']
DATA_FILES = ['icon.png', 'main.ui', 'resource.qrc']

OPTIONS = {
    # 关键修改：禁用参数模拟，这是使用Carbon框架的原因
    'argv_emulation': False,
    'iconfile': 'icon.png',
    'universal': True ,  # 构建通用二进制文件，支持arm64和x86_64
    'plist': {
        'CFBundleName': 'cloud-clipboard-go',
        'CFBundleDisplayName': 'cloud-clipboard-go',
        'CFBundleIdentifier': 'com.jonnyan404.cloudclipboard',
        'CFBundleVersion': 'v0.0.0',  # 将在构建时被替换为实际版本
        'CFBundleShortVersionString': 'v0.0.0',  # 将在构建时被替换为实际版本
        'NSHighResolutionCapable': True,
        # 强制清除应用程序缓存
        'LSApplicationCategoryType': 'public.app-category.utilities',
        'BuildTimestamp': str(int(time.time()))
    },
    'packages': ['PyQt5'],
}

setup(
    app=APP,
    name='cloud-clipboard-go',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)

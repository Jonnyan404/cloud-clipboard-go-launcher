import configparser
import os
import subprocess
import sys
from threading import Thread
import platform

import requests
from PyQt5.QtCore import pyqtSlot, Qt, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QSystemTrayIcon, QMenu, QLineEdit

# 先创建QApplication实例（必须放在最前面）
app = QApplication(sys.argv)
from ui import Ui_MainWindow
from utils import get_ips, system_related_secret, get_latest_version

# 修改文件名逻辑
base_filename = "cloud-clipboard-go"
config_file = "cloud-clipboard-go-launcher.ini"
version = "v0.0.0"
is_windows = os.name == "nt"
use_shell = is_windows

# 获取系统架构
arch = platform.machine().lower()
if arch in ("x86_64", "amd64"):
    arch_str = "x86_64"
elif arch in ("aarch64", "arm64"):
    arch_str = "aarch64"
elif arch == "i386":
    arch_str = "i386"
elif arch.startswith("arm"):
    arch_str = "armv7"
else:
    arch_str = "x86_64"  # 默认

if sys.platform == 'darwin':
    os_str = "Darwin"
    filename = f"{base_filename}"
    exec_filename = f"./{filename}"
    download_filename = f"{base_filename}_Darwin_{arch_str}.tar.gz"
    
    # 使用更可靠的方法获取目录路径
    try:
        # 获取绝对路径
        dir_path = os.path.dirname(os.path.abspath(sys.argv[0]))
        if dir_path:
            print(f"切换到目录: {dir_path}")
            os.chdir(dir_path)
    except Exception as e:
        print(f"切换目录失败: {e}")
elif sys.platform == 'linux':
    os_str = "Linux"
    filename = f"{base_filename}"
    exec_filename = f"./{filename}"
    download_filename = f"{base_filename}_Linux_{arch_str}.tar.gz"
elif is_windows:
    os_str = "Windows"
    filename = f"{base_filename}.exe"
    exec_filename = filename
    download_filename = f"{base_filename}_Windows_{arch_str}.zip"
else:
    # 默认情况
    os_str = "Unknown"
    filename = base_filename
    exec_filename = f"./{filename}"
    download_filename = f"{base_filename}_Linux_x86_64.tar.gz"

os.environ["SESSION_SECRET"] = system_related_secret()

# macOS程序坞图标设置（放在QApplication创建之后）
if sys.platform == 'darwin':
    try:
        # 创建应用图标
        app_icon = QIcon("icon.png")  # 确保icon.png文件存在
        
        # 设置应用图标
        app.setWindowIcon(app_icon)
        
        # macOS特定设置
        app.setAttribute(Qt.AA_UseHighDpiPixmaps)
        
        # 设置应用名称和ID
        app.setApplicationName("Cloud Clipboard")
        
        # 在macOS中，这个会显示在程序坞和菜单栏中
        app.setApplicationDisplayName("Cloud Clipboard")
    except Exception as e:
        print(f"设置macOS图标失败: {e}")


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon(":/icon.png"))
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(QIcon(":/icon.png"))
        self.tray.setVisible(True)

        def activate_tray(reason):
            if reason == QSystemTrayIcon.Trigger:
                self.show()

        self.tray.activated.connect(activate_tray)
        self.menu = QMenu()
        self.menu.setFont(self.font())
        show_action = self.menu.addAction("设置")
        show_action.triggered.connect(self.show)
        quit_action = self.menu.addAction("退出")
        quit_action.triggered.connect(self.quit)
        self.tray.setContextMenu(self.menu)
        self.gofile = None
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.ips = get_ips()
        self.ips.insert(0, "localhost")
        for ip in self.ips:
            self.hostComboBox.addItem(ip, ip)
        if 'host' in self.config['DEFAULT']:
            host = self.config['DEFAULT']['host']
            if host in self.ips:
                idx = self.ips.index(host)
            else:
                idx = 0
            self.hostComboBox.setCurrentIndex(idx)
        self.hostComboBox.currentIndexChanged.connect(lambda v: self.update_config("host", self.ips[v]))
        if 'port' in self.config['DEFAULT']:
            self.portSpinBox.setValue(int(self.config['DEFAULT']['port']))
        self.portSpinBox.textChanged.connect(lambda v: self.update_config("port", v))
        if 'file' in self.config['DEFAULT']:
            self.fileLineEdit.setText(self.config['DEFAULT']['file'])
        self.fileLineEdit.textChanged.connect(lambda v: self.update_config("file", v))
        if 'video' in self.config['DEFAULT']:
            self.videoLineEdit.setText(self.config['DEFAULT']['video'])

        # 设置密码输入框为密码模式（显示为星号）
        self.videoLineEdit.setEchoMode(QLineEdit.Password)
        # 添加密码可见状态变量
        self.password_visible = False

        self.videoLineEdit.textChanged.connect(lambda v: self.update_config("video", v))
        self.aboutMsgBox = QMessageBox()
        self.aboutMsgBox.setFont(self.font())
        self.aboutMsgBox.setWindowIcon(QIcon(":/icon.png"))
        self.aboutMsgBox.setIcon(QMessageBox.Information)
        self.aboutMsgBox.setWindowTitle("关于")
        self.aboutMsgBox.setText(
            f"cloud-clipboard-go Launcher {version} 由 Jonnyan404 构建，<a href='https://github.com/jonnyan404/cloud-clipboard-go-launcher'>源代码</a>遵循 MIT 协议")
        self.NotFoundMsgBox = QMessageBox()
        self.NotFoundMsgBox.setFont(self.font())
        self.NotFoundMsgBox.setWindowIcon(QIcon(":/icon.png"))
        self.NotFoundMsgBox.setIcon(QMessageBox.Information)
        self.NotFoundMsgBox.setWindowTitle(f"未能找到 {filename}")
        self.NotFoundMsgBox.setText("请点击下载按钮进行下载或者手动下载后放到本启动器相同目录下")
        if not os.path.exists(f"./{filename}"):
            self.updateBtn.setText("下载 cloud-clipboard-go")

    def closeEvent(self, event):
        if self.gofile is None:
            event.accept()
        else:
            self.hide()
            event.ignore()

    def quit(self):
        with open(config_file, 'w') as cfg:
            self.config.write(cfg)
        if self.gofile is not None:
            self.on_startBtn_clicked()
        app.quit()

    def update_config(self, key, value):
        self.config['DEFAULT'][key] = value

    @pyqtSlot()
    def on_startBtn_clicked(self):
        if self.gofile is None:
            if os.path.exists(f"./{filename}"):
                port = self.portSpinBox.text()
                host = self.hostComboBox.currentText()
                file_path = self.fileLineEdit.text()
                video_path = self.videoLineEdit.text()
                self.gofile = subprocess.Popen(
                    [f"{exec_filename}", "-port", f"{port}", "-host", f"{host}", "-config", f"{file_path}", "-auth",
                     f"{video_path}"], shell=use_shell, cwd="./")
                self.statusbar.showMessage("服务已启动")
                self.startBtn.setText("终止")
            else:
                self.NotFoundMsgBox.show()
        else:
            if os.name == "nt":
                subprocess.Popen("TASKKILL /F /PID {pid} /T".format(pid=self.gofile.pid), shell=True)
            else:
                # Not tested.
                # https://stackoverflow.com/questions/4789837/how-to-terminate-a-python-subprocess-launched-with-shell-true
                self.gofile.kill()
            self.gofile = None
            self.statusbar.showMessage("服务已终止")
            self.startBtn.setText("启动")

    @pyqtSlot()
    def on_fileChooseBtn_clicked(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择配置文件", ".", "配置文件 (*.json *.yaml *.yml *.conf);;所有文件 (*)")
        if path:
            self.fileLineEdit.setText(path)
            self.statusbar.showMessage(f"已选择：{path}")

    @pyqtSlot()
    def on_videoChooseBtn_clicked(self):
        from PyQt5.QtWidgets import QLineEdit
        
        # 获取当前密码
        current_password = self.videoLineEdit.text()
        
        if not current_password:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                "提示",
                "未设置密码，请先在输入框中输入密码",
                QMessageBox.Ok
            )
            return
        
        # 切换密码显示/隐藏状态
        self.password_visible = not self.password_visible
        
        if self.password_visible:
            # 显示密码
            self.videoLineEdit.setEchoMode(QLineEdit.Normal)
            self.videoChooseBtn.setText("隐藏密码")
            self.statusbar.showMessage("密码已显示")
        else:
            # 隐藏密码
            self.videoLineEdit.setEchoMode(QLineEdit.Password)
            self.videoChooseBtn.setText("查看密码")
            self.statusbar.showMessage("密码已隐藏")
        
    @pyqtSlot()
    def on_aboutBtn_clicked(self):
        self.aboutMsgBox.show()

    @pyqtSlot()
    def on_updateBtn_clicked(self):
        if os.path.exists(f"./{filename}"):
            process = subprocess.Popen([f"{exec_filename}", '-v'], stdout=subprocess.PIPE, shell=use_shell,
                                       cwd="./")
            output = process.communicate()[0]
            current_version = output.decode('utf-8')
            current_version = current_version.rstrip("\n")
            self.statusbar.showMessage(f"正在请求 GitHub 服务器查询当前最新版本 ...")
            core_latest_version = get_latest_version("cloud-clipboard-go")
            if core_latest_version is None:
                self.statusbar.showMessage(f"无法连接到 GitHub 服务器")
                return
            if core_latest_version == current_version:
                self.statusbar.showMessage(f"Go File 已是最新版：{core_latest_version}")
                launcher_latest_version = get_latest_version("cloud-clipboard-go-launcher")
                if launcher_latest_version is not None and launcher_latest_version != version:
                    self.statusbar.showMessage(
                        f"cloud-clipboard-go 已是最新版：{core_latest_version}，启动器更新可用：{version}->{launcher_latest_version}")
                    return
                self.statusbar.showMessage(f"已是最新版：cloud-clipboard-go {core_latest_version} & 启动器 {version}")
                return
        worker = ThreadDownloader(self.statusbar, self.updateBtn)
        worker.start()


class ThreadDownloader(Thread):
    def __init__(self, statusbar, updateBtn):
        super().__init__()
        self.statusbar = statusbar
        self.updateBtn = updateBtn

    def run(self):
        self.updateBtn.setEnabled(False)
        self.statusbar.showMessage("正在从 GitHub 上获取最新版 ...")
        
        download_url = f"https://github.com/jonnyan404/cloud-clipboard-go/releases/latest/download/{download_filename}"
        self.statusbar.showMessage(f"正在下载: {download_url}")
        
        try:
            res = requests.get(download_url)
            if res.status_code != 200:
                self.statusbar.showMessage(f"下载失败：HTTP {res.status_code} - {res.text}")
                self.updateBtn.setEnabled(True)
                return
                
            # 保存压缩包
            temp_file = f"./temp_{download_filename}"
            with open(temp_file, "wb") as f:
                f.write(res.content)
            
            # 根据文件类型解压
            if download_filename.endswith('.tar.gz'):
                import tarfile
                with tarfile.open(temp_file, "r:gz") as tar:
                    tar.extract(base_filename, ".")
            elif download_filename.endswith('.zip'):
                import zipfile
                with zipfile.ZipFile(temp_file, 'r') as zip_ref:
                    for file in zip_ref.namelist():
                        if file.endswith(filename):
                            with open(f"./{filename}", "wb") as f:
                                f.write(zip_ref.read(file))
                            break
            
            # 删除临时文件
            os.remove(temp_file)
            
            # 设置可执行权限
            if os.name != "nt":
                subprocess.run(["chmod", "u+x", f"./{filename}"])
                
            self.statusbar.showMessage(f"下载并解压完成")
        except Exception as e:
            self.statusbar.showMessage(f"下载或解压过程出错: {str(e)}")
        finally:
            self.updateBtn.setEnabled(True)
            self.updateBtn.setText("检查更新")


if __name__ == "__main__":
    Dialog = MainWindow()
    Dialog.show()
    sys.exit(app.exec_())

import configparser
import os
import subprocess
import sys
from threading import Thread
import platform
import time

import requests
from PyQt5.QtCore import pyqtSlot, Qt, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QGroupBox, QRadioButton, QTabWidget, QWidget,QCheckBox, QComboBox, QDialog,QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,QLineEdit,QApplication, QMainWindow, QFileDialog, QMessageBox, QSystemTrayIcon, QMenu, QLineEdit
from configparser import ConfigParser 
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
        self.ips.insert(1, "0.0.0.0")
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

        # 添加代理配置相关逻辑
        if 'PROXY' not in self.config:
            self.config['PROXY'] = {}
            
        # 设置默认代理类型为URL
        if 'type' not in self.config['PROXY']:
            self.config['PROXY']['type'] = 'url'
            
        # 默认加速URL
        if 'url' not in self.config['PROXY']:
            self.config['PROXY']['url'] = "https://gh-proxy.com"
            
        if 'enabled' not in self.config['PROXY']:
            self.config['PROXY']['enabled'] = 'False'
            
        # 传统代理的默认值
        if 'proxy_type' not in self.config['PROXY']:
            self.config['PROXY']['proxy_type'] = 'HTTP'
            
        if 'proxy_server' not in self.config['PROXY']:
            self.config['PROXY']['proxy_server'] = '127.0.0.1'
            
        if 'proxy_port' not in self.config['PROXY']:
            self.config['PROXY']['proxy_port'] = '7897'
            
        if 'auth_enabled' not in self.config['PROXY']:
            self.config['PROXY']['auth_enabled'] = 'False'

        # 将代理设置按钮与处理函数连接
        self.proxy_dialog_active = False
        self._last_proxy_dialog_close_time = 0 # 用于防抖动
        self.proxySettingsBtn.clicked.connect(self.on_proxySettingsBtn_clicked)

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
                file_path = self.fileLineEdit.text() or "config.json"
                if not self.fileLineEdit.text():
                    self.statusbar.showMessage(f"使用默认配置文件: {file_path}")
              
                video_path = str(self.videoLineEdit.text() or "")
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
        # 获取当前密码
        current_password = self.videoLineEdit.text()
        
        if not current_password:
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
        self.statusbar.showMessage(f"正在请求 GitHub 服务器查询当前最新版本 ...")
        self.config.read(config_file)
        # 获取核心组件版本 - 从配置文件中读取
        if os.path.exists(f"./{filename}"):
            # 从配置文件读取已保存的版本信息
            if 'VERSION' in self.config and 'core_version' in self.config['VERSION']:
                current_version = self.config['VERSION']['core_version'].lstrip("vV")
                saved_publish_date = self.config['VERSION'].get('core_publish_date', '未知')
                print(f"从配置文件读取版本: {current_version} ({saved_publish_date})")
            else:
                current_version = "未知"
                saved_publish_date = "未知"
                print("无法找到已保存的版本信息")
            
            # 获取最新版本和发布日期
            core_info = get_latest_version("cloud-clipboard-go")
            if isinstance(core_info, tuple) and len(core_info) == 2:
                core_latest_version, core_publish_date = core_info
            else:
                core_latest_version, core_publish_date = core_info, "未知"
        else:
            current_version = "未安装"
            saved_publish_date = "未知"
            core_info = get_latest_version("cloud-clipboard-go")
            if isinstance(core_info, tuple) and len(core_info) == 2:
                core_latest_version, core_publish_date = core_info
            else:
                core_latest_version, core_publish_date = core_info, "未知"
        
        if core_latest_version is None:
            self.statusbar.showMessage(f"无法连接到 GitHub 服务器")
            return
        
        # 标准化版本号
        core_latest_clean = core_latest_version.lstrip("vV")
        
        # 判断核心组件是否需要更新
        core_needs_update = current_version == "未知" or current_version != core_latest_clean
        
        # 获取启动器版本
        launcher_current = version.lstrip("vV")
        launcher_info = get_latest_version("cloud-clipboard-go-launcher")
        if isinstance(launcher_info, tuple) and len(launcher_info) == 2:
            launcher_latest_version, launcher_publish_date = launcher_info
        else:
            launcher_latest_version, launcher_publish_date = launcher_info, "未知"
        
        if launcher_latest_version is None:
            self.statusbar.showMessage(f"无法连接到 GitHub 服务器")
            return
        
        # 标准化启动器版本号
        launcher_latest_clean = launcher_latest_version.lstrip("vV")
        
        # 判断启动器是否需要更新
        launcher_needs_update = launcher_current != launcher_latest_clean
        
        # 如果两者都不需要更新
        if not core_needs_update and not launcher_needs_update:
            self.statusbar.showMessage(f"已是最新版：cloud-clipboard-go {core_latest_version} & 启动器 {version}")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("软件更新")
        dialog.setWindowIcon(QIcon(":/icon.png"))
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # 添加核心组件信息
        core_frame = QFrame()
        core_frame.setFrameShape(QFrame.Box)
        core_layout = QVBoxLayout(core_frame)
        
        core_title = QLabel("<b>Cloud Clipboard Go</b>")
        core_layout.addWidget(core_title)
        
        core_info = QLabel(
            f"当前版本：{current_version if current_version != '未安装' else '未安装'} "
            f"({saved_publish_date})\n"
            f"最新版本：{core_latest_clean} ({core_publish_date or '未知'})"
        )
        core_layout.addWidget(core_info)
        
        core_update_btn = QPushButton("更新" if current_version != "未安装" else "下载")
        core_update_btn.setEnabled(core_needs_update)
        core_layout.addWidget(core_update_btn)
        
        layout.addWidget(core_frame)
        
        # 添加分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        
        # 添加启动器信息
        launcher_frame = QFrame()
        launcher_frame.setFrameShape(QFrame.Box)
        launcher_layout = QVBoxLayout(launcher_frame)
        
        launcher_title = QLabel("<b>Cloud Clipboard Go Launcher</b>")
        launcher_layout.addWidget(launcher_title)
        
        launcher_info = QLabel(
            f"当前版本：{launcher_current}\n"
            f"最新版本：{launcher_latest_clean} ({launcher_publish_date or '未知'})"
        )
        launcher_layout.addWidget(launcher_info)
        
        # 替换更新按钮为可点击链接
        launcher_link = QLabel(
            f'<a href="https://github.com/jonnyan404/cloud-clipboard-go-launcher/releases/latest">点击此处下载最新版启动器</a>'
        )
        launcher_link.setOpenExternalLinks(True)  # 允许打开外部链接
        launcher_layout.addWidget(launcher_link)
        
        layout.addWidget(launcher_frame)
        
        # 添加关闭按钮
        btn_layout = QHBoxLayout()
        close_btn = QPushButton("关闭")
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
        
        dialog.setLayout(layout)
        
        # 连接信号
        def update_core():
            dialog.accept()
            worker = ThreadDownloader(self.statusbar, self.updateBtn, self)
            worker.start()
        
        core_update_btn.clicked.connect(update_core)
        def close_dialog():
            dialog.reject()
            self.statusbar.showMessage("用户取消更新")
            
        close_btn.clicked.connect(close_dialog)
        
        # 显示对话框
        dialog.exec_()

    @pyqtSlot()
    def on_openWebBtn_clicked(self):
        """打开网页版界面"""
        import webbrowser
        
        host = self.hostComboBox.currentText()
        port = self.portSpinBox.text()
        
        # 如果主机是localhost或0.0.0.0，使用127.0.0.1代替
        if host in ["localhost", "0.0.0.0"]:
            host = "127.0.0.1"
            
        url = f"http://{host}:{port}"
        self.statusbar.showMessage(f"正在打开 {url}")
        
        # 打开默认浏览器
        webbrowser.open(url)

    @pyqtSlot()
    def on_proxySettingsBtn_clicked(self):
        """打开代理设置对话框，支持传统HTTP/SOCKS代理和认证"""
        
        current_time = time.time()
        # 防抖动检查：如果距离上次对话框关闭时间非常短（例如少于100毫秒），则忽略此次点击
        if hasattr(self, '_last_proxy_dialog_close_time') and \
           current_time - self._last_proxy_dialog_close_time < 0.1: # 100毫秒阈值
            print("代理设置按钮点击过快（可能为自动重触发），已忽略。")
            return

        if self.proxy_dialog_active:
            print("代理设置对话框已经打开，忽略请求")
            return
        
        print("代理设置按钮被点击") 
        self.proxy_dialog_active = True # 在显示对话框前立即设置

        # 创建对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("代理设置")
        dialog.setWindowIcon(QIcon(":/icon.png"))
        dialog.setMinimumWidth(450)
        dialog.setAttribute(Qt.WA_DeleteOnClose, True) # 确保对话框关闭时删除
        layout = QVBoxLayout()
        
        # ====== 选项卡和按钮的创建逻辑 (从您的代码中复制并确保变量名正确) ======
        # 创建选项卡
        tab_widget = QTabWidget()
        
        # ====== 第一个选项卡：GH加速代理 ======
        url_proxy_tab = QWidget()
        url_layout = QVBoxLayout()
        url_info_label = QLabel("设置GitHub下载加速代理URL，加速下载云剪贴板核心组件")
        url_layout.addWidget(url_info_label)
        url_proxy_checkbox = QCheckBox("启用URL加速代理")
        url_proxy_checkbox.setChecked(self.config['PROXY'].get('type', '').lower() == 'url' and self.config['PROXY'].get('enabled', '').lower() == 'true')
        url_layout.addWidget(url_proxy_checkbox)
        url_input_layout = QHBoxLayout()
        url_label = QLabel("代理URL:")
        url_edit = QLineEdit(self.config['PROXY'].get('url', 'https://gh-proxy.com'))
        url_edit.setPlaceholderText("https://gh-proxy.com")
        url_input_layout.addWidget(url_label)
        url_input_layout.addWidget(url_edit)
        url_layout.addLayout(url_input_layout)
        url_example = QLabel("示例: https://gh-proxy.com/, https://ghproxy.com/ 等")
        url_layout.addWidget(url_example)
        url_proxy_tab.setLayout(url_layout)
        
        # ====== 第二个选项卡：HTTP/SOCKS代理 ======
        traditional_proxy_tab = QWidget()
        traditional_layout = QVBoxLayout()
        traditional_info_label = QLabel("设置传统HTTP/SOCKS代理，通过代理服务器连接GitHub")
        traditional_layout.addWidget(traditional_info_label)
        traditional_proxy_checkbox = QCheckBox("启用HTTP/SOCKS代理")
        traditional_proxy_checkbox.setChecked(self.config['PROXY'].get('type', '').lower() == 'traditional' and self.config['PROXY'].get('enabled', '').lower() == 'true')
        traditional_layout.addWidget(traditional_proxy_checkbox)
        proxy_type_layout = QHBoxLayout()
        proxy_type_label = QLabel("代理类型:")
        proxy_type_combo = QComboBox()
        proxy_type_combo.addItems(["HTTP", "SOCKS4", "SOCKS5"])
        current_proxy_type = self.config['PROXY'].get('proxy_type', 'HTTP')
        proxy_type_index = proxy_type_combo.findText(current_proxy_type)
        if proxy_type_index >= 0:
            proxy_type_combo.setCurrentIndex(proxy_type_index)
        proxy_type_layout.addWidget(proxy_type_label)
        proxy_type_layout.addWidget(proxy_type_combo)
        traditional_layout.addLayout(proxy_type_layout)
        proxy_server_layout = QHBoxLayout()
        proxy_server_label = QLabel("服务器地址:")
        proxy_server_edit = QLineEdit(self.config['PROXY'].get('proxy_server', '127.0.0.1'))
        proxy_server_edit.setPlaceholderText("example.com 或 127.0.0.1")
        proxy_server_layout.addWidget(proxy_server_label)
        proxy_server_layout.addWidget(proxy_server_edit)
        traditional_layout.addLayout(proxy_server_layout)
        proxy_port_layout = QHBoxLayout()
        proxy_port_label = QLabel("端口号:")
        proxy_port_edit = QLineEdit(self.config['PROXY'].get('proxy_port', '7897'))
        proxy_port_edit.setPlaceholderText("7897")
        proxy_port_layout.addWidget(proxy_port_label)
        proxy_port_layout.addWidget(proxy_port_edit)
        traditional_layout.addLayout(proxy_port_layout)
        auth_group = QGroupBox("认证信息")
        auth_group.setCheckable(True)
        auth_group.setChecked(self.config['PROXY'].get('auth_enabled', '').lower() == 'true')
        auth_layout = QVBoxLayout()
        username_layout = QHBoxLayout()
        username_label = QLabel("用户名:")
        username_edit = QLineEdit(self.config['PROXY'].get('proxy_username', ''))
        username_layout.addWidget(username_label)
        username_layout.addWidget(username_edit)
        auth_layout.addLayout(username_layout)
        password_layout = QHBoxLayout()
        password_label = QLabel("密码:")
        password_edit = QLineEdit(self.config['PROXY'].get('proxy_password', ''))
        password_edit.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(password_edit)
        auth_layout.addLayout(password_layout)
        auth_group.setLayout(auth_layout)
        traditional_layout.addWidget(auth_group)
        traditional_proxy_tab.setLayout(traditional_layout)
        
        tab_widget.addTab(url_proxy_tab, "加速URL")
        tab_widget.addTab(traditional_proxy_tab, "HTTP/SOCKS代理")
        layout.addWidget(tab_widget)
        
        btn_layout = QHBoxLayout()
        reset_btn = QPushButton("恢复默认")
        save_btn = QPushButton("保存")
        cancel_btn = QPushButton("取消")
        btn_layout.addWidget(reset_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        dialog.setLayout(layout)

        # 设置选项卡之间的互斥关系
        def on_url_checkbox_changed(state):
            if state:
                traditional_proxy_checkbox.setChecked(False)
                
        def on_traditional_checkbox_changed(state):
            if state:
                url_proxy_checkbox.setChecked(False)
        
        url_proxy_checkbox.stateChanged.connect(on_url_checkbox_changed)
        traditional_proxy_checkbox.stateChanged.connect(on_traditional_checkbox_changed)
        
        # 统一的清理函数，在对话框 finished 时调用
        def actual_cleanup_and_log(result_code): # QDialog.finished 传递结果码
            self.proxy_dialog_active = False
            self._last_proxy_dialog_close_time = time.time() # 更新关闭时间戳
            print(f"代理设置对话框已关闭 (结果: {result_code})")

        # 连接信号
        def reset_defaults_action(): # 重命名以避免与外部函数冲突
            url_proxy_checkbox.setChecked(True)
            traditional_proxy_checkbox.setChecked(False)
            url_edit.setText("https://gh-proxy.com")
            proxy_type_combo.setCurrentText("HTTP")
            proxy_server_edit.setText("")
            proxy_port_edit.setText("")
            auth_group.setChecked(False)
            username_edit.setText("")
            password_edit.setText("")
            tab_widget.setCurrentIndex(0)
        
        def save_settings_action(): # 重命名
            # 保存代理设置
            if url_proxy_checkbox.isChecked():
                self.config['PROXY']['enabled'] = 'True'
                self.config['PROXY']['type'] = 'url'
                self.config['PROXY']['url'] = url_edit.text()
                self.statusbar.showMessage(f"已启用URL加速代理: {url_edit.text()}")
            elif traditional_proxy_checkbox.isChecked():
                self.config['PROXY']['enabled'] = 'True'
                self.config['PROXY']['type'] = 'traditional'
                # ... (省略了其他配置项的保存，与您原代码一致) ...
                self.config['PROXY']['proxy_type'] = proxy_type_combo.currentText()
                self.config['PROXY']['proxy_server'] = proxy_server_edit.text()
                self.config['PROXY']['proxy_port'] = proxy_port_edit.text()
                self.config['PROXY']['auth_enabled'] = str(auth_group.isChecked())
                self.config['PROXY']['proxy_username'] = username_edit.text() if auth_group.isChecked() else ''
                self.config['PROXY']['proxy_password'] = password_edit.text() if auth_group.isChecked() else ''
                proxy_desc = f"{proxy_type_combo.currentText()}://{proxy_server_edit.text()}:{proxy_port_edit.text()}"
                if auth_group.isChecked():
                    proxy_desc += " (已设置认证)"
                self.statusbar.showMessage(f"已启用HTTP/SOCKS代理: {proxy_desc}")
            else:
                self.config['PROXY']['enabled'] = 'False'
                self.statusbar.showMessage("代理已禁用")
            
            with open(config_file, 'w') as f:
                self.config.write(f)
            
            dialog.accept() # 这将关闭对话框并触发 finished 信号

        def cancel_settings_action(): # 重命名
            dialog.reject() # 这将关闭对话框并触发 finished 信号

        reset_btn.clicked.connect(reset_defaults_action)
        save_btn.clicked.connect(save_settings_action)
        cancel_btn.clicked.connect(cancel_settings_action)
        
        # 关键：只将 dialog.finished 连接到清理函数
        dialog.finished.connect(actual_cleanup_and_log)
        
        # 显示对话框
        dialog.exec_()
        # 当 exec_() 返回后, actual_cleanup_and_log 会被调用过一次,
        # self.proxy_dialog_active 会是 False, _last_proxy_dialog_close_time 会被更新。

class ThreadDownloader(Thread):
    def __init__(self, statusbar, updateBtn, main_window=None):
        super().__init__()
        self.statusbar = statusbar
        self.updateBtn = updateBtn
        self.main_window = main_window  # 保存 MainWindow 实例引用

    def run(self):
        self.updateBtn.setEnabled(False)
        self.statusbar.showMessage("正在从 GitHub 上获取最新版 ...")
        
        # 读取代理配置
        config = configparser.ConfigParser()
        config.read(config_file)
        
        proxy_enabled = config['PROXY'].get('enabled', '').lower() == 'true'
        proxy_type = config['PROXY'].get('type', '')
        
        # 定义代理设置
        proxies = None
        
        # 原始下载URL
        github_url = f"https://github.com/jonnyan404/cloud-clipboard-go/releases/latest/download/{download_filename}"
        download_url = github_url
        
        if proxy_enabled:
            if proxy_type.lower() == 'url':
                # URL加速代理
                proxy_url = config['PROXY'].get('url', 'https://gh-proxy.com')
                if not proxy_url.endswith('/'):
                    proxy_url = proxy_url + '/'
                download_url = f"{proxy_url}https://github.com/jonnyan404/cloud-clipboard-go/releases/latest/download/{download_filename}"
                self.statusbar.showMessage(f"使用URL加速代理: {download_url}")
            elif proxy_type.lower() == 'traditional':
                # 传统HTTP/SOCKS代理
                proxy_protocol = config['PROXY'].get('proxy_type', 'HTTP').lower()
                proxy_server = config['PROXY'].get('proxy_server', '127.0.0.1')
                proxy_port = config['PROXY'].get('proxy_port', '7897')
                auth_enabled = config['PROXY'].get('auth_enabled', '').lower() == 'true'
                
                # 构建代理URL
                proxy_url = f"{proxy_protocol.lower()}://"
                
                # 添加认证信息
                if auth_enabled:
                    username = config['PROXY'].get('proxy_username', '')
                    password = config['PROXY'].get('proxy_password', '')
                    if username:
                        if password:
                            proxy_url += f"{username}:{password}@"
                        else:
                            proxy_url += f"{username}@"
                
                # 添加服务器和端口
                proxy_url += f"{proxy_server}:{proxy_port}"
                
                # 根据代理协议设置不同的代理
                proxies = {
                    'http': proxy_url,
                    'https': proxy_url
                }
                
                self.statusbar.showMessage(f"使用{proxy_protocol}代理: {proxy_server}:{proxy_port}")
        else:
            self.statusbar.showMessage(f"未使用代理，直接下载: {download_url}")
        
        try:
            # 先获取最新版本信息
            core_info = get_latest_version("cloud-clipboard-go")
            if isinstance(core_info, tuple) and len(core_info) == 2:
                latest_version, publish_date = core_info
            else:
                latest_version, publish_date = None, None
                
            # 下载文件
            if proxies:
                res = requests.get(download_url, proxies=proxies)
            else:
                res = requests.get(download_url)
            
            if res.status_code != 200:
                self.statusbar.showMessage(f"下载失败：HTTP {res.status_code} - {res.text}")
                self.updateBtn.setEnabled(True)
                return
                
            # 保存压缩包
            temp_file = f"./temp_{download_filename}"
            with open(temp_file, "wb") as f:
                f.write(res.content)
            
            # 解压逻辑保持不变
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
                
            # 保存版本信息到配置文件
            if latest_version and publish_date:
                # 假设self.main_window是MainWindow的实例
                
                config = ConfigParser()
                # 尝试读取现有配置
                config.read(config_file)
                
                # 确保有VERSION部分
                if 'VERSION' not in config:
                    config['VERSION'] = {}
                    
                # 保存版本信息
                config['VERSION']['core_version'] = latest_version
                config['VERSION']['core_publish_date'] = publish_date
                
                # 写入配置文件
                with open(config_file, 'w') as f:
                    config.write(f)
                    
            self.statusbar.showMessage(f"下载并解压完成")
        except Exception as e:
            self.statusbar.showMessage(f"下载或解压过程出错: {str(e)}")
        finally:
            self.updateBtn.setEnabled(True)
            self.updateBtn.setText("检查更新")


if __name__ == "__main__":
    app = QApplication(sys.argv)
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
    Dialog = MainWindow()
    Dialog.show()
    sys.exit(app.exec_())

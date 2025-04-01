import os
import socket
import sys
import subprocess
import platform

import requests


def get_ips():
    """获取本机局域网IP地址，增强对py2app环境的兼容性"""
    ips = []
    
    # 方法1: 标准方式
    try:
        hostname = socket.gethostname()
        ip_list = socket.gethostbyname_ex(hostname)[2]
        for ip in ip_list:
            if not ip.startswith('127.'):  # 过滤本地环回地址
                ips.append(ip)
    except Exception as e:
        print(f"方法1获取IP失败: {str(e)}")
    
    # 方法2: 创建UDP连接方式
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.1)  # 设置超时，防止阻塞
        try:
            # 连接到外部地址，但不发送数据
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            if ip and ip not in ips and not ip.startswith('127.'):
                ips.append(ip)
        finally:
            s.close()
    except Exception as e:
        print(f"方法2获取IP失败: {str(e)}")
    
    # 方法3: 使用系统命令
    try:
        if platform.system() == "Darwin":  # macOS
            cmd = "ifconfig | grep 'inet ' | grep -v 127.0.0.1"
            result = subprocess.check_output(cmd, shell=True, universal_newlines=True)
            for line in result.split('\n'):
                if line.strip():
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        ip = parts[1]
                        if ip and ip not in ips and not ip.startswith('127.'):
                            ips.append(ip)
        elif platform.system() == "Linux":
            cmd = "ip addr | grep 'inet ' | grep -v 127.0.0.1"
            result = subprocess.check_output(cmd, shell=True, universal_newlines=True)
            for line in result.split('\n'):
                if line.strip():
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        ip = parts[1].split('/')[0]
                        if ip and ip not in ips and not ip.startswith('127.'):
                            ips.append(ip)
        elif platform.system() == "Windows":
            cmd = "ipconfig"
            result = subprocess.check_output(cmd, shell=True, universal_newlines=True)
            for line in result.split('\n'):
                if "IPv4" in line and ":" in line:
                    ip = line.split(':')[-1].strip()
                    if ip and ip not in ips and not ip.startswith('127.'):
                        ips.append(ip)
    except Exception as e:
        print(f"方法3获取IP失败: {str(e)}")
    
    # 确保返回列表非空，至少包含localhost
    if not ips:
        ips.append("localhost")
        ips.append("0.0.0.0")  # 添加通配地址
    
    print(f"获取到的局域网IP: {ips}")
    return ips


def system_related_secret():
    return socket.gethostname() + os.getcwd() + str(get_ips()) + str(os.path.getctime(sys.argv[0]))


def get_latest_version(repository, username="jonnyan404"):
    try:
        data = requests.get(f"https://api.github.com/repos/{username}/{repository}/releases/latest").json()
    except:
        return None
    latest_version = data["tag_name"]
    return latest_version
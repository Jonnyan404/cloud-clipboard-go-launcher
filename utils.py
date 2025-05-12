import os
import socket
import sys
import subprocess
import platform
import configparser

import requests


def get_ips():
    # print("get_ips() 被调用")
    # import traceback
    # traceback.print_stack()
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
    """获取最新版本信息，返回(版本号, 发布日期)元组，支持多种代理"""
    try:
        # 检查是否有代理配置
        config = configparser.ConfigParser()
        config_file = "cloud-clipboard-go-launcher.ini"
        config.read(config_file)
        
        proxies = None
        proxy_enabled = config['PROXY'].get('enabled', '').lower() == 'true'
        proxy_type = config['PROXY'].get('type', '')
        
        # 构建API URL
        api_url = f"https://api.github.com/repos/{username}/{repository}/releases/latest"
        
        if proxy_enabled:
            if proxy_type.lower() == 'url':
                # URL加速代理
                proxy_url = config['PROXY'].get('url', 'https://gh-proxy.com')
                if not proxy_url.endswith('/'):
                    proxy_url += '/'
                api_url = f"{proxy_url}{api_url}"
                print(f"使用URL加速代理获取版本信息: {api_url}")
            elif proxy_type.lower() == 'traditional':
                # 传统HTTP/SOCKS代理
                proxy_protocol = config['PROXY'].get('proxy_type', 'HTTP').lower()
                proxy_server = config['PROXY'].get('proxy_server', '')
                proxy_port = config['PROXY'].get('proxy_port', '1080')
                auth_enabled = config['PROXY'].get('auth_enabled', '').lower() == 'true'
                
                # 构建代理URL
                proxy_url = f"{proxy_protocol.lower()}://"
                
                # 添加认证信息
                if auth_enabled:
                    username_proxy = config['PROXY'].get('proxy_username', '')
                    password = config['PROXY'].get('proxy_password', '')
                    if username_proxy:
                        if password:
                            proxy_url += f"{username_proxy}:{password}@"
                        else:
                            proxy_url += f"{username_proxy}@"
                
                # 添加服务器和端口
                proxy_url += f"{proxy_server}:{proxy_port}"
                
                # 设置代理
                proxies = {
                    'http': proxy_url,
                    'https': proxy_url
                }
                print(f"使用{proxy_protocol}代理获取版本信息: {proxy_server}:{proxy_port}")
        
        # 使用代理发送请求
        if proxies:
            data = requests.get(api_url, proxies=proxies).json()
        else:
            data = requests.get(api_url).json()
            
        if "tag_name" not in data:
            return None, None
        latest_version = data["tag_name"]
        published_at = data.get("published_at", "").split("T")[0]  # 只保留日期部分
        return latest_version, published_at
    except Exception as e:
        print(f"获取版本信息失败: {e}")
        return None, None
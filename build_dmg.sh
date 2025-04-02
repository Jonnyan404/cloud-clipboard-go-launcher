#!/bin/bash
#python3.9.12
set -e  # 遇到错误立即停止

echo "清理旧构建..."
rm -rf build/ dist/* *.dmg staging/ venv/

echo "创建虚拟环境..."
python -m venv venv
source venv/bin/activate

echo "安装依赖..."
pip install --upgrade pip
pip install wheel
pip install -r requirements.txt
pip install py2app

echo "生成UI文件..."
pyuic5 -o ui.py main.ui
pyrcc5 -o resource_rc.py resource.qrc

echo "打包应用..."
python setup.py py2app --no-strip --no-chdir --arch=arm64

echo "检查生成的应用..."
find ./dist -name "*.app"

APP_PATH=$(find ./dist -name "*.app" | head -1)
if [ -z "$APP_PATH" ]; then
  echo "错误：没有找到应用程序文件"
  exit 1
fi

APP_NAME=$(basename "$APP_PATH")
echo "找到应用: $APP_NAME"

echo "创建DMG安装包..."
mkdir -p staging
cp -r "$APP_PATH" staging/

# 简化create-dmg命令
create-dmg \
  --volname "cloud-clipboard-go" \
  --volicon "icon.png" \
  --window-size 600 400 \
  --app-drop-link 425 190 \
  "cloud-clipboard-go-安装包.dmg" \
  staging/ || echo "警告：DMG创建过程遇到非致命错误"

echo "清理临时目录..."
rm -rf staging
deactivate  # 退出虚拟环境

echo "打包完成：cloud-clipboard-go-安装包.dmg"
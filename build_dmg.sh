#!/bin/bash
# cloud-clipboard-go 通用构建脚本
# 在 Apple Silicon (arm64, 开启 Rosetta) 上会自动构建并合并出 universal2 安装包(同时支持 amd64 + arm64)
# 在仅单架构的机器(如普通 Intel 或未装 Rosetta 的机器)上，自动回退为只构建本机架构的单架构安装包
set -e  # 遇到错误立即停止

# 保证构建产物最低支持 macOS 12.x（用户机器为 macOS 12）
export MACOSX_DEPLOYMENT_TARGET=12.0

NATIVE_ARCH="$(uname -m)"
echo "本机原生架构: $NATIVE_ARCH"

# ---------------------------------------------------------------------------
# 0. 判断是否支持双架构(universal)构建
#    需要 Apple Silicon + Rosetta，能同时执行 arm64 与 x86_64 两种 Python 切片
# ---------------------------------------------------------------------------
can_universal=0
if [ "$NATIVE_ARCH" = "arm64" ]; then
  if arch -arm64 true 2>/dev/null && arch -x86_64 true 2>/dev/null; then
    can_universal=1
  fi
fi

if [ "$can_universal" = "1" ]; then
  echo "检测到支持双架构构建 (Apple Silicon + Rosetta)，将构建 universal2 安装包"
else
  echo "本机不支持双架构构建，将回退为只构建本机 ($NATIVE_ARCH) 的单架构安装包"
fi

echo "清理旧构建..."
rm -rf build/ dist/* ./*.dmg staging/
rm -rf venv/ venv-arm64/ venv-x86_64/

echo "生成UI文件..."
pyside6-uic main.ui -o ui.py
pyside6-rcc resource.qrc -o resource_rc.py

# ---------------------------------------------------------------------------
# 通用：在指定的 Python 解释器下创建 venv、装依赖、并跑 PyInstaller
#   用法: build_one <interpreter> <output_dir> <arch> <label>
# ---------------------------------------------------------------------------
build_one() {
  local interp="$1"
  local outdir="$2"
  local arch="$3"
  local label="$4"

  echo "========== [$label] 创建虚拟环境 ($interp) =========="
  # interp 可能带参数(如 "arch -x86_64 /path/python3")，用 bash -c 执行
  bash -c "$interp -m venv \"$outdir\""
  # shellcheck disable=SC1090
  source "$outdir/bin/activate"

  echo "[$label] 安装依赖..."
  pip install --upgrade pip wheel
  pip install -r requirements.txt

  echo "[$label] 打包应用 (PyInstaller, arch=$arch)..."
  python -m PyInstaller --windowed --noconfirm --clean \
    --name cloud-clipboard-go-launcher \
    --icon icon.png \
    --add-data "icon.png:." \
    main.py

  echo "[$label] 校验主可执行文件架构..."
  file "dist/cloud-clipboard-go-launcher.app/Contents/MacOS/cloud-clipboard-go-launcher"

  deactivate
}

# ---------------------------------------------------------------------------
# 合并两个 app 里的所有 Mach-O 二进制为 universal
#   用法: merge_universal <base_app> <other_app> <out_app>
# ---------------------------------------------------------------------------
merge_universal() {
  local BASE="$1"
  local OTHER="$2"
  local OUT="$3"

  echo "========== 使用 lipo 合并为 universal2 =========="
  cp -R "$BASE" "$OUT"
  while IFS= read -r f; do
    local rel="${f#"${OUT}"/}"
    local other="${OTHER}/${rel}"
    if [ -f "$other" ] && ! [ -L "$f" ] && file -b "$f" | grep -q "Mach-O"; then
      if file -b "$f" | grep -q "universal"; then
        echo "已是 universal: $rel"
      else
        lipo -create "$f" "$other" -output "$f"
        echo "合并: $rel"
      fi
    else
      echo "跳过: $rel"
    fi
  done < <(find "$OUT" -type f)

  echo "=== 校验合并后的主可执行文件 ==="
  lipo -info "$OUT/Contents/MacOS/cloud-clipboard-go-launcher"
}

# ---------------------------------------------------------------------------
# 打包 DMG
#   用法: make_dmg <app_path> <dmg_name>
# ---------------------------------------------------------------------------
make_dmg() {
  local app="$1"
  local dmg="$2"

  echo "创建DMG安装包 ($dmg)..."
  mkdir -p staging
  # 以固定名称 cloud-clipboard-go.app 打包（与 homebrew cask 的 app 名称一致）
  cp -r "$app" staging/cloud-clipboard-go.app

  create-dmg \
    --volname "cloud-clipboard-go" \
    --volicon "icon.png" \
    --window-size 600 400 \
    --app-drop-link 425 190 \
    "$dmg" \
    staging/ || echo "警告：DMG创建过程遇到非致命错误"

  rm -rf staging
}

# ---------------------------------------------------------------------------
# A) 双架构构建 (Apple Silicon + Rosetta)
# ---------------------------------------------------------------------------
if [ "$can_universal" = "1" ]; then
  # arm64：原生解释器
  ARM_INTERP="$(command -v python3)"
  if [ -z "$ARM_INTERP" ]; then ARM_INTERP=python3; fi
  echo "arm64 解释器: $ARM_INTERP"

  # x86_64：通过 Rosetta 运行同一个解释器（或系统 python）
  X86_INTERP="arch -x86_64 $ARM_INTERP"
  echo "x86_64 解释器(经 Rosetta): $X86_INTERP"

  build_one "$ARM_INTERP" "$PWD/venv-arm64" "arm64" "arm64/Apple-Silicon"
  mv dist/cloud-clipboard-go-launcher.app dist/cloud-clipboard-go-launcher-arm64.app

  build_one "arch -x86_64 $ARM_INTERP" "$PWD/venv-x86_64" "x86_64" "x86_64/Intel"
  mv dist/cloud-clipboard-go-launcher.app dist/cloud-clipboard-go-launcher-x86_64.app

  # 合并
  merge_universal "$PWD/dist/cloud-clipboard-go-launcher-arm64.app" \
                  "$PWD/dist/cloud-clipboard-go-launcher-x86_64.app" \
                  "$PWD/dist/cloud-clipboard-go-launcher.app"
  DMG_NAME="cloud-clipboard-go-安装包-macOS-universal.dmg"

  echo "清理各架构临时 app..."
  rm -rf "$PWD/dist/cloud-clipboard-go-launcher-arm64.app" "$PWD/dist/cloud-clipboard-go-launcher-x86_64.app"

# ---------------------------------------------------------------------------
# B) 单架构回退 (Intel 或 Apple Silicon)
# ---------------------------------------------------------------------------
else
  echo "创建虚拟环境..."
  python -m venv venv
  source venv/bin/activate

  echo "安装依赖..."
  pip install --upgrade pip
  pip install wheel
  pip install -r requirements.txt

  echo "打包应用 (PyInstaller, arch=$NATIVE_ARCH)..."
  python -m PyInstaller --windowed --noconfirm --clean \
    --name cloud-clipboard-go-launcher \
    --icon icon.png \
    --add-data "icon.png:." \
    main.py

  echo "校验主可执行文件架构..."
  file "dist/cloud-clipboard-go-launcher.app/Contents/MacOS/cloud-clipboard-go-launcher"

  deactivate

  DMG_NAME="cloud-clipboard-go-安装包-macOS-$NATIVE_ARCH.dmg"
fi

# ---------------------------------------------------------------------------
# 打包最终 DMG
# ---------------------------------------------------------------------------
APP_PATH=$(find "$PWD/dist" -name "*.app" | head -1)
if [ -z "$APP_PATH" ]; then
  echo "错误：没有找到应用程序文件"
  exit 1
fi
echo "找到应用: $(basename "$APP_PATH")"

make_dmg "$APP_PATH" "$DMG_NAME"

echo "打包完成：$DMG_NAME"

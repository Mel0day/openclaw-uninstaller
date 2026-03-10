#!/bin/bash
# 构建 OpenClaw卸载工具.app
set -e

APP="OpenClaw卸载工具.app"
DIST="dist/$APP"
RESOURCES="$DIST/Contents/Resources"

echo "→ 清理旧构建..."
rm -rf dist && mkdir -p dist

echo "→ 编译 AppleScript 启动器..."
osacompile -o "$DIST" launcher.applescript

echo "→ 复制资源文件..."
cp server.py "$RESOURCES/"
cp index.html "$RESOURCES/"

echo "→ 生成图标..."
python3 make_icon.py "$RESOURCES"

echo "→ 清除隔离属性..."
xattr -cr "$DIST"

echo "✓ 构建完成 → $DIST"
echo "  可将 dist/$APP 拖到应用程序文件夹或桌面使用"

@echo off
chcp 65001
REM 打包入口文件是 m2w/main.py
REM --onefile 生成单 exe
REM --disable-console 如果你不想要黑窗口，可以加这个参数

python -m nuitka  --onefile  --enable-plugin=tk-inter  --follow-imports  --output-dir=build --lto=yes  myblog.py

echo 打包完成! exe 在 build 目录下。
pause

#!/usr/bin/env bash
# Unix/Mac: 在项目根目录运行 ./venv_setup.sh
python3 -m venv .venv
if [ -d ".venv" ]; then
  echo "虚拟环境已创建：.venv"
  echo "运行：source .venv/bin/activate 来激活虚拟环境"
else
  echo "虚拟环境创建失败，请检查 Python 可用性。"
  exit 1
fi
python -m pip install --upgrade pip
pip install -r requirements.txt

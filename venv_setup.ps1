<#
PowerShell: 在 Windows 上创建并激活虚拟环境，然后安装依赖
Usage: 在项目根目录运行 `.\venv_setup.ps1`（可能需要以管理员/合适权限运行）
#>
python -m venv .venv
if (Test-Path -Path .venv\Scripts\Activate.ps1) {
    Write-Host "虚拟环境已创建：.venv"
    Write-Host "请执行：.\.venv\Scripts\Activate.ps1 来激活虚拟环境，或在PowerShell中运行：`Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` 后再激活。"
} else {
    Write-Host "虚拟环境创建失败，请检查 Python 可用性。"
    exit 1
}
python -m pip install --upgrade pip
pip install -r requirements.txt

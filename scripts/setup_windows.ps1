param(
 [string]$ToolsRoot=(Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'DocRestoreTools'),
 [string]$PythonExe,
 [ValidateSet('modelscope','huggingface')][string]$ModelSource='modelscope',
 [switch]$SkipModels,
 [switch]$CheckOnly
)
$ErrorActionPreference='Stop'
if ([Environment]::OSVersion.Platform -ne 'Win32NT' -or -not [Environment]::Is64BitOperatingSystem) { throw 'This setup supports 64-bit Windows.' }
$root=[System.IO.Path]::GetFullPath($ToolsRoot)
if ($root -match '[^\x20-\x7E]') { throw 'Choose a writable ASCII-only -ToolsRoot to avoid native VLM Unicode path errors.' }
if ($root -eq [System.IO.Path]::GetPathRoot($root)) { throw 'Use a dedicated ToolsRoot directory, not a drive root.' }
$venv=Join-Path $root 'venv'
$taskPython=Join-Path $venv 'Scripts\python.exe'
$taskMineru=Join-Path $venv 'Scripts\mineru-kit.exe'
if ($CheckOnly) {
 @{tools_root=$root;python_exists=(Test-Path -LiteralPath $taskPython);mineru_exists=(Test-Path -LiteralPath $taskMineru);activation_exists=(Test-Path -LiteralPath (Join-Path $root 'Activate-DocumentTools.ps1'))} | ConvertTo-Json
 return
}
if (-not (Test-Path -LiteralPath $taskPython)) {
 if (-not $PythonExe) {
  $launcher=Get-Command py -ErrorAction SilentlyContinue
  if ($launcher) {
   $candidate=$null
   try { $candidate=& $launcher.Source -3.12 -c 'import sys; print(sys.executable)' 2>$null } catch { $candidate=$null }
   if ($LASTEXITCODE -eq 0 -and $candidate -and (Test-Path -LiteralPath ([string]$candidate))) { $PythonExe=[string]$candidate }
  }
 }
 if (-not $PythonExe) {
  $pythonCommand=Get-Command python -ErrorAction SilentlyContinue
  if ($pythonCommand -and $pythonCommand.Source -notmatch 'WindowsApps') {
   $version=$null
   try { $version=& $pythonCommand.Source -c "import sys; print(str(sys.version_info.major)+'.'+str(sys.version_info.minor))" 2>$null } catch { $version=$null }
   if ($LASTEXITCODE -eq 0 -and $version -eq '3.12') { $PythonExe=$pythonCommand.Source }
  }
 }
 if (-not $PythonExe) {
  $winget=Get-Command winget -ErrorAction SilentlyContinue
  if (-not $winget) { throw 'Install Python 3.12 x64 from python.org, then rerun with -PythonExe pointing to python.exe.' }
  & $winget.Source install --id Python.Python.3.12 --exact --source winget --scope user --silent --accept-source-agreements --accept-package-agreements
  if ($LASTEXITCODE -ne 0) { throw 'Python installation failed. Install from python.org and pass -PythonExe.' }
  $installed=Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'Programs\Python\Python312\python.exe'
  if (Test-Path -LiteralPath $installed) { $PythonExe=$installed }
  else {
   $launcher=Get-Command py -ErrorAction SilentlyContinue
   if ($launcher) { $candidate=& $launcher.Source -3.12 -c 'import sys; print(sys.executable)' 2>$null; if ($LASTEXITCODE -eq 0) { $PythonExe=[string]$candidate } }
  }
  if (-not $PythonExe) { throw 'Reopen the shell after Python installation or pass -PythonExe.' }
 }
 $null=New-Item -ItemType Directory -Path $root -Force
 & $PythonExe -c 'import sys; assert sys.version_info[:2] == (3,12) and sys.maxsize > 2**32'
 if ($LASTEXITCODE -ne 0) { throw 'Python 3.12 x64 is required.' }
 & $PythonExe -m venv $venv
 if ($LASTEXITCODE -ne 0) { throw 'Virtual environment creation failed.' }
}
& $taskPython -c 'import sys; assert sys.version_info[:2] == (3,12) and sys.maxsize > 2**32'
if ($LASTEXITCODE -ne 0) { throw 'The existing dedicated environment is not Python 3.12 x64. Choose a new ToolsRoot.' }
& $taskPython -m pip install --disable-pip-version-check --index-url https://pypi.org/simple -r (Join-Path $PSScriptRoot 'requirements.txt') 'mineru==4.0.12'
if ($LASTEXITCODE -ne 0) { throw 'Package installation failed. Inspect pip output; do not bypass certificate verification.' }
$data=Join-Path $root 'data'
$models=Join-Path $root 'models'
$env:MINERU_HOME=$data
$env:MINERU_MODEL_BASE_DIR=$models
$env:MINERU_MODEL_SMALL_BACKEND='onnx'
$env:MINERU_MODEL_VLM_ENGINE='llama-cpp'
$env:MINERU_MODEL_SOURCE=$ModelSource
$modelReady=$false
if (-not $SkipModels) {
 & $taskMineru models download --tier standard --small-backend onnx --vlm-engine llama-cpp --source $ModelSource
 if ($LASTEXITCODE -ne 0) { throw 'Model download failed. Keep cache and retry; installation is incomplete.' }
 & $taskMineru models verify --tier standard --small-backend onnx --vlm-engine llama-cpp
 if ($LASTEXITCODE -ne 0) { throw 'Model verification failed.' }
 $modelReady=$true
}
$runtime=@{python=$taskPython;mineru=$taskMineru;data=$data;models=$models;mineru_version='4.0.12';models_verified=$modelReady}
$runtime | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $root 'runtime.json') -Encoding UTF8
$activate=@'
$taskRuntime=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'runtime.json') -Raw | ConvertFrom-Json
$env:DOC_RESTORE_PYTHON=$taskRuntime.python
$env:DOC_RESTORE_MINERU=$taskRuntime.mineru
$env:MINERU_HOME=$taskRuntime.data
$env:MINERU_MODEL_BASE_DIR=$taskRuntime.models
$env:MINERU_MODEL_SMALL_BACKEND='onnx'
$env:MINERU_MODEL_VLM_ENGINE='llama-cpp'
$env:MINERU_MODEL_SOURCE='local'
'@
$activate | Set-Content -LiteralPath (Join-Path $root 'Activate-DocumentTools.ps1') -Encoding UTF8
& $taskPython (Join-Path $PSScriptRoot 'doctor.py') --mineru-exe $taskMineru
if ($LASTEXITCODE -ne 0) { throw 'Helper package verification failed.' }
Write-Output ('Ready for activation: '+(Join-Path $root 'Activate-DocumentTools.ps1'))
if (-not $modelReady) { Write-Warning 'Models skipped; OCR is not ready until downloaded and verified.' }
Write-Output 'Install/activate licensed Microsoft Word desktop separately if COM rendering is unavailable.'

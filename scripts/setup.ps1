# First-run setup for pmu-beautify (Windows 10/11). Safe to run again: it skips what is already there.
# Installs: ffmpeg + Python 3.12 (winget), a private venv with mediapipe/opencv/numpy/pillow-heif,
# and the two face models, checked against their SHA-256.
# Run:  powershell -ExecutionPolicy Bypass -File scripts\setup.ps1
# shortcut: written for Windows but not tested on a real Windows machine yet; fix here if a step fails.
$ErrorActionPreference = "Stop"

$Dir = Split-Path -Parent $PSScriptRoot
$HomeDir = if ($env:PMU_BEAUTIFY_HOME) { $env:PMU_BEAUTIFY_HOME } else { Join-Path $env:USERPROFILE ".pmu-beautify" }
$Venv = Join-Path $HomeDir "venv"
$Models = Join-Path $HomeDir "models"
$VPy = Join-Path $Venv "Scripts\python.exe"

function Refresh-Path {  # winget installs land in PATH only for new shells: reload it here
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
}

if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    Write-Host "winget is missing. Install 'App Installer' from the Microsoft Store, then run this setup again:"
    Write-Host "  https://apps.microsoft.com/detail/9NBLGGH4NNS1"
    exit 2
}

if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    Write-Host "Installing ffmpeg..."
    winget install --id Gyan.FFmpeg -e --accept-source-agreements --accept-package-agreements --silent
    Refresh-Path
    if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
        Write-Host "ffmpeg installed but not on PATH yet: close this window, open a new one and run setup again."
        exit 4
    }
}

function Find-Py312 {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        try {  # PowerShell 5.1 + "Stop" turns a redirected native stderr line into a terminating error
            $p = & py -3.12 -c "import sys; print(sys.executable)" 2>$null
            if ($LASTEXITCODE -eq 0 -and $p) { return "$p".Trim() }
        } catch { }
    }
    $c = Join-Path $env:LOCALAPPDATA "Programs\Python\Python312\python.exe"
    if (Test-Path $c) { return $c }
    return $null
}
$Py = Find-Py312
if (-not $Py) {
    Write-Host "Installing Python 3.12..."
    winget install --id Python.Python.3.12 -e --accept-source-agreements --accept-package-agreements --silent
    Refresh-Path
    $Py = Find-Py312
    if (-not $Py) { Write-Host "Python 3.12 installed but not found yet: open a new window and run setup again."; exit 4 }
}

New-Item -ItemType Directory -Force -Path $Models | Out-Null
if (-not (Test-Path $VPy)) {
    Write-Host "Creating venv in $Venv..."
    & $Py -m venv $Venv
}
& $VPy -m pip install -q --upgrade pip
& $VPy -m pip install -q -r (Join-Path $Dir "requirements.txt")
if ($LASTEXITCODE -ne 0) { Write-Host "pip install failed"; exit 1 }

function Fetch($Name, $Url, $Sha) {
    $f = Join-Path $Models $Name
    if ((Test-Path $f) -and ((Get-FileHash $f -Algorithm SHA256).Hash.ToLower() -eq $Sha)) { return }
    Write-Host "Downloading $Name..."
    $part = "$f.part"
    $ProgressPreference = "SilentlyContinue"  # the progress bar makes Invoke-WebRequest very slow
    Invoke-WebRequest -Uri $Url -OutFile $part -UseBasicParsing
    if ((Get-FileHash $part -Algorithm SHA256).Hash.ToLower() -ne $Sha) { Remove-Item $part; Write-Host "Checksum mismatch for $Name"; exit 3 }
    Move-Item -Force $part $f
}
Fetch "face_landmarker.task" `
  "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task" `
  "64184e229b263107bc2b804c6625db1341ff2bb731874b0bcc2fe6544e0bc9ff"
Fetch "face_recognition_sface_2021dec.onnx" `
  "https://github.com/opencv/opencv_zoo/raw/main/models/face_recognition_sface/face_recognition_sface_2021dec.onnx" `
  "0ba9fbfa01b5270c96627c4ef784da859931e02f04419c829e83484087c34e79"

& $VPy -c "import cv2, mediapipe, numpy; cv2.FaceRecognizerSF"
if ($LASTEXITCODE -ne 0) { Write-Host "Import check failed"; exit 1 }
New-Item -ItemType File -Force -Path (Join-Path $HomeDir ".ready") | Out-Null
Write-Host "pmu-beautify ready. Python: $VPy"

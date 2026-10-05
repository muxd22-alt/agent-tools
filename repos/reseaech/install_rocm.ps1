# AutoResearch ROCm Windows Installer
# Installs AMD ROCm SDK + PyTorch for Windows with RX 7600 support
# Run: powershell -ExecutionPolicy Bypass -File install_rocm.ps1

$ErrorActionPreference = "Stop"

$ROCM_BASE = "https://repo.radeon.com/rocm/windows/rocm-rel-7.2"
$DOWNLOAD_DIR = "$PSScriptRoot\.rocm_wheels"

# Wheel files to download
$WHEELS = @(
    @{ Name = "ROCm SDK Core";      File = "rocm_sdk_core-7.2.0.dev0-py3-none-win_amd64.whl" },
    @{ Name = "ROCm SDK Libraries"; File = "rocm_sdk_libraries_custom-7.2.0.dev0-py3-none-win_amd64.whl" },
    @{ Name = "PyTorch ROCm";       File = "torch-2.9.1%2Brocmsdk20260116-cp312-cp312-win_amd64.whl" },
    @{ Name = "ROCm Base Module";   File = "rocm-7.2.0.dev0.tar.gz" }
)

Write-Host "=== AutoResearch ROCm Windows Installer ===" -ForegroundColor Cyan
Write-Host ""

# Create download directory
if (-not (Test-Path $DOWNLOAD_DIR)) {
    New-Item -ItemType Directory -Path $DOWNLOAD_DIR | Out-Null
}

# Download wheels
foreach ($wheel in $WHEELS) {
    if ($wheel.File.EndsWith(".whl")) {
        $localFile = [System.Uri]::UnescapeDataString($wheel.File)
    } else {
        $localFile = $wheel.File
    }
    $url = "$ROCM_BASE/$($wheel.File)"
    $outPath = "$DOWNLOAD_DIR\$localFile"
    
    if (Test-Path $outPath) {
        Write-Host "[OK] $($wheel.Name) already downloaded" -ForegroundColor Green
    } else {
        Write-Host "[DL] Downloading $($wheel.Name)..." -ForegroundColor Yellow
        Write-Host "     URL: $url"
        try {
            Invoke-WebRequest -Uri $url -OutFile $outPath -UseBasicParsing
            Write-Host "     Done!" -ForegroundColor Green
        } catch {
            Write-Host "     FAILED: $_" -ForegroundColor Red
            exit 1
        }
    }
}

Write-Host ""
Write-Host "=== Installing into uv venv ===" -ForegroundColor Cyan

# Ensure venv exists
$uvPath = "$env:USERPROFILE\.local\bin\uv.exe"
if (-not (Test-Path $uvPath)) {
    $uvPath = "uv"
}

# Sync non-torch dependencies first
Write-Host "[1/2] Installing base Python dependencies..." -ForegroundColor Yellow
& $uvPath sync --no-install-project
if ($LASTEXITCODE -ne 0) {
    Write-Host "uv sync failed!" -ForegroundColor Red
    exit 1
}

# Install ROCm SDK and PyTorch into the venv
Write-Host "[2/2] Installing ROCm SDK and PyTorch..." -ForegroundColor Yellow

$coreWheel  = "$DOWNLOAD_DIR\rocm_sdk_core-7.2.0.dev0-py3-none-win_amd64.whl"
$libWheel   = "$DOWNLOAD_DIR\rocm_sdk_libraries_custom-7.2.0.dev0-py3-none-win_amd64.whl"
$torchWheel = "$DOWNLOAD_DIR\torch-2.9.1+rocmsdk20260116-cp312-cp312-win_amd64.whl"
$rocmTar    = "$DOWNLOAD_DIR\rocm-7.2.0.dev0.tar.gz"

# Install all at once to resolve dependencies across wheels
& $uvPath pip install "$coreWheel" "$libWheel" "$torchWheel" "$rocmTar" --reinstall --no-deps
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installation of ROCm/PyTorch wheels failed!" -ForegroundColor Red
    exit 1
}

# Verify installation
Write-Host ""
Write-Host "=== Verifying Installation ===" -ForegroundColor Cyan
$venvPython = "$PSScriptRoot\.venv\Scripts\python.exe"
& $venvPython -c @"
import torch
print(f'PyTorch version: {torch.__version__}')
hip_avail = hasattr(torch.version, 'hip') and torch.version.hip is not None
print(f'HIP available:   {hip_avail}')
if hip_avail:
    print(f'HIP version:     {torch.version.hip}')
print(f'CUDA available:  {torch.cuda.is_available()}')
if torch.cuda.is_available():
    import torch.cuda
    print(f'GPU:             {torch.cuda.get_device_name(0)}')
    props = torch.cuda.get_device_properties(0)
    print(f'VRAM Total:      {props.total_mem / 1024**3:.2f} GB')
    print(f'VRAM Free/Resrv: {torch.cuda.memory_reserved(0) / 1024**2:.2f} MB')
"@

Write-Host ""
Write-Host "=== Installation Complete ===" -ForegroundColor Green
Write-Host "Run 'uv run prepare.py --num-shards 8' to prepare data"
Write-Host "Run 'uv run train.py' for a baseline training run"

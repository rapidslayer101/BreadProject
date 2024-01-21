# Check if nvcc.exe exists in the PATH
$nvccPath = Get-Command nvcc.exe -ErrorAction SilentlyContinue
if ($nvccPath) {
    Write-Host "CUDA Toolkit is already installed."
} else {
    Write-Host "Installing CUDA Toolkit..."
    winget install --id=Nvidia.CUDA  -e
}


$env:CMAKE_ARGS="-DLLAMA_CUBLAS=on"
pip install llama-cpp-python --force-reinstall --no-cache-dir


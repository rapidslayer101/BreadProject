# Check if nvcc.exe exists in the PATH
$nvccPath = Get-Command nvcc.exe -ErrorAction SilentlyContinue
if ($nvccPath) {
    Write-Host "CUDA Toolkit is already installed."
} else {
    # Specify the URL of the CUDA Toolkit installer
    # Replace this URL with the actual download link for the version you need
    $url = "https://developer.download.nvidia.com/compute/cuda/12.3.2/network_installers/cuda_12.3.2_windows_network.exe"

    # Specify the path where the installer will be saved
    $output = "C:\cuda_installer.exe"

    # Download the installer
    Invoke-WebRequest -Uri $url -OutFile $output

    # Run the installer
    # Additional arguments can be added for silent installation or specific installation options
    Start-Process -FilePath $output -ArgumentList "/S" -Wait

    Write-Host "CUDA Toolkit installation process has been initiated."
}


$env:CMAKE_ARGS="-DLLAMA_CUBLAS=on"
pip install llama-cpp-python --force-reinstall --no-cache-dir


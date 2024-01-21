cd %UserProfile%\BreadClient
echo y |.\Miniconda3\_conda.exe install -p %UserProfile%\BreadClient\venv python=3.11 conda-forge::llama-cpp-python conda-forge::pycuda nvidia::cuda-nvtx pytorch::pytorch pytorch::torchvision pytorch::torchaudio pytorch-cuda=12.1
echo y |.\Miniconda3\_conda.exe install -p %UserProfile%\BreadClient\venv -c huggingface transformers datasets
.\launch.bat
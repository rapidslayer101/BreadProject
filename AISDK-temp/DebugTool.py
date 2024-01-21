""" ⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⡀⠀⠀⠀
⣿⣩⣿⣉⣉⣉⠉⠉⠉⠉⠉⠉⠙⣷⣄⠀
⠀⠀⢈⡟⢸⡟⣷⠀⠀⠀⠀⠀⡾⠋⠀⠀
⠀⠀⣾⣵⠟⠀⣿⠛⠛⠛⠛⢻⡇⠀⠀⠀
⠀⠀⠈⠁⠀⠀⣿⠛⠛⠛⠛⠛⣷⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢿⡀⠀⠀⠀⠀⠸⣇⠀⠀
⠀⠀⠀⠀⠀⠀⠘⣇⠀⠀⠀⠀⠀⢻⡄⠀
⠀⠀⠀⠀⠀⠀⢀⡟ JakeR⠈⣷⠀
⠀⠀⠀⠀⢀⡾⠃IlloomAI⢹⡆
⠀⠀⠀⠀⢠⡾⢁⡴⠒⠒⠒⠒⠲⣦⠘⣧
⠀⠀⠀⢠⡟⢠⡟⠁AISDK⣿⠀⣿
⠀⠀⠀⣿⢀⡟⠀  BUG  ⣿⠀⣿
⠀⠀⢰⡇⢸⣇Remover⢀⣿⠀⣿
⠀⠀⠈⢧⣀⣉⣉⣉⣉⣉⣉⣉⣉⣁⣠⡟
⠀⠀⠀⠀⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠁⠀ """
import subprocess
import platform
import GPUtil

try:
    import torch
    import pycuda.driver as cuda
except:
    print("Failed to import Pytorch or Pycuda, NVIDIA specific functions will crash.")


def get_best_accelerator():
    """
    Finds and returns the best AI Accelerator in the system
    This is usually the most powerful GPUs however I anticipate AI
    accelerators will be large soon.
    :return: best attached AI Accelerator i.e. NVIDIA, RTX 3090, 24GB VRAM
    """

    match len(GPUtil.getGPUs()):
        case 0:
            return {"name": None,
                    "manufacturer": None,
                    "vram": 0,
                    "score": -9999}
        case 1:
            gpu = GPUtil.getGPUs()[0]
            return {"name": gpu.name, "manufacturer": gpu.name.split()[0], "vram": gpu.memoryTotal, "score": "-1"}
        case _:
            scoring = {"NVIDIA": 1000000, "AMD": 500000}
            gpu_scores = []
            for gpu in GPUtil.getGPUs():
                gpu_scores.append({"name": gpu.name,
                                   "manufacturer": gpu.name.split()[0],
                                   "vram": gpu.memoryTotal,
                                   "score": scoring.get(gpu.name.split()[0], 0) + gpu.memoryTotal})
            gpu_scores = sorted(gpu_scores, key=lambda x: x['score'], reverse=True)
            return gpu_scores[0]


def _check_rocm_installed():
    """
    Check if ROCm is installed on linux.
    :return:
    """
    try:
        subprocess.run(["pip", "show", "roccl"], check=True)
        return True
    except FileNotFoundError:
        return False


def _check_rocm_support(GPU):
    """
    Checks if ROCm is supported
    :return: -1 if OS is unsupported, 0 if GPU is unsupported, 1 if ROCm and OS is supported.
    """

    '''Windows only code, we do not support ROCm on windows due to pytorch not working
    ROCmCards = {"6600", "6600 XT", "6650 XT", "6700", "6700 XT", "6750", "6800", "6800 XT", "6900 XT",
                "6950 XT", "7600", "7900 XT", "7900 XTX", "VII", "W5500", "W6600", "W6800", "W7800", "W7900"}

    print("Checking your card supports ROCm...")
    if any(card in GPU['name'] for card in ROCmCards):
        print(f"✓ Your card {GPU['name']}, appears to support ROCm on wid!")
    else:
        print(f"""✗ Your card {GPU['name']} does not appear to support ROCm
Check https://rocm.docs.amd.com/projects/install-on-windows/en/latest/reference/system-requirements.html to confirm
if your card does support ROCm, please contact Jake.""")'''

    os_name = platform.system()
    if os_name == "Windows" or os_name == "Darwin ":
        return -1
    else:
        ROCm_Cards = ["W7900", "W6800", "V620", "VII", "7900 XTX", "7900 XT"]
        if any(card in GPU['name'] for card in ROCm_Cards):
            return 1
    return 0


def _check_cuda_support():
    """
    Checks if the GPU supports CUDA
    :return: True if CUDA is supported, False if not
    """
    cuda.init()  # Initialize CUDA

    if cuda.Device.count() > 0:
        # Get the name and compute capability of each GPU
        for i in range(cuda.Device.count()):
            return True
    return False


def check_cuda_toolkit():
    """
    Checks if CUDA Toolkit is installed.
    :return: True if CUDA is installed, None otherwise
    """
    try:
        output = subprocess.check_output(['nvcc', '--version'], text=True)
        if "release" in output:
            return True
        else:
            return None
    except FileNotFoundError:
        return None


def _check_py_torch_supports_cuda():
    if torch.cuda.is_available():
        return True
    else:
        return False


def _check_py_torch_supports_rocm():
    try:
        if torch.backends.mlu.is_available():
            return True
    except:
        print("WARNING: ERROR ACCESSING MLU BACKEND")
    return False


def get_system_report():
    print("Only use this tool to debug your configs, please double check EVERYTHING it says, especially anything ROCm.")
    return_flag = True
    GPU = get_best_accelerator()
    if GPU["name"] is None:
        print("✗ - No GPUs found, only the CPU is available.")
        return_flag = False
    else:
        print(f"✓ - GPU Found: {GPU['name']} (VRAM {GPU['vram']} mb)")

    if GPU["manufacturer"] == "NVIDIA":
        print("✓ - Nvidia Card detected")

        # Check card supports CUDA
        if _check_cuda_support():
            print(f"✓ - Your GPU supports CUDA")
        else:
            print("✗ - Your GPU doesn't support CUDA.")
            return_flag = False

        # Check CUDA Toolkit is installed.
        if check_cuda_toolkit():
            print("✓ - CUDA Toolkit Found")
        else:
            print("✗ - CUDA Toolkit not found")
            return_flag = False

        # Check PyTorch is correctly installed
        if _check_py_torch_supports_cuda():
            print(f"✓ - Your pytorch install supports CUDA")
        else:
            print("✗ - Your pytorch does not support CUDA, reinstall it here: https://pytorch.org/get-started/locally/")
            return_flag = False

    elif GPU["manufacturer"] == "AMD":
        print("You are using an AMD GPU, this code has not been properly tested also inference on AMD GPUs is " +
              "MUCH slower than NVIDIA GPUs. ")
        print("✓ - AMD Card detected")
        ROCm_support = _check_rocm_support(GPU)
        if ROCm_support == -1:
            print("✗ - AI SDK does not support ROCm on win or mac at this time as pytorch ROCm only works on linux .")
            print("NOTE: This does not mean your GPU supports/does not support ROCm")
            return_flag = False
        elif ROCm_support == 0:
            print("✗ - Your OS Supports ROCm but your GPU does not, check the ROCm website to confirm this.")
            print(
                "NOTE: Check https://rocm.docs.amd.com/projects/install-on-windows/en/latest/reference/system"
                "-requirements.html to confirm")
            return_flag = False
        else:
            print(f"✓ Your card {GPU['name']}, appears to support ROCm on linux!")
            print("Checking ROCm is installed...")
            if _check_rocm_installed:
                print("✓ - ROCm is installed")
            else:
                print("✗ - ROCm is not installed.")
                return_flag = False

            if _check_py_torch_supports_cuda() or _check_py_torch_supports_rocm():
                print(f"✓ - Your pytorch install appears to support CUDA/ROCm")
            else:
                print("✗ - ROCm is not available")
                return_flag = False

    elif str(GPU["manufacturer"]).upper() == "INTEL":
        print("✗ - Intel Arc/Integrated Graphics are not supported by AISDK")
        return_flag = False

    if GPU["name"] is not None:
        if get_flash_attention_support(GPU):
            print("✓ - Your GPU supports Flash Attention 2 (30/40 series GPUs) (check support for 20 series)")
        else:
            print("✗ - Your GPU does not support Flash Attention 2 (NVIDIA 30/40 series GPUs)")
    else:
        print("✗ - Flash Attention 2 requires an NVIDIA 30/40 series GPUs")

    return return_flag


def get_flash_attention_support(gpu=None):
    if gpu is None:
        gpu = get_best_accelerator()

    if gpu['manufacturer'] == "NVIDIA":
        cuda.init()
        major, minor = cuda.Device(0).compute_capability()
        if major == 8 or major == 9:
            return True

    return False


if __name__ == '__main__':
    print("You are running AISDK Debug Tool as the main file, checking your system config.")
    get_system_report()

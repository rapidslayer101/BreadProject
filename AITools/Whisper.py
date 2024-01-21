"""
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢠⡄⠀⠀⠀⠀⠀⠀⢠⡄⢸⡇⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⢠⡄⢸⡇⠀⠀⠀⠀⠀⠀⢸⡇⢸⡇⢸⡇⠀⠀⢸⡇⢀⡀⠀⠀⠀⠀⠀
⠀⢠⡄⢸⡇⢸⡇⢸⡇⢀⡀⢰⡆⢸⡇⢸⡇⢸⡇⢰⡇⢸⡇⢸⡇⢠⡀⠀⠀⠀
⠀⢸⡇⢸⡇⢸⡇⢸⡇⢸⡇⢸⡇⢸⡇⢸⡇⢸⡇⢸⡇⢸⡇⢸⡇⢸⡇⢸⡇⠀
⠀⠘⠃⢸⡇⢸⡇⢸⡇⠈⠁⢸⡇⢸⡇⢸⡇⢸⡇⠸⡇⢸⡇⢸⡇⠘⠁⠀⠀⠀
⠀⠀⠀⠈⠁⢸⡇⠀⠀⠀⠀⠀⠀⢸⡇⢸⡇⢸⡇⠀⠀⢸⡇⠈⠁⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠈⠁⠀⠀⠀⠀⠀⠀⠘⠃⢸⡇⢸⠇⠀⠀⠀IlloomAI⠀⠀
Whisper         ⢸⡇⠀⠀⠀Written by JakeR⠀⠀⠀⠀⠀⠀
Interface
"""
import os

import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from datasets import load_dataset


import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

class Whisper:
    def __init__(self, model_path):
        import torch
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        print(f"CUDA/ROCm available: {self.device}")
        self.torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

        # Load the model from the specified path
        self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
            model_path, torch_dtype=self.torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
        )
        self.model.to(self.device)

        # Load the processor from the same path
        self.processor = AutoProcessor.from_pretrained(model_path)

        self.pipe = pipeline(
            "automatic-speech-recognition",
            model=self.model,
            tokenizer=self.processor.tokenizer,
            feature_extractor=self.processor.feature_extractor,
            max_new_tokens=128,
            chunk_length_s=30,
            batch_size=16,
            return_timestamps=True,
            torch_dtype=self.torch_dtype,
            device=self.device,
        )
        print(f"READY!")

    def transcribe(self, audio_file_path):
        result = self.pipe(audio_file_path)
        return result["text"]

# Usage


if __name__ == "__main__":
    print("This is a library file, see WhisperTest.py for an example on how to use this.")
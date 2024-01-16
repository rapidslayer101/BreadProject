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


class Whisper():
    pipe = pipeline

    def __init__(self, ModelPath):
        global pipe
        os.chdir(ModelPath)
        print("Initialising Whisper object")
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        print(f"Using {device} device")

        model = AutoModelForSpeechSeq2Seq.from_pretrained(
            "openai/whisper-large-v3", torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True)
        model.to(device)

        processor = AutoProcessor.from_pretrained("openai/whisper-large-v3")

        pipe = pipeline(
            "automatic-speech-recognition",
            model=model,
            tokenizer=processor.tokenizer,
            feature_extractor=processor.feature_extractor,
            max_new_tokens=128,
            chunk_length_s=30,
            batch_size=16,
            return_timestamps=True,
            torch_dtype=torch_dtype,
            device=device,
        )

        dataset = load_dataset("distil-whisper/librispeech_long", "clean", split="validation")
        sample = dataset[0]["audio"]

    def get_text(self, FilePath):
        """
        Gets text from a given filepath
        """

        global pipe
        return pipe(FilePath)

if __name__ == "__main__":
    print("This is a library file, see WhisperTest.py for an example on how to use this.")
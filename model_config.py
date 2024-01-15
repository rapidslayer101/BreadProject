import os
import multiprocessing

print(multiprocessing.cpu_count())

model_configs = {"TheBloke/LLaMA-Pro-8B-Instruct-GGUF/llama-pro-8b-instruct.Q8_0.gguf":
                     {"model_alias": "llama-pro", "chat_format": "chatml", "n_gpu_layers": -1, "offload_kqv": "true",
                      "n_threads": 8, "n_batch": 512, "n_ctx": 4096},

                 "TheBloke/Mistral-7B-Instruct-v0.1-GGUF/mistral-7b-instruct-v0.1.Q5_K_M.gguf":
                     {"model_alias": "mistral", "chat_format": "chatml", "n_gpu_layers": -1, "offload_kqv": "true",
                      "n_threads": 8, "n_batch": 512, "n_ctx": 16384},

                 "TheBloke/OpenHermes-2.5-Mistral-7B-16k-GGUF/openhermes-2.5-mistral-7b-16k.Q5_K_M.gguf":
                     {"model_alias": "mistral16k", "n_gpu_layers": -1, "offload_kqv": "true", "n_threads": 8,
                      "n_batch": 512, "n_ctx": 4096},

                 "TheBloke/phi-2-GGUF/phi-2.Q8_0.gguf":
                     {"model_alias": "lunatic", "n_gpu_layers": -1, "offload_kqv": "true", "n_threads": 8,
                      "n_batch": 1024, "n_ctx": 2048},
}


loaded_models = []

for directory in os.listdir("models/"):
    models = os.listdir(f"models/{directory}")
    for model in models:
        for variant in os.listdir(f"models/{directory}/{model}"):
            loaded_models.append(f"{directory}/{model}/{variant}")


model_configs_string = ""
for model in loaded_models:
    if model in list(model_configs.keys()):
        print(model_configs[model])
        model_configs[model]["model_path"] = f"models/{model}"
        print(model_configs[model])
        model_configs_string += str(model_configs[model])+",\n"
    else:
        print(f"Invalid model: {model}")
model_configs_string = model_configs_string[:-2]+"\n"


model_configs = """{
    "host": "0.0.0.0",
    "port": 8080,
    "models": [\n"""+model_configs_string+"]"+"""}"""

with open("LLMServer/model_config.cfg", "w", encoding="utf-8") as f:
    f.write(str(model_configs))

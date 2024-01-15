from openai import OpenAI

client = OpenAI(base_url="http://localhost:8080/v1", api_key="not-needed")

def one_shot(SystemPrompt, UserPrompt, Model="Mistal", Temperature=0.2, MaxTokens=-1):
    completion = client.chat.completions.create(model=Model, temperature=Temperature, max_tokens=MaxTokens,
        messages=[{"role": "system", "content":SystemPrompt}, {"role": "user", "content": UserPrompt}])

    return completion.choices[0].message.content.strip()
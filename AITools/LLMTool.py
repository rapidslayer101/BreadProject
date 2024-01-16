from openai import OpenAI

client = OpenAI(base_url="http://localhost:8080/v1", api_key="not-needed")


def one_shot(system_prompt, user_prompt, model="mistral16k", temperature=0.2, max_tokens=-1):
    completion = client.chat.completions.create(model=model, temperature=temperature, max_tokens=max_tokens,
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}])

    return completion.choices[0].message.content.strip()



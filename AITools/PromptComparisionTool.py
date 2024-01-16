"""
       /\
      /  \
     /,--.\
    /< () >\
   /  `--'  \
  / IlloomAI \
 /LMComparison\
/______________\
A tool for comparing multiple LLM Models, enter a prompt and see what the responses are.
"""
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8080/v1", api_key="none")

for model in client.models.list():
    response = client.chat.completions.create(temperature=0.3, top_p=0.05, frequency_penalty=2, model=model.id,
        messages=[
            {
                "content": """You answer complicated tech questions""",
                "role": "system"
            },
            {
                "content": """Explain how to partition a fresh debian distro""",
                "role": "user"
            }
        ]
    )

    print(f"\n\n[{model.id}] - {response.choices[0].message.content.strip()}")
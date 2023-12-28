# Example: reuse your existing OpenAI setup
from openai import OpenAI


def init():
    print("Starting server")
    # Point to the local server
    return OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")


def summarise_article(client, article_content):
    completion = client.chat.completions.create(
        model="local-model",  # this field is currently unused
        messages=[{"role": "system",
                   "content": "Following this message is a news article, summarise this to around 100 words."},
                  {"role": "user", "content": article_content}],
        temperature=0.2,
        top_p=0.5,
    )
    return completion.choices[0].message

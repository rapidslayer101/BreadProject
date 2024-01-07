"""
⠀⠀⠀⠀⠀⠀⢱⣆⠀⠀⠀⠀⠀⠀      FIREHOSE.py
⠀⠀⠀⠀⠀⠀⠈⣿⣷⡀⠀⠀⠀⠀      Probably created by JakeR
⠀⠀⠀⠀⠀⠀⢸⣿⣿⣷⣧⠀⠀⠀      A tool for automatically sorting, storing and dealing news article text.
⠀⠀⠀⠀⡀⢠⣿⡟⣿⣿⣿⡇⠀⠀
⠀⠀⠀⠀⣳⣼⣿⡏⢸⣿⣿⣿⢀⠀
⠀⠀⠀⣰⣿⣿⡿⠁⢸⣿⣿⡟⣼⡆
⢰⢀⣾⣿⣿⠟⠀⠀⣾⢿⣿⣿⣿⣿
⢸⣿⣿⣿⡏⠀⠀⠀⠃⠸⣿⣿⣿⡿
⢳⣿⣿⣿⠀⠀⠀⠀⠀⠀⢹⣿⡿⡁
⠀⠹⣿⣿⡄⠀⠀⠀⠀⠀⢠⣿⡞⠁
⠀⠀⠈⠛⢿⣄⠀⠀⠀⣠⠞⠋⠀⠀
⠀⠀⠀⠀⠀⠀⠉⠀⠀⠀⠀⠀⠀⠀
"""
from openai import OpenAI

import Hydrant
import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Mavik",
    database="Oven"
)
OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")
hy = Hydrant.Hydrant()
b = hy.get_stories(1)

print(db.cursor().execute("SELECT * FROM articles"))
"""
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
"""
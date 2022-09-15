from operator import index
from parse_post import *
import pandas as pd
from pandas import read_csv
from tqdm import tqdm

file = "data/dataset.csv"

df = read_csv(file, index_col=[0])

def extract_from_series(posts, extractor):
    elems = []
    for post in tqdm(posts):
        try:
            if isinstance(post, str):
                elems.append(" ".join(set(extractor.extract(post))))
            else:
                elems.append("")
        except Exception as e:
            elems.append("")
            print(post)
            print(extractor.extract(post))
            raise e
    return elems

# phone numbers
df = df.assign(phone_numbers=lambda df: extract_from_series(df.post, RegexPhoneNumberExtractor()))

# emails
df = df.assign(emails=lambda df: extract_from_series(df.post, EmailExtractor()))

# snapchat
df = df.assign(snapchat_users=lambda df: extract_from_series(df.post, SnapchatUsernameExtractor()))

# instagram
df = df.assign(insta_users=lambda df: extract_from_series(df.post, InstagramUsernameExtractor()))

# url
df = df.assign(urls=lambda df: extract_from_series(df.post, UrlExtractor()))


df.to_csv("data/dataset_ext.csv")
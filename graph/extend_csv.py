from parse_post import *
from pandas import read_csv
from tqdm import tqdm
from sys import argv

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

if __name__ == "__main__":

    file_data = argv[1]
    dump_to = argv[2]

    df = read_csv(file_data, index_col=[0])

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

    # time
    df = df.assign(time=lambda df: extract_from_series(df.date, TimeExtractor()))

    # date
    df = df.assign(date=lambda df: extract_from_series(df.date, DateExtractor()))

    # date
    df = df.assign(region=lambda df: extract_from_series(df.region, RegionExtractor()))

    df.to_csv(dump_to)

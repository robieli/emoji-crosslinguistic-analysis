from datasets import load_dataset
from huggingface_hub import login, HfApi


def main():
    langs = ["en", "it"]  # CHANGE THIS ONE
    data_ids = ["enryu43/twitter100m_tweets", "local"]
    # NOTE:
    filter = True

    data_ids = {lang: id for lang, id in zip(langs, data_ids)}
    lang_data = {}

    login(token="insert token here")
    api = HfApi()
    api.create_repo(
        "robieli/english_tweets_filtered", repo_type="dataset", exist_ok=True
    )
    api.create_repo(
        "robieli/italian_tweets_filtered", repo_type="dataset", exist_ok=True
    )

    for lang in langs:
        if data_ids[lang] == "local":
            lang_data[lang] = load_dataset(
                "parquet", data_files={"train": "it_data/train.parquet"}
            )["train"]
        else:
            lang_data[lang] = load_dataset(data_ids[lang], split="train")

        print(len(lang_data[lang]))
        if filter:
            lang_data[lang] = lang_data[lang].filter(
                lambda x: x["date"] >= "2022",
                batched=False,
            )
        print(len(lang_data[lang]))
        print(lang_data[lang][0])

        # remove unnecessary columns
        if lang == "it":
            lang_data[lang] = lang_data[lang].rename_column("text", "tweet")
            lang_data[lang] = lang_data[lang].rename_column("created_at", "date")
        lang_data[lang] = lang_data[lang].select_columns(["tweet", "date"])

        # filter for tweets in or after 2022
        if filter:
            lang_data[lang] = lang_data[lang].shuffle(seed=497)
            lang_data[lang] = lang_data[lang].select(range(500000))
            print(len(lang_data[lang]))
            if lang == "en":
                lang_data[lang].push_to_hub("robieli/english_tweets_filtered")
            elif lang == "it":
                lang_data[lang].push_to_hub("robieli/italian_tweets_filtered")
    print(lang_data["en"][0])
    print(lang_data["it"][0])


if __name__ == "__main__":
    main()

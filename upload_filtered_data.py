from datasets import load_dataset
import emoji


def main():
    langs = ["it"]  # CHANGE THIS ONE
    data_ids = ["local"]
    # NOTE:
    filter = True

    data_ids = {lang: id for lang, id in zip(langs, data_ids)}
    lang_data = {}

    for lang in langs:
        if data_ids[lang] == "local":
            lang_data[lang] = load_dataset(
                "parquet", data_files={"train": "it_data/train.parquet"}
            )["train"]
        else:
            lang_data[lang] = load_dataset(data_ids[lang], split="train")

        if lang == "it":
            lang_data[lang] = lang_data[lang].rename_column("created_at", "date")

        if filter:
            lang_data[lang] = lang_data[lang].filter(
                lambda x: x["date"] >= "2018" and emoji.emoji_count(x["text"]) > 0,
                batched=False,
            )

        # remove unnecessary columns
        lang_data[lang] = lang_data[lang].select_columns(["text"])

        # filter for tweets in or after 2022
        if filter:
            lang_data[lang] = lang_data[lang].shuffle(seed=497)
            lang_data[lang] = lang_data[lang].select(range(500000))
            print(len(lang_data[lang]))
            if lang == "en":
                lang_data[lang].save_to_disk("../en_data")
            elif lang == "it":
                lang_data[lang].save_to_disk("../it_data")


if __name__ == "__main__":
    main()

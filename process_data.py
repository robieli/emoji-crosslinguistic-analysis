from datasets import load_dataset
import numpy as np
import emoji
import csv
from tqdm import tqdm
import matplotlib.pyplot as plt
from collections import Counter
import ast


class Data:
    size = 500000
    langs = ["en", "it"]  # CHANGE THIS ONE
    labels = ["English", "Italian"]
    formats = ["tweet", "text"]
    date_formats = ["date", "created_at"]
    data_ids = ["enryu43/twitter100m_tweets", "local"]

    # labels = {lang: label for lang, label in zip(langs, labels)}
    formats = {lang: format for lang, format in zip(langs, formats)}
    date_formats = {lang: format for lang, format in zip(langs, date_formats)}
    data_ids = {lang: id for lang, id in zip(langs, data_ids)}
    lang_data = {}
    lang_emoji = {}

    def __init__(self) -> None:
        # load in language datasets
        for lang in self.langs:
            if self.data_ids[lang] == "local":
                self.lang_data[lang] = load_dataset(
                    "parquet", data_files={"train": "it_data/train.parquet"}
                ).with_format("numpy")["train"]
            else:
                self.lang_data[lang] = load_dataset(
                    self.data_ids[lang], split="train"
                ).with_format("numpy")

            # filter for tweets in or after 2022
            # self.lang_data[lang] = self.lang_data[lang].filter(
            #     lambda x: int(x[self.date_formats[lang]][:4]) >= 2022
            # )

            # shuffle datapoints
            # self.lang_data[lang] = self.lang_data[lang].shuffle(seed=497)

        # process datasets
        for lang in self.langs:
            self._extract_emoji(lang)

    def _extract_emoji(self, lang):
        "Extract datasets into single lists of emoji and their associated tweet indices"
        output = []
        dataset = self.lang_data[lang]

        output = self.read_from_csv(lang)
        if output:
            print(f"CSV file {lang}_emojis.csv found, drawing data from file")
            self.lang_emoji[lang] = output
        else:
            print(f"CSV file {lang}_emojis.csv not found, processing dataset")

            for i, data in enumerate(tqdm(dataset)):
                # limit size to 500000
                if i >= self.size:
                    break

                # handle different JSON formats
                text = data[self.formats[lang]]

                # remove non-emoji text
                just_emoji = self.extract_single_emoji(text)
                if just_emoji:
                    output.append((just_emoji, i))
            self.lang_emoji[lang] = output
            self.write_to_csv(lang)

    def extract_single_emoji(self, text: str) -> list:
        parsed = emoji.analyze(text, join_emoji=True)
        output = []
        for token in parsed:
            output.append(token.chars)
        return output

    def write_to_csv(self, lang: str):
        "writes <lang>_emojis[] to csv file <lang>_emojis.csv"
        file = lang + "_emojis.csv"
        with open(file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(self.lang_emoji[lang])

    def read_from_csv(self, lang: str) -> list[tuple[list[str], int]]:
        "reads <lang>_emojis.csv to attribute <lang>_emojis[]"
        file = lang + "_emojis.csv"
        output = []
        try:
            with open(file, "r", newline="") as f:
                reader = csv.reader(f)
                for row in reader:
                    output.append((row[0], row[1]))
        except FileNotFoundError:
            print(f"CSV file {file} not found")
        return output

    def percent_with_emojis(self) -> None:
        "processes and displays the percent of tweets with emoji in each language"
        y = np.empty(len(self.lang_data))
        for i, lang in enumerate(self.lang_data):
            y[i] = len(self.lang_emoji[lang]) / self.size
        plt.figure()
        plt.title("Percent of tweets containing any emoji")
        plt.bar(self.labels, y)
        plt.savefig("percent_with_emojis.png")
        plt.show()

    def percent_with_specific_emoji(self, input: str) -> None:
        "processes and displays the percent of tweets with a specific emoji in each language"

        if not emoji.is_emoji(input):
            print("Failed. Please input a single Unicode emoji character.")

        y = np.empty(len(self.lang_data))

        for i, lang in enumerate(self.langs):
            count = 0
            for x, _ in tqdm(self.lang_emoji[lang]):
                if input in x:
                    count += 1
            y[i] = count / len(self.lang_emoji[lang])

        plt.figure()
        plt.title(f"Percent of tweets containing {input}")
        plt.bar(self.labels, y)
        plt.savefig(f"percent_with_{emoji.demojize(input)[1:-1]}")
        plt.show()

    def top_emoji(self, k: int) -> None:
        "processes and displays the top k emoji in each language"

        fig, axs = plt.subplots(1, len(self.langs))
        for i, ax in enumerate(axs):
            ax.set_title(f"Top {k} {self.labels[i]} Emoji")

        for i, lang in enumerate(self.langs):
            emoji_counter = Counter()
            for emojis, _ in self.lang_emoji[lang]:
                emojis = ast.literal_eval(emojis)
                unique_emojis = set(emojis)  # remove duplicates in each item
                emoji_counter.update(unique_emojis)

            most_common = emoji_counter.most_common(k)
            x, y = zip(*most_common)
            axs[i].bar(x, y)

        plt.savefig(f"top_{k}_emoji.png")
        plt.show()


def main():
    data = Data()
    # data.percent_with_emojis()
    # data.percent_with_specific_emoji(emoji.emojize("😱"))
    data.top_emoji(10)


if __name__ == "__main__":
    main()

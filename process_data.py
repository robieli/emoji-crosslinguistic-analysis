from datasets import load_dataset
import numpy as np
import emoji
import csv
from tqdm import tqdm
import matplotlib as mpl
from matplotlib import font_manager
import matplotlib.pyplot as plt
from collections import Counter
import ast
import re


# font_manager.fontManager.addfont("/usr/share/fonts/noto/NotoColorEmoji.ttf")
# try:
#     font_path = font_manager.findfont("Noto Color Emoji", fallback_to_default=False)
#     print(f"Found Noto Color Emoji at: {font_path}")
# except ValueError:
#     print(
#         "Noto Color Emoji not found by Matplotlib. Run 'fc-list' in terminal to confirm."
#     )
#     font_path = None

# FONT_PATH = "/usr/share/fonts/noto/NotoColorEmoji.ttf"
#
# prop = font_manager.FontProperties(fname=FONT_PATH)
# print(prop)

# plt.rcParams["font.family"] = "Noto Color Emoji"


class Data:
    size = 500000
    langs = ["en", "it"]  # CHANGE THIS ONE
    labels = ["English", "Italian"]
    data_ids = ["robieli/english_tweets_filtered", "robieli/italian_tweets_filtered"]

    # labels = {lang: label for lang, label in zip(langs, labels)}
    data_ids = {lang: id for lang, id in zip(langs, data_ids)}
    lang_data = {}
    lang_emoji = {}

    def __init__(self) -> None:
        # load in language datasets
        for lang in self.langs:
            self.lang_data[lang] = load_dataset(
                self.data_ids[lang], split="train"
            ).with_format("numpy")
            self.lang_data[lang] = self.lang_data[lang]["tweet"]

        # process datasets
        for lang in self.langs:
            self._extract_emoji(lang)

    def _extract_emoji(self, lang):
        "Extract datasets into single lists of emoji and their associated tweet indices"
        output = []
        dataset = self.lang_data[lang]

        output = self.read_from_csv(lang)
        if output:
            print(f"CSV file {lang}_emoji.csv found, drawing data from file")
            self.lang_emoji[lang] = output
        else:
            print(f"CSV file {lang}_emoji.csv not found, processing dataset")

            for i, data in enumerate(tqdm(dataset)):
                # limit size to 500000
                if i >= self.size:
                    break

                # remove non-emoji text
                just_emoji = self.extract_single_emoji(data)
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
        "writes <lang>_emoji[] to csv file <lang>_emoji.csv"
        file = lang + "_emoji.csv"
        with open(file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(self.lang_emoji[lang])

    def read_from_csv(self, lang: str) -> list[tuple[list[str], int]]:
        "reads <lang>_emoji.csv to attribute <lang>_emoji[]"
        file = lang + "_emoji.csv"
        output = []
        try:
            with open(file, "r", newline="") as f:
                reader = csv.reader(f)
                for row in reader:
                    emojis = ast.literal_eval(row[0])
                    output.append((emojis, row[1]))
        except FileNotFoundError:
            print(f"CSV file {file} not found")
        return output

    def percent_with_emoji(self) -> None:
        "processes and displays the percent of tweets with emoji in each language"
        y = np.empty(len(self.lang_data))
        for i, lang in enumerate(self.lang_data):
            y[i] = len(self.lang_emoji[lang]) / self.size
        plt.figure()
        plt.title("Percent of tweets containing any emoji")
        plt.bar_label(plt.bar(self.labels, y))
        plt.savefig("percent_with_emoji.png")
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
        plt.bar_label(plt.bar(self.labels, y))
        plt.savefig(f"percent_with_{self.emoji_name(input)}")
        plt.show()

    def emoji_name(self, text: str) -> str:
        "takes in an emoji and returns the name, stripped of skin_tone"
        if not emoji.is_emoji(text):
            return text
        text = emoji.demojize(text)
        text = re.sub(
            r"(_(light|medium-light|medium|medium-dark|dark)_skin_tone)", "", text
        )
        return text[1:-1]

    def handshape_emoji(self) -> None:
        "returns chart with percent of handshape emoji"

        handshape_emoji = []
        file = "handshape_emoji.csv"
        try:
            with open(file, "r", newline="") as f:
                reader = csv.reader(f)
                handshape_emoji = next(reader)
        except FileNotFoundError:
            print(f"CSV file {file} not found")
            return

        handshape_emoji = set(handshape_emoji)

        y = np.zeros(len(self.langs))
        for i, lang in enumerate(self.langs):
            count = 0
            for emojis, _ in self.lang_emoji[lang]:
                emojis = [self.emoji_name(item) for item in emojis]
                emojis = set(emojis)
                common = emojis.intersection(handshape_emoji)
                if common:
                    count += 1
            y[i] = count / len(self.lang_emoji[lang])

        plt.figure()
        plt.title("Percent of tweets with emoji containing handshape emoji")
        plt.bar_label(plt.bar(self.labels, y))
        plt.savefig("percent_with_handshape_emoji.png")
        plt.show()

    def top_emoji(self, k: int) -> None:
        "processes and displays the top k emoji in each language"

        fig, axs = plt.subplots(1, len(self.langs))
        for i, ax in enumerate(axs):
            ax.set_title(f"Top {k} {self.labels[i]} Emoji")

        for i, lang in enumerate(self.langs):
            emoji_counter = Counter()
            # I wish I could use emoji like everywhere else but it overshadows the import :sad_face:
            for emojis, _ in self.lang_emoji[lang]:
                unique_emojis = set(emojis)  # remove duplicates in each item
                emoji_counter.update(unique_emojis)

            most_common = emoji_counter.most_common(k)
            x, y = zip(*most_common)
            axs[i].bar(x, y)

        plt.savefig(f"top_{k}_emoji.png")
        plt.show()

    def emoji_per_character(self) -> None:
        "displays a chart of the emoji per character in each language"

        y = np.zeros(len(self.langs))
        for i, lang in enumerate(self.langs):
            num_emoji = 0
            num_char = 0
            for emojis, idx in self.lang_emoji[lang]:
                num_emoji += len(emojis)
                num_char += len(self.lang_data[lang][idx])
            y[i] = num_emoji / num_char

            plt.figure()
            plt.title("Emoji per character in tweets containing emoji")
            plt.bar_label(plt.bar(self.labels, y))
            plt.savefig("emoji_per_character.png")
            plt.show()


def main():
    data = Data()
    print(len(data.lang_data["en"]))  # 43209702
    print(len(data.lang_data["it"]))  # 5858698
    # data.percent_with_emoji()
    # data.percent_with_specific_emoji(emoji.emojize(":pinched_fingers:"))
    # data.top_emoji(10)
    # data.handshape_emoji()
    # data.emoji_per_character()


if __name__ == "__main__":
    main()

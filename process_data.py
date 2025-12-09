from datasets import load_from_disk
import numpy as np
import emoji
import csv
from tqdm import tqdm
import matplotlib as mpl
import matplotlib.pyplot as plt
from collections import Counter
from random import randrange
import ast
import re
import os


class Data:
    size = 500000
    graph_dir = "graphs"
    langs = ["en", "it"]  # CHANGE THIS ONE
    labels = ["English", "Italian"]
    colors = ["#1F77B4", "#FF7F0E"]

    # labels = {lang: label for lang, label in zip(langs, labels)}
    lang_data = {}
    lang_emoji = {}

    def __init__(self, test=False) -> None:
        # load in language datasets
        if test:
            for lang in self.langs:
                self.lang_data[lang] = load_from_disk(
                    f"./test/{lang}_data"
                ).with_format("numpy")
                self.lang_data[lang] = self.lang_data[lang]["text"]
        else:
            for lang in self.langs:
                self.lang_data[lang] = load_from_disk(f"../{lang}_data").with_format(
                    "numpy"
                )
                self.lang_data[lang] = self.lang_data[lang]["text"]

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

    def get_random_tweet_with_emoji(self, lang) -> None:
        "Prints a new tweet after every keypress, until 'C' is pressed"
        kyp = ""
        i = 1
        while kyp.lower() != "c":
            idx = randrange(len(self.lang_emoji[lang]))
            emojis = self.lang_emoji[lang]
            entry = emojis[idx][1]
            print("-" * 10, "TWEET", i, "-" * 10)
            print("ENTRY:", entry)
            print(self.lang_data[lang][entry])
            i += 1
            kyp = input()

    def extract_single_emoji(self, text: str) -> list:
        text = text.replace("❤", "❤️")
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
                    output.append((emojis, int(row[1])))
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
        plt.savefig(f"./{self.graph_dir}/percent_with_emoji.png")
        plt.show()

    def percent_with_specific_emoji(self, input: str) -> np.ndarray:
        "processes and displays the percent of tweets with a specific emoji in each language"

        if not emoji.is_emoji(input):
            print("Failed. Please input a single Unicode emoji character.")

        counts = np.empty(len(self.langs))
        y = np.empty(len(self.langs))

        for i, lang in enumerate(self.langs):
            count = 0
            for x, _ in tqdm(self.lang_emoji[lang]):
                if input in x:
                    count += 1
            counts[i] = count
            y[i] = count / len(self.lang_emoji[lang])

        print(counts)
        plt.figure()
        plt.title(f"Number of tweets containing {input}")
        plt.bar_label(plt.bar(self.labels, counts))
        plt.savefig(
            f"./{self.graph_dir}/specific/percent_with_{self.emoji_name(input)}"
        )
        plt.show()
        return counts

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

        fig, axs = plt.subplots(1, len(self.langs))
        if len(self.langs) == 1:
            axs = [axs]

        for i, ax in enumerate(axs):
            ax.pie(
                [y[i], 1 - y[i]],
                colors=[self.colors[i], "lightgray"],
                autopct="%1.1f%%",
            )
            ax.set_title(self.labels[i])

        plt.suptitle("Percent of tweets with emoji containing handshape emoji")
        plt.savefig(f"./{self.graph_dir}/percent_with_handshape_emoji.png")
        plt.show()

    def top_emoji(self, k: int) -> None:
        "plots the top k emoji in each language"

        fig, axs = plt.subplots(1, len(self.langs))
        for i, ax in enumerate(axs):
            ax.set_title(f"Top {k} {self.labels[i]} Emoji")

        for i, lang in enumerate(self.langs):
            emoji_counter = Counter()
            for emojis, _ in self.lang_emoji[lang]:
                unique_emojis = set(emojis)  # remove duplicates in each item
                emoji_counter.update(unique_emojis)

            most_common = emoji_counter.most_common(k)
            print(most_common)
            x, y = zip(*most_common)
            axs[i].bar(x, y)

        plt.savefig(f"./{self.graph_dir}/top_{k}_emoji.png")
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
        plt.bar_label(plt.bar(self.labels, y, color=self.colors))
        plt.savefig(f"./{self.graph_dir}/emoji_per_character.png")
        plt.show()

    def type_token_analysis(self) -> None:
        "processes and displays the type-token ratio of emoji in each language"

        y = np.zeros(len(self.langs))
        counts = np.zeros(len(self.langs))
        for i, lang in enumerate(self.langs):
            tokens = 0
            types = set()
            for emojis, _ in self.lang_emoji[lang]:
                tokens += len(emojis)
                types.update(emojis)
            counts[i] = len(types)

            if tokens > 0:
                y[i] = len(types) / tokens
            else:
                y[i] = 0

        plt.figure()
        plt.title("Type-Token Ratio of Emoji")
        plt.bar_label(plt.bar(self.labels, y))
        plt.savefig(f"./{self.graph_dir}/type_token_ratio.png")
        plt.show()

    def collect_type_data(self, lang: str, n=10, file=None) -> tuple[int, int, int]:
        "enters user into a manual referential/pragmatic gesture coding portal"
        counts = {"p": 0, "r": 0, "n": 0}
        if file:
            file = f"types/{lang}/types_{file}.csv"
            try:
                with open(file, "r", newline="") as f:
                    reader = csv.reader(f)
                    for row in reader:
                        for char in row[1]:
                            if char in counts:
                                counts[char] += 1
                return (counts["p"], counts["r"], counts["n"])
            except FileNotFoundError:
                print(f"CSV file {file} not found")

        print("Input 'p' for pragmatic and 'r' for referential")

        types = []
        for i in range(n):
            idx = randrange(len(self.lang_emoji[lang]))
            data = self.lang_data[lang]
            emojis = self.lang_emoji[lang]
            entry = emojis[idx][1]
            print("-" * 10, i + 1, "-" * 10)
            print(data[entry])
            type_input = input()
            valid = ["p", "r", "n"]
            if type_input and all(char in valid for char in type_input):
                types.append((data[entry], type_input))
                for char in type_input:
                    counts[char] += 1
            else:
                print("Invalid input")

        num = len(os.listdir("types")) + 1
        file = f"types/{lang}/types_{num}.csv"
        with open(file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(types)

        return (counts["p"], counts["r"], counts["n"])

    def plot_type_data(self, num=10, files=[0, 0]) -> None:
        "takes data collected by collect_type_data and plots it per language"
        categories = ("Pragmatic", "Referential", "Neither")
        x = np.arange(len(categories))  # the label locations
        width = 0.25  # the width of the bars
        multiplier = 0

        fig, ax = plt.subplots(layout="constrained")

        for i, lang in enumerate(self.langs):
            file_val = files[i] if i < len(files) else 0
            (p, r, n) = self.collect_type_data(lang, n=num, file=file_val)
            measurement = (p, r, n)

            offset = width * multiplier
            rects = ax.bar(x + offset, measurement, width, label=self.labels[i])
            ax.bar_label(rects, padding=3)
            multiplier += 1

        ax.set_ylabel("Count")
        ax.set_title("Emoji Type Distribution by Language")
        ax.set_xticks(x + width * (len(self.langs) - 1) / 2)
        ax.set_xticklabels(categories)
        ax.legend(loc="upper right")

        plt.savefig(f"./{self.graph_dir}/type_data.png")
        plt.show()

    def get_most_different(self, k) -> None:
        "plots the k emoji with most proportional difference across all languages"
        emoji_proportions = {}
        all_emojis = set()

        for lang in self.langs:
            counts = Counter()
            for emojis, _ in self.lang_emoji[lang]:
                counts.update(set(emojis))

            total_tweets = len(self.lang_emoji[lang])
            if total_tweets > 0:
                emoji_proportions[lang] = {
                    e: count / total_tweets for e, count in counts.items()
                }
            else:
                emoji_proportions[lang] = {}
            all_emojis.update(counts.keys())

        diffs = []
        for emoji_char in all_emojis:
            props = [emoji_proportions[lang].get(emoji_char, 0) for lang in self.langs]
            diff = max(props) - min(props)
            max_idx = props.index(max(props))
            diffs.append((emoji_char, diff, max_idx))

        diffs.sort(key=lambda item: item[1], reverse=True)

        fig, ax = plt.subplots()
        colors = [f"C{i}" for i in range(len(self.langs))]
        state = {"start_index": 0}

        def update(event=None):
            if event is not None:
                state["start_index"] += k
                if state["start_index"] >= len(diffs):
                    state["start_index"] = 0

            idx = state["start_index"]
            current_data = diffs[idx : idx + k]

            if not current_data:
                state["start_index"] = 0
                idx = 0
                current_data = diffs[0:k]

            x = [item[0] for item in current_data]
            y = [item[1] for item in current_data]
            color_indices = [item[2] for item in current_data]
            bar_colors = [colors[i] for i in color_indices]

            ax.clear()
            bars = ax.bar(x, y, color=bar_colors)
            ax.bar_label(bars)
            ax.set_title(
                f"Top {k} Different Emoji (Rank {idx + 1}-{idx + len(current_data)})"
            )

            handles = [
                mpl.patches.Rectangle((0, 0), 1, 1, color=colors[i])
                for i in range(len(self.langs))
            ]
            ax.legend(handles, self.labels, loc="upper right")
            fig.canvas.draw()

        update()
        fig.canvas.mpl_connect("button_press_event", update)

        plt.savefig(f"./{self.graph_dir}/top_{k}_emoji.png")
        plt.show()

    def plot_multiple_specific(self, specific: list[str]) -> None:
        "plots multiple specific emoji in the same image"
        counts_list = []
        for em in specific:
            counts_list.append(self.percent_with_specific_emoji(em))

        fig, axs = plt.subplots(1, len(specific))
        if len(specific) == 1:
            axs = [axs]

        for i, ax in enumerate(axs):
            ax.set_title(f"Number of {specific[i]}")
            bars = ax.bar(self.labels, counts_list[i], color=self.colors)
            ax.bar_label(bars)

        names = [self.emoji_name(em) for em in specific]
        plt.tight_layout()
        plt.savefig(f"./{self.graph_dir}/specific_{'_'.join(names)}.png", dpi=400)
        plt.show()


def main():
    data = Data()
    # print(len(data.lang_data["en"]))  # 500000
    # print(len(data.lang_data["it"]))  # 500000
    # data.percent_with_emoji()  # SANITY CHECK
    # data.percent_with_specific_emoji(emoji.emojize(":thumbs_up:"))
    # data.top_emoji(10)
    data.handshape_emoji()
    data.emoji_per_character()
    # data.get_random_tweet_with_emoji("en")
    # data.get_random_tweet_with_emoji("it")
    # data.type_token_analysis()
    # data.plot_type_data(300)
    # data.get_most_different(10)
    # emojis = [
    #     emoji.emojize(":pinched_fingers:"),
    #     emoji.emojize(":OK_hand:"),
    #     emoji.emojize(":sign_of_the_horns:"),
    # ]
    # print(emojis)
    # data.plot_multiple_specific(emojis)


if __name__ == "__main__":
    main()

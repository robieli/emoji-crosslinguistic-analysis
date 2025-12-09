import os
import numpy as np
import emoji
import csv
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.font_manager import findfont, FontProperties, fontManager
import re
from datasets import load_from_disk


def extract_single_emoji(text: str) -> list:
    parsed = emoji.analyze(text)
    output = []
    for token in parsed:
        output.append(token.chars)
    return output


def extract_compound_emoji(text: str) -> list:
    parsed = emoji.analyze(text)
    output = []
    length = 0
    for token in parsed:
        output.append(token.chars)
        length += 1

    # for i in range(1, length):
    #     if parsed[i].value.start == parsed[i - 1].value.end:
    #         print("YIPPEE")
    return []


def normalize_emoji(text: str) -> str:
    text = re.sub(
        r"(_(light|medium-light|medium|medium-dark|dark)_skin_tone)", "", text
    )
    if text[0] != ":" or text[-1] != ":":
        return text
    return text[1:-1]


def main():
    with open("handshape_emoji.csv", "r", newline="") as f:
        reader = csv.reader(f)
        handshape_emoji = next(reader)

    handshape_emoji = set(handshape_emoji)

    # data setup
    langs = ["en", "it"]
    data = {}
    for lang in langs:
        if lang == "en":
            data[lang] = [
                [":thumbs_up:", ":red_heart:"],
                [":palm_up_hand_dark_skin_tone:"],
            ]
        elif lang == "it":
            data[lang] = [
                [":green_heart:", ":white_heart:", ":red_heart:"],
                [":pinched_fingers_medium_skin_tone:"],
            ]

    # sanity check
    print("Sanity Check")
    for lang in langs:
        for text in data[lang]:
            print(text)
    print()
    print(handshape_emoji)
    print()

    # setup plot
    plt.figure()
    y = np.zeros(len(langs))
    # data processing
    for i, lang in enumerate(langs):
        count = 0
        for emojis in data[lang]:
            emojis = [normalize_emoji(item) for item in emojis]
            emojis = set(emojis)
            print(emojis)
            common = emojis.intersection(handshape_emoji)
            print(common)
            if common:
                count += 1
        y[i] = count / len(data[lang])

    plt.bar(langs, y)
    plt.show()


if __name__ == "__main__":
    # main()
    for i in range(5):
        type = input()
        valid = ["p", "r", "n"]
        if type not in valid:
            print("NOT VALID")
        else:
            print("VALID")

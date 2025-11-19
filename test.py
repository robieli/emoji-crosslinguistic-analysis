import numpy as np
import emoji
import csv


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


if __name__ == "__main__":
    text = emoji.demojize("❤️")
    print(text)
    # extracted = extract_single_emoji(text)
    # print(extracted)
    # en_emojis = [(extracted, 0)]
    # lang = "en"
    # # print(extract_compound_emoji(text))
    # file = lang + "_emojis.csv"
    # with open(file, "w", newline="") as f:
    #     writer = csv.writer(f)
    #     writer.writerows(en_emojis)
    #
    # try:
    #     with open(file, "r", newline="") as f:
    #         reader = csv.reader(f)
    #         for row in reader:
    #             print()
    #             break
    # except FileNotFoundError:
    #     print("error")

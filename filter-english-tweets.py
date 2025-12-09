from datasets import load_dataset, Dataset
import pandas as pd


def main():
    size = 500000
    file = "emojitweets-01-04-2018.txt"
    data = pd.read_csv(file)

    dataset = Dataset.from_pandas(data)
    dataset = dataset.select(range(size))
    print(len(dataset))
    print(dataset["text"][0])
    dataset.save_to_disk("../en_data")


if __name__ == "__main__":
    main()

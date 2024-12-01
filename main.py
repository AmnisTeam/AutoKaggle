import os
from kaggle.api.kaggle_api_extended import KaggleApi
from src.kaggle_dataset import KaggleDataset

config = "kaggle.json"

if __name__ == "__main__":
    api = KaggleApi()
    api.config = config
    api.authenticate()

    test_dataset = KaggleDataset(api, "test-dataset123123", "spectrespect")
    test_dataset.upload_dataset("src")

import os
import json
from kaggle.api.kaggle_api_extended import KaggleApi
import tempfile
import shutil
import uuid
import gc

class KaggleDataset():
    def __init__(self, api: KaggleApi, dataset_name: str, user_name: str, license: str = "CC0-1.0"):
        self.api = api
        self.dataset_name = dataset_name
        self.user_name = user_name
        self.license = license

        self.dataset_metadata = {
            "title": dataset_name,
            "id": f"{user_name}/{dataset_name}",
            "licenses": [{"name": license}]
        }
    

    def upload_dataset(self, local_folder_path: str, version_message: str = "Updated dataset with new files"):
        """
            Creates or (if it already exists) uploads a dataset to Kaggle.

            local_folder_path - Path to the local folder with the dataset, 
            which will be uploaded to Kaggle
        """

        local_folder_path = os.path.normpath(local_folder_path)

        # create a temp archive with dataset files
        unique_archive_folder_name = str(uuid.uuid4())
        archive_folder_path = os.path.join(tempfile.gettempdir(), unique_archive_folder_name)
        os.makedirs(archive_folder_path, exist_ok=True)

        # create a metadata file
        metadata_file_path = os.path.join(archive_folder_path, "dataset-metadata.json")
        with open(metadata_file_path, "w") as file:
            json.dump(self.dataset_metadata, file, indent=4)
   
        local_folder_parent = os.path.dirname(local_folder_path)
        local_folder_name = os.path.basename(local_folder_path)
        archive_path = os.path.join(archive_folder_path, self.dataset_name)
        shutil.make_archive(archive_path, "zip", "./" + local_folder_parent, local_folder_name)

        archive_path = archive_path + ".zip" # because initially archive_path don't have extension

        datasets = self.api.datasets_list(user=self.user_name)
        if not self.dataset_metadata["id"] in map(lambda x: x["ref"], datasets):
            # Dataset does not exist -> create them
            ret = self.api.dataset_create_new(archive_folder_path, dir_mode="skip", public=True)
        else:
            # Dataset exists -> update them
            ret = self.api.dataset_create_version(archive_folder_path, version_message, dir_mode="skip", delete_old_versions=True)
        
        gc.collect()
        shutil.rmtree(archive_folder_path)
        assert not ret.hasError, ret.error

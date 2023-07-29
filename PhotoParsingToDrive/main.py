import requests
import os

from typing import List
from pandas import read_excel
from PIL import Image
from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth

TEAM_DRIVE_ID = '1PfznI0LCOKGLFHmBEZTefYXP0s-RtV3s'
PARENT_FOLDER_ID = '1JdvIA2Tto9kxbY7PlW3rOeINOMV3Rzbi'

def create_invalid_images_file(invalid_images: tuple):
    with os.open('./invalid_images.txt', 'wb') as file:
        for invalid_image in invalid_images:
            index, url = invalid_image
            file.write("Index: {0} -> Invalid URL: {1}\n".format(index, url))

def setup_google_drive_for_uploading() -> GoogleDrive:
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    return GoogleDrive(gauth)

def upload_to_google_drive(drive, path: str):
    file = drive.CreateFile({
        'title': path.split('/')[1],
        'parents': [{
            'kind': 'drive#fileLink',
            'teamDriveId': TEAM_DRIVE_ID,
            'id': PARENT_FOLDER_ID
        }]
    })
    file.SetContentFile(path)
    file.Upload(param={'supportsTeamDrives': True})
    file = None

def download_images(image_data: List[tuple]) -> List[tuple]:
    # Complete the relevant authorization tasks for Google Drive access
    drive = setup_google_drive_for_uploading()

    invalid_images = []
    for index, data in enumerate(image_data):
        print("Started processing image {0}".format(index))

        # Get the url content
        url, project_id = data
        content = requests.get(url, allow_redirects=True).content

        # Save the image locally
        file_path = './{0}_{1}.jpg'.format(project_id, index)
        open(file_path, 'wb').write(content)
        
        try:
            # Validate image with Image.open which throws an error if not valid
            Image.open(file_path)

            # Upload the image to Google Drive
            upload_to_google_drive(drive, file_path)

            print("Finished processing image {0}".format(index))
        except IOError:
            invalid_images.append((index, url))
            print("Failed processing image {0}".format(index))
        
        # Delete the local image
        os.remove(file_path)
        
    return invalid_images

def parse_image_urls(data_path: str) -> List[tuple]:
    data = read_excel(data_path)

    image_data = []
    for row in data.index:
        image_data.append((data['Image_large_size'][row], data['Project_id'][row]))

    return image_data

if __name__ == '__main__':
    data_path = './data.xlsx'
    image_data = parse_image_urls(data_path)
    invalid_images = download_images(image_data)
    create_invalid_images_file(invalid_images)

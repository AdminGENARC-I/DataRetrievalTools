import requests
import os
import validators

from typing import List
from pandas import read_excel
from PIL import Image
from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth

TEAM_DRIVE_ID = '1eQPIczWLji6qtoXWE55KVZko8l2-Ttai'
CATEGORY_FOLDER_IDS = {
    'Aerial': '1z69FwfhnE6K-LQUllddaIxAU2RBoUwa3',
    'Drawing': '19-U4I7lcVGMgdY4JH2Ugzw2cnes0TluO',
    'Interior': '1UuSDFKPrtuANe58IsE604BI0A9Zwscuc',
    'Exterior': '1CHl0eUFsGE8kNZkobk3q5VdVr3GPgcP-',
}

def setup_google_drive_for_uploading() -> GoogleDrive:
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    return GoogleDrive(gauth)

def upload_to_google_drive(drive, folder: str, path: str):
    file = drive.CreateFile({
        'title': path.split('/')[1],
        'parents': [{
            'kind': 'drive#fileLink',
            'teamDriveId': TEAM_DRIVE_ID,
            'id': CATEGORY_FOLDER_IDS[folder]
        }]
    })

    file.SetContentFile(path)
    file.Upload(param={'supportsTeamDrives': True})
    file = None

def download_images(image_data: List[tuple]) -> List[tuple]:
    with open('./invalid_images.txt', 'w') as invalid_images_file:
        # Complete the relevant authorization tasks for Google Drive access
        drive = setup_google_drive_for_uploading()
    
        for index, data in enumerate(image_data):
            index = index
            print("Started processing image {0}".format(index))
    
            # Get the url content
            url, project_id, project_category = data
            if validators.url(url):
                content = requests.get(url, allow_redirects=True).content

                # Save the image locally
                file_path = './{0}_{1}.jpg'.format(project_id, index)
                open(file_path, 'wb').write(content)

                try:
                    # Validate image with Image.open which throws an error if not valid
                    Image.open(file_path)

                    # Upload the image to Google Drive if not Delete
                    if project_category in CATEGORY_FOLDER_IDS:
                        upload_to_google_drive(drive, project_category, file_path)

                    print("Finished processing image {0}".format(index))
                except IOError:
                    invalid_images_file.write("Index: {0} -> Invalid URL: {1}\n".format(index, url))
                    print("Failed processing image {0}".format(index))

                # Delete the local image
                os.remove(file_path)

def parse_image_urls(data_path: str) -> List[tuple]:
    data = read_excel(data_path)

    image_data = []
    for row in data.index:
        image_data.append((data['Image_large_size'][row], data['Project_id'][row], data['manual_category'][row]))

    return image_data

if __name__ == '__main__':
    data_path = './data.xlsx'
    image_data = parse_image_urls(data_path)
    download_images(image_data)

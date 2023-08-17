import requests
import os

from typing import List
from pandas import read_excel
from PIL import Image
from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth

TEAM_DRIVE_ID = '1PfznI0LCOKGLFHmBEZTefYXP0s-RtV3s'
CATEGORY_FOLDER_IDS = {
    'Cultural Architecture': '1LMUMeKYOhStB_cC1y4SNkM5xAdy0BzQx',
    'Healthcare Architecture': '11F39CLte4vlTjlh8P7om1OmeAXOY75CH',
    'Landscape & Urbanism': '1hSY2nCIhTliTNAvQSBCCTaHiq644Egrj',
    'Religious Architecture': '139Ljhkbxtv8urmxh19rcuVMmfPaAY7Qi',
    'Educational Architecture': '1Pjzzpue6biWh9pjOuf3HCdqbhmdW23dN',
    'Industrial & Infrastructure': '1pHjLLlj9-8zPgRZKmCWOkW3FU2idJIhn',
    'Hospitality Architecture': '1TkBSgdbmF8QGf8lXktFMnL59n7l_eB_2',
    'Public Architecture': '1_72IZocWeqzDoq6c79g3VtWV2Z3yBEfI',
    'Mixed Use Architecture': '1ll5zQ__5IBIAtUAC54rlOXFoG9KMK4_Y',
    'Sports Architecture': '19qDSG5SIw91aj9Wn3BL_eLQHE5X2__BL',
    'Residential Architecture': '1tLi1fAvhYK_Q_r3OQ1gWcX_JMN8O71Q3',
    'Urbanism': '1bDwUZRN0PAqDk4qJWC5wZjzq-nwklEXh',
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
    with open('./invalid_images.txt', 'wb') as invalid_images_file:
        # Complete the relevant authorization tasks for Google Drive access
        drive = setup_google_drive_for_uploading()
    
        for index, data in enumerate(image_data):
            print("Started processing image {0}".format(index))
    
            # Get the url content
            url, project_id, project_category = data
            content = requests.get(url, allow_redirects=True).content
    
            # Save the image locally
            file_path = './{0}_{1}.jpg'.format(project_id, index)
            open(file_path, 'wb').write(content)
            
            try:
                # Validate image with Image.open which throws an error if not valid
                Image.open(file_path)
    
                # Upload the image to Google Drive
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
        image_data.append((data['Image_large_size'][row], data['Project_id'][row], data['Project_category_0'][row]))

    return image_data

if __name__ == '__main__':
    data_path = './data.xlsx'
    image_data = parse_image_urls(data_path)
    download_images(image_data)

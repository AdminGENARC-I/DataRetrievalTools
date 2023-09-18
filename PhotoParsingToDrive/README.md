# Photo Parsing to Google Drive
This script is used to download all the images provided in the `data.xlsx` file and upload them to the Google Drive: https://drive.google.com/drive/u/1/folders/1nkHQ-7wis0yuvaXAn6i7axzYsToxaAbR

Here are important reminders:
- Don't forget to install Python3 and PIP from `https://www.python.org/downloads/`
- Don't forget to `pip install pandas && pip install openpyxl && pip install pydrive && pip install validators`
- Don't forget to setup `client_secrets.json` to be able to access Google Drive. Here are the instructions: https://pythonhosted.org/PyDrive/quickstart.html#authentication which you should do so with the admin GENARC-I email

Step by step how to guide:
- Step 1: After completing the reminders above, clone this repository by following the instructions on this link: https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository
- Step 2: Open a terminal and navigate into `PhotoParsingToDrive` folder
- Step 3: Run the script via `python3 main.py`
- Step 4: You can observe the progress on the terminal and Google Drive at the same time
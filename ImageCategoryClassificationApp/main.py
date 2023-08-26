import gspread
from oauth2client.service_account import ServiceAccountCredentials
from PIL import Image, ImageTk
import requests
import tkinter as tk
from tkinter import ttk
from io import BytesIO

OPTIONS = ["Exterior", "Interior", "Aerial", "Drawing", "DELETE"]

# Set up Google Sheets API credentials
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(credentials)

# Open the Google Sheet
sheet = client.open('GENARCI DEMO').sheet1

# Get all values in the image URL column
image_urls = sheet.col_values(30)

# Create GUI window
root = tk.Tk()
root.geometry('600x600')
root.title("GENARC-I Image Categorization Tool")

# GUI variables
choice_var = tk.StringVar()
start_index_var = tk.StringVar(value="0")  # Default start index

# Function to display the next image
def display_image():
    start_index = int(start_index_var.get())
    if start_index < 0:
        start_index = 0
    
    start_index = start_index + 1 # Added to pass first two rows
    
    if start_index < len(image_urls):
        url = image_urls[start_index]
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        img = img.resize((400, 400))  # Resize image for display
        img_tk = ImageTk.PhotoImage(img)
        image_label.config(image=img_tk)
        image_label.img_tk = img_tk
    else:
        image_label.config(text="All images processed.")

# Function to record user choice and update Google Sheet
def record_choice():    
    sheet.update_cell(int(start_index_var.get()) + 2, 33, OPTIONS[int(choice_var.get()) - 1])  # Adding 1 because of header row
    choice_var.set('0')
    start_index_var.set(str((int(start_index_var.get())) + 1))

# Create GUI elements
start_frame = ttk.Frame(root)
start_frame.pack(padx=20, pady=5)

ttk.Label(start_frame, text="Start Index:").pack(side="left")
start_index_entry = ttk.Entry(start_frame, textvariable=start_index_var, width=5)
start_index_entry.pack(side="left", padx=5)

start_button = ttk.Button(start_frame, text="Start", command=lambda:[start_button.pack_forget(), display_image()])
start_button.pack(pady=10)

image_label = ttk.Label(root, text="Click 'Start' to start.", font=("Helvetica", 12))
image_label.pack(padx=20, pady=20)

option_frame = ttk.Frame(root)
option_frame.pack(padx=20, pady=10)
for idx, option in enumerate(OPTIONS):
    if idx == 4:
        ttk.Radiobutton(option_frame, text=option, variable=choice_var, value=str(idx+1)).grid(row=1, column=1, padx=5)
    else:
        ttk.Radiobutton(option_frame, text=option, variable=choice_var, value=str(idx+1)).grid(row=0, column=idx, padx=5)

next_button = ttk.Button(root, text="Next", command=lambda: [record_choice(), display_image()])
next_button.pack(pady=10)

root.mainloop()

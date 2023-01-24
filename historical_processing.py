import pandas as pd
import os
import cv2
import pytesseract

#Loads dataframe while dropping any errors or blank rows

df_chat = pd.read_csv(r'whatsapp/Text/_chat.txt', sep = ']',
                      error_bad_lines=False, names= ["Timestamp","Text"])

df_chat.dropna(inplace=True)

# Filters out rows that don't have images in

df_chat = df_chat[df_chat['Text'].str.contains("attached")]

# Creates user column from the first word in text column

df_chat[['User', 'Text']] = df_chat['Text'].str.split(':',n=1, expand=True)

# Renames columns and does some trimming to leave just the filename

df_chat= df_chat.rename(columns={'Text' : 'Filename'})
df_chat['Timestamp'] = df_chat['Timestamp'].str.replace('[' , '')
df_chat['Timestamp'] = df_chat['Timestamp'].str.replace(',' , '')
df_chat['Filename'] = df_chat['Filename'].str.replace('<attached: ' , '')
df_chat['Filename'] = df_chat['Filename'].str.replace('>' , '')

df_chat_cleaned = df_chat.copy()

## Image text extraction

pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
mydir = r'C:\Users\tomwh\PycharmProjects\Plusword\whatsapp\Images'

# loop to generate a list of filenames and a list of text from images

filename_list=[]
text_list = []

for files in os.listdir(mydir):
    img = cv2.imread(r'C:\Users\tomwh\PycharmProjects\Plusword\whatsapp\Images\\' + files)
    text=pytesseract.image_to_string(img)
    filename_list.append(os.fsdecode(files))
    text_list.append(text)

# Creates dataframe from the two lists

df_image_text_raw=pd.DataFrame({'Filename': filename_list, "Text": text_list})

## image text cleaning

df = df_image_text_raw.copy()

# Separates out times from text columns and then removes \n from text to make more readable

df["Time"] = df["Text"].str.extract(r'(PlusWord in\n\n[\d+][\d+]:[\d+][\d+])')
df["Text"] = df["Text"].replace(r'\n',' ', regex=True)

# Creates dataframe of errored rows and drops them from the main df

df_image_error=df[df["Time"].isna()]
df = df.dropna()

# strips text from time column and adds hour column to time before converting to datetime format

df["Time"] =df["Time"].str.replace(r"PlusWord in\n\n", "")
df['Time'] = '00:' + df['Time'].astype(str)
df["Time"] = pd.to_datetime(df["Time"], format ='%H:%M:%S')

df_image_text_clean = df.copy()

##join

# Reconnects df_image_text_clean to df_image_error before stripping special characters and setting index to filename

df_image_combined = df_image_text_clean.append(df_image_error)
df_image_combined.replace({r'[^\x00-\x7F]+':''}, regex=True, inplace=True)
df_image_combined["Filename"] = df_image_combined["Filename"].astype(str)
df_image_combined = df_image_combined.set_index('Filename')

# Special characters and leading spaces are stripped from df_chat and filename is set to index

df_chat.replace({r'[^\x00-\x7F]+':''}, regex=True, inplace=True)
df_chat["Filename"] = df_chat["Filename"].str.lstrip()
df_chat["Filename"] = df_chat["Filename"].astype(str)
df_chat = df_chat.set_index('Filename')

# Left join is done on df_image_combined so only rows that have a plusword screenshot image associated with them are
# kept. I deleted all the images that weren't screenshots out before processing.

df_combined = df_image_combined.merge(df_chat, how='left', on='Filename')

# Oli gets his name added to his rows and User and Timestamp have their datatypes fixed

df_combined["User"] = df_combined["User"].str.replace('\+447400975974', 'Oli')
df_combined["User"] = df_combined["User"].astype('category')
df_combined["Timestamp"] = pd.to_datetime(df_combined["Timestamp"], format ='%d/%m/%Y %H:%M:%S')

#df_combined.to_csv('munged.csv', index=False)

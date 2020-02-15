# Phonebook Project
This is an ultra secure phonebook for all the data you wish to contain about people. It features tagging, multiple filtering options, links to the most important websites, automated messenger messaging and much more.

## Installation
The project is currently in a portable version, meaning it does not install itself on your computer. To launch the app simply execute the main.py file in the main project directory.
  
## Security
The app takes a photo of every person launching an app via built-in webcam. It features image recognition so that the phonebook owner does not get notified about his own app launches. Each taken photo is encrypted so that they can be viewed only after entering the app, and photos are checked for tampering with them/deleting part of them. The app itself does not send any data into the web, except for facebook calls.

## Usage
### Launching the app
After launching an app you will be presented with a password dialog:

![Screenshot of password dialog](https://github.com/barci2/phonebook/blob/master/screenshots/password.png)

The default password for the app is xyz, which can be changed later. Launching the app may take a while, and in case of security breach attempts the user will be notified of them and photos of deliquents will be presented. 

### Basic usage
After the entering the app the user will be presented with the following screen:

![Screenshot of main window](https://github.com/barci2/phonebook/blob/master/screenshots/phonebook.png)

Entries may be selected with a single-click <+ctrl> on them which will result in them highlighting and number of selected entries showing on the top. Doublie-clicking on an entry will result in showing the "Additional Data" box. Entries may be filtered by clicking any of the tags including the ones next to person's name, typing their name in the search bar or clicking at the top person rating filter. Clicking on a linkedin/research gate/messenger icon next to the person's name will result in opening the corresponding site in browser (keep in mind that an icon will appear only after entering a proper web link into the person's data). Using one of the buttons on the top will result in the following (counting from the left):
.* Adding new entry (a dialog will be show)
.* Opening automatic message creator (at least one entry must be selected, a login dialog will be shown the first time you want to sign in after launching the app)
.* Opening password modification dialog
.* Opening self-timed camera for the face recognition

### Editing entry
After adding an entry user may modify it by clicking the pencil icon next to the person's name, after which a following dialog will be shown:

![Screenshot of edit dialog](https://github.com/barci2/phonebook/blob/master/screenshots/edit.png)

User may change the name, phone number (default country is Poland, you may change it in phonebook_lib/base/constants.py according to the phonenumbers module), email (must be a proper email address), linkedin, research gate and messenger links (must be the whole page address), quality of the entry, level of acquaintance or tags(adding by typing them in the line edit, deleting by clicking them)

## Dependencies
Install the dependencies by typing in:

pip3 install pysqlcipher3 phonenumbers cryptography numpy cv2 face_recognition face_recognition_models sortedcontainers Unidecode PyQt5

Also, for proper fonts, you will need to install ttf-montserrat font.

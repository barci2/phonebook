from pathlib import *

tab_size=6

db_file=Path("./data/phonebook.sqlite")

images_db_directory=Path("./data/.images_db/")

icon_directory=Path("./data/icons/")

application_icon_file=icon_directory.joinpath("phonebook.png")
new_item_icon_file=icon_directory.joinpath("new.png")
edit_item_icon_file=icon_directory.joinpath("edit.png")
delete_item_icon_file=icon_directory.joinpath("delete.png")
alert_icon_file=icon_directory.joinpath("alert.png")
question_icon_file=icon_directory.joinpath("question.png")
linkedin_icon_file=icon_directory.joinpath("linkedin.png")
researchgate_icon_file=icon_directory.joinpath("researchgate.png")
messenger_icon_file=icon_directory.joinpath("messenger.png")
key_icon_file=icon_directory.joinpath("key.png")
camera_icon_file=icon_directory.joinpath("camera.png")
rating_icon_file=icon_directory.joinpath("rating.png")
acquaintance_icon_file=icon_directory.joinpath("acquaintance.png")

camera_image_dims=(720,1280,3)
sneaky_photos_directory=Path.cwd().joinpath(Path("./data/.imgcaptures/"))
public_key_file=Path("./data/pubkey.txt")
fernet_key_length=1024
hash_file_name="images_hash.txt"
date_length=5

screen_dims=(1920,1080)

phone_default_region="PL"

max_rating=5
default_rating=1
acquaintance_levels=["Nonexistent", "Poor", "Medium", "Good", "Perfect"]
max_acquaintance=len(acquaintance_levels)

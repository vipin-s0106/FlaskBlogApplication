import os
import secrets
from PIL import Image
from flaskblog import app


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _,f_ext = os.path.splitext(form_picture.filename)
    #print(f_ext)
    picture_fn = random_hex + f_ext
    #print(picture_fn)
    picture_path = os.path.join(app.root_path,'static\profilepics',picture_fn)
    #print(picture_path)
    
    #resizing image before save it
    output_size = (320,320)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn
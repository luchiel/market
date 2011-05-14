import os
from hashlib import md5
from PIL import Image

IMAGE_PATH = 'media/img/'
MAX_SIZE = 400

def save_image(i):
    hash = md5()
    map(hash.update, i.chunks())
    iname = IMAGE_PATH + hash.hexdigest() + '.' + i.name.rpartition('.')[2]
    with open(iname, 'wb+') as dest:
        map(dest.write, i.chunks())    
    
    img = Image.open(iname)
    if img.size[0] > img.size[1]:
        w = MAX_SIZE
        h = w * img.size[1] / img.size[0]
    else:
        h = MAX_SIZE
        w = h * img.size[0] / img.size[1]
    img = img.resize((w, h))
    img.save(iname)

    return iname


def remove_image(i):
    if i != '' and os.path.exists(os.getcwd() + '/' + i):
        os.remove(os.getcwd() + '/' + i)

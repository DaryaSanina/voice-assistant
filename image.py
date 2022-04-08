from PIL import Image

USER_IMAGE_SIZE = 48, 48


def resize_image(file):
    image = Image.open(file)
    image.thumbnail(USER_IMAGE_SIZE, Image.ANTIALIAS)
    image.save(file, 'PNG')


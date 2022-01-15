import base64
from PIL import Image
from io import BytesIO


image = open('data/333.jpg', 'rb')
image_read = image.read()
image_64_encode = base64.b64encode(image_read)
print(image_64_encode)
im_str = image_64_encode.decode()
print(im_str)
#
#im_byte = im_str.encode()
image_64_decode = base64.decodebytes(image_64_encode)
bytes_io = BytesIO(image_64_decode)
watermark = Image.open('data/watermark.jpg')
base_image = Image.open(bytes_io)
width, height = base_image.size
transparent = Image.new('RGBA', (width, height), (0, 0, 0, 0))
w = watermark.resize((width, height))
transparent = Image.blend(base_image, w, 0.2)
transparent.show()

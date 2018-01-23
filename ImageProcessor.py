import base64, os
from Util import Coordinate
from PIL import Image, ImageEnhance, ImageFilter

class ImageProcessor:

    def __init__(self, path):
        self.path = path
        self.raw_img = Image.open(path)
        self.width, self.height = self.raw_img.size
        self.resize_size = 1500.0
        self.file_size = os.stat(self.path).st_size
        self.max_file_size = 4000000

    def crop_image(self, c1, c2):
        return self.raw_img.crop((c1.x, c1.y, c2.x, c2.y))

    def check_size(self):
        return self.file_size > self.max_file_size

    def save_temp(self):
        self.raw_img.save("temp_" + self.path)

    def delete_temp(self):
        os.remove("temp_" + self.path)

    def get_temp_path(self):
        return "temp_" + self.path

    def get_contrast(self, im):
        im_matrix = im.load()
        black = 0

        for r in range(im.width):
            for c in range(im.height):
                if im_matrix[r, c] < 128:
                    black += 1

        return float(black) / float(im.height * im.width)

    def resize(self):
        factor = 0

        if self.width > self.height:
            factor = float(self.width)/self.resize_size
        else:
            factor = float(self.height)/self.resize_size

        self.raw_img = self.raw_img.resize((int(float(self.width)/factor), int(float(self.height)/factor)))
        self.width, self.height = self.raw_img.size

    def enhance_image(self):
        self.raw_img = self.raw_img.convert('L')
        self.raw_img = ImageEnhance.Contrast(self.raw_img).enhance(1.95)
        self.raw_img = ImageEnhance.Sharpness(self.raw_img).enhance(1.15)
        #self.raw_img = self.raw_img.filter(ImageFilter.UnsharpMask(percent=105))

    def encode(self, path):
        with open(path, "rb") as img:
            return base64.b64encode(img.read())

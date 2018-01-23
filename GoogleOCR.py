import requests, json, math, numpy
from Util import Coordinate
from ImageProcessor import ImageProcessor
from PIL import Image, ImageDraw

class OCRLine:

    def __init__(self, words, c1, c2, c3, c4, contrast, page_width, page_height):
        self.page_width = page_width
        self.page_height = page_height
        self.page_center = page_width / 2.0
        self.c1 = c1
        self.c2 = c2
        self.c3 = c3
        self.c4 = c4

        self.words = words
        self.contrast = contrast
        self.area = Coordinate.get_distance(self.c1, self.c2) * Coordinate.get_distance(self.c2, self.c3)
        self.line_center = float(self.c1.x + self.c2.x) / 2.0

        #large medium small
        self.type = "large"

    def compute_formatting(self, page_height, page_area, page_indent, page_spacing, line_spacing):
        self.is_centered_confidence = math.fabs((self.page_center - self.line_center) / self.page_center)
        self.is_centered = self.is_centered_confidence < 0.075
        print "is centered conf: " + str(self.is_centered_confidence)
        print "is centered: " + str(self.is_centered)

        self.is_indented_confidence = math.fabs((page_indent - self.c1.x) / page_indent)
        self.is_indented = self.is_indented_confidence > 0.50
        print "is indent conf: " + str(self.is_indented_confidence)
        print "is indent: " + str(self.is_indented)

        self.type_confidence = math.fabs((page_height - (self.c1.y - self.c4.y)) / page_height)
        if self.type_confidence > 0.50:
            self.type = "large"
        elif self.type_confidence > 0.20:
            self.type = "medium"
        else:
            self.type = "small"
        print "type conf: " + str(self.type_confidence)
        print "type: " + self.type

        self.is_end_paragraph_confidence = math.fabs((page_spacing - line_spacing) / page_spacing)
        self.is_end_paragraph = self.is_end_paragraph_confidence > 0.20
        print "end paragraph: " + str(self.is_end_paragraph)

        print "\n"

class OCRBlock:

    def __init__(self, word, x1, y1, x2, y2, x3, y3, x4, y4):
        self.word = word
        self.c1 = Coordinate(x1, y1)
        self.c2 = Coordinate(x2, y2)
        self.c3 = Coordinate(x3, y3)
        self.c4 = Coordinate(x4, y4)
        self.area = Coordinate.get_distance(self.c1, self.c2) * Coordinate.get_distance(self.c2, self.c3)

    def set_contrast(self, contrast):
        self.contrast = contrast

    def compute_formatting(self, page_contrast):
        #is_bold
        pass

class GoogleOCR:

    def __init__(self, path):
        self.path = path
        self.url = "https://vision.googleapis.com/v1/images:annotate"
        self.api_key = "[REDACTED]"
        self.ip = ImageProcessor(path)

    def process_image(self):
        if self.ip.check_size():
            self.ip.resize()
        self.ip.enhance_image()
        self.ip.save_temp()
        self.encoded_img = self.ip.encode(self.ip.get_temp_path())

    def send_ocr_request(self):
        self.payload = json.loads("{\"requests\":[{\"image\":{\"content\":\"" + self.encoded_img + "\"},\"features\":[{\"type\":\"TEXT_DETECTION\"}]}]}")
        self.request = requests.post(self.url, params={"key" : self.api_key}, json=self.payload)

    def get_status_code(self):
        return self.request.status_code

    def get_text(self):
        return self.full_text

    def get_word_array(self):
        return self.word_array

    def get_lines_array(self):
        return self.lines_array

    def compute_median_height(self):
        height_np = numpy.zeros(len(self.lines_array))
        for i in xrange(0, len(self.lines_array) - 1):
            height_np[i] = self.lines_array[i].c1.y - self.lines_array[i].c4.y
        self.median_height = numpy.median(height_np)

    def compute_median_spacing(self):
        spacing_np = numpy.zeros(len(self.lines_array))
        for i in xrange(0, len(self.lines_array) - 1):
            spacing_np[i] = self.lines_array[i + 1].c4.y - self.lines_array[i].c1.y
        self.median_spacing = numpy.median(spacing_np)

    def compute_median_indent(self):
        indent_np = numpy.zeros(len(self.lines_array))
        for i in xrange(0, len(self.lines_array)):
            indent_np[i] = self.lines_array[i].c1.x
        self.median_indent = numpy.median(indent_np)

    #might have to do average instead of median
    def compute_median_contrast(self):
        contrast_np = numpy.zeros(len(self.word_array))
        for i in xrange(0, len(self.word_array)):
            contrast_np[i] = self.word_array[i].contrast
        self.median_contrast = numpy.average(contrast_np)

    def compute_median_area(self):
        areas_np = numpy.zeros(len(self.lines_array))
        for i in xrange(0, len(self.lines_array)):
            areas_np[i] = self.lines_array[i].area
        self.median_area = numpy.median(areas_np)

    def parse_ocr_response(self):
        self.response_data = json.loads(self.request.text)
        text_array = self.response_data["responses"][0]["textAnnotations"]
        text_array_range = len(text_array)
        self.full_text = text_array[0]["description"]

        self.word_array = []
        for i in xrange(1, text_array_range):
            cur_word = text_array[i]
            verts = cur_word["boundingPoly"]["vertices"]
            cur_word_block = OCRBlock(cur_word["description"], verts[0]["x"], verts[0]["y"], verts[1]["x"], verts[1]["y"], verts[2]["x"], verts[2]["y"], verts[3]["x"], verts[3]["y"])
            cropped_word_image = self.ip.crop_image(cur_word_block.c1, cur_word_block.c3)
            cur_word_block.set_contrast(self.ip.get_contrast(cropped_word_image))
            self.word_array.append(cur_word_block)

    def process_ocr_data(self):

        #im = Image.open(self.path)
        #draw = ImageDraw.Draw(im)

        j = 0
        cur_line = []
        self.lines_array = []
        for i in xrange(0, len(self.full_text)):
            if self.full_text[i] == ' ':
                cur_line.append(self.word_array[j])
                j += 1
            elif self.full_text[i] == '\n' or i == len(self.full_text) - 1:
                cur_line.append(self.word_array[j])
                j += 1

                avg_contrast = 0.0
                avg_c1 = Coordinate(cur_line[0].c1.x, 0)
                avg_c2 = Coordinate(cur_line[len(cur_line) - 1].c2.x, 0)
                avg_c3 = Coordinate(cur_line[len(cur_line) - 1].c3.x, 0)
                avg_c4 = Coordinate(cur_line[0].c4.x, 0)

                for k in xrange(0, len(cur_line)):
                    avg_contrast += cur_line[k].contrast
                    avg_c1.sum_y(cur_line[k].c1)
                    avg_c2.sum_y(cur_line[k].c2)
                    avg_c3.sum_y(cur_line[k].c3)
                    avg_c4.sum_y(cur_line[k].c4)

                avg_c1.average_y(len(cur_line))
                avg_c2.average_y(len(cur_line))
                avg_c3.average_y(len(cur_line))
                avg_c4.average_y(len(cur_line))

                #draw.line((avg_c1.x, avg_c1.y, avg_c2.x, avg_c2.y), fill=(255, 0, 0, 128))
                #draw.line((avg_c2.x, avg_c2.y, avg_c3.x, avg_c3.y), fill=(255, 0, 0, 128))
                #draw.line((avg_c3.x, avg_c3.y, avg_c4.x, avg_c4.y), fill=(255, 0, 0, 128))
                #draw.line((avg_c1.x, avg_c1.y, avg_c4.x, avg_c4.y), fill=(255, 0, 0, 128))

                avg_contrast /= len(cur_line)

                self.lines_array.append(OCRLine(cur_line, avg_c1, avg_c2, avg_c3, avg_c4, avg_contrast, self.ip.width, self.ip.height))
                cur_line = []

            #im.save("___hahahah.png")

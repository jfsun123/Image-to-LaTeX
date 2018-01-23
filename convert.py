import json, sys, base64
from GoogleOCR import GoogleOCR
from ImageProcessor import ImageProcessor
from LatexFormat import LatexFormat

def convert(path):
    go = GoogleOCR(path)
    go.process_image()
    go.send_ocr_request()
#    print "Status code: " + str(go.get_status_code()) + "\n"
    if go.get_status_code() == 200:
        go.parse_ocr_response()
        word_array = go.get_word_array()
 #       for i in xrange(0, len(word_array)):
  #          print word_array[i].word + "\tArea: " + str(word_array[i].area) + "\tContrast: " + str(word_array[i].contrast)
   #     print go.get_text()
        go.process_ocr_data()
        lines_array = go.get_lines_array()

        go.compute_median_area()
        go.compute_median_contrast()
        go.compute_median_indent()
        go.compute_median_spacing()
        go.compute_median_height()
        print "median area: " + str(go.median_area)
        print "median contrast: " + str(go.median_contrast)
        print "median indent: " + str(go.median_indent)
        print "median spacing: " + str(go.median_spacing)
        print "median height: " + str(go.median_height)
        print "\n\n"

        for i in xrange(0, len(lines_array) - 1):
            print str(i)
            line_spacing = lines_array[i + 1].c4.y - lines_array[i].c1.y
            lines_array[i].compute_formatting(go.median_height, go.median_area, go.median_indent, go.median_spacing, line_spacing)
        lines_array[len(lines_array) - 1].compute_formatting(go.median_height, go.median_area, go.median_indent, go.median_spacing, go.median_spacing)

        # do the latex stuff here
        latex = LatexFormat(go.get_lines_array())
        d = latex.createLatex()
        d = d.replace('%', "")
        d = d.replace('textbackslash{}', '')
        f = open("textFile.txt", "w+")
        f.write(d.encode('utf-8').strip())
        f.close()

        return base64.b64encode(d.encode('utf-8'))
    else:
        print go.response.text
        return None

#LatexPrinter

"""formats the given words and text into latex format"""

from GoogleOCR import OCRLine
from pylatex import Document, Section, Subsection, Command
from pylatex.utils import italic, bold, NoEscape

class LatexFormat:

	"""self.lines should be of the type OCRLine, has a type and an array of string words

		Use pylatex to convert the string into a latex file"""

	def __init__(self, lines):
		self.lines = lines


	"""the big function"""
	def createLatex(self):
		doc = Document('ImageLatexResult')
		for i in range(len(self.lines)):

			if self.lines[i].type == "large":
				doc.append("\Huge")
			elif self.lines[i].type == "medium":
				doc.append("\LARGE")
			elif self.lines[i].type == "small":
				doc.append("\large")

			if self.lines[i].is_centered:
				doc.append(NoEscape(r'\centerline'))
			elif self.lines[i].is_indented:
				doc.append("\t")

			doc.append(NoEscape(r'{'))
			for k in xrange(0, len(self.lines[i].words)):
				doc.append(self.lines[i].words[k].word)
			doc.append(NoEscape(r'}'))
			doc.append("\n")

			if self.lines[i].is_end_paragraph:
				doc.append(NoEscape(r'\n'))
				doc.append(NoEscape(r'\n'))
				doc.append(NoEscape(r'\n'))

			#if self.lines[i].is_bold:
			#	for k in xrange(0, len(self.lines[i].words)):
 			#		doc.append(bold(self.lines[i].words[k].word))
			#	doc.append("\n")
		return doc.dumps()

# Nippy Text Editor
# Author: Joshua Leung
#         Based on Eli Bendersky's example
#
# First rough prototype

import sys
import os

import PyQt4.QtCore as qcore
import PyQt4.QtGui as qgui
from PyQt4.Qsci import QsciScintilla

from PyQt4.QtGui import QColor, QFont, QFontMetrics

################################################
# Nippy Editor

class NippyEdit(QsciScintilla):
	ARROW_MARKER_NUM = 8
	
	# ctor
	# < fileN: (str) name of file
	# < (path): (str) path to file, including the file name
	def __init__(self, fileN="untitled.txt", path=None, parent=None):
		super(NippyEdit, self).__init__(parent)
		
		# init data fields
		self.fileN = fileN
		self.path = path
		
		self.bookmarks = set()
		
		# make editor sane
		self.setup_ui()
		self.bind_events()
		
		# configure WIP placeholder stuff
		self.temp_init_settings()
		
		# load configuration data
		# TODO
	
	# Setup UI =================================================
	
	# Configure editor
	def setup_ui(self):
		# Set the default font
		font = QFont()
		font.setFamily('Courier')
		font.setFixedPitch(True)
		font.setPointSize(10)
		self.setFont(font)
		self.setMarginsFont(font)

		# Margin 0 is used for line numbers
		fontmetrics = QFontMetrics(font)
		self.setMarginsFont(font)
		self.setMarginWidth(0, fontmetrics.width("0000") + 6)
		self.setMarginLineNumbers(0, True)
		self.setMarginsBackgroundColor(QColor("#dedede"))
		
		# Clickable margin 1 for showing markers
		self.setMarginSensitivity(1, True)
		self.marginClicked.connect(self.on_margin_clicked)
		self.markerDefine(QsciScintilla.RightArrow, self.ARROW_MARKER_NUM)
		self.setMarkerBackgroundColor(QColor("#ee1111"), self.ARROW_MARKER_NUM)
		
		# Brace matching: enable for a brace immediately before or after
		# the current position
		self.setBraceMatching(QsciScintilla.SloppyBraceMatch)
		
		# Current line visible with special background color
		self.setCaretLineVisible(True)
		self.setCaretLineBackgroundColor(QColor("#eeeeee"))
		
		# Indent guides
		#SETINDENTATIONGUIDES
		self.setIndentationGuides(True)
		self.setIndentationGuidesForegroundColor(QColor("#aaaaaa"))
		
		self.setWhitespaceVisibility(QsciScintilla.WsVisible)
		self.setWhitespaceForegroundColor(QColor("#eeeeee"))
		
		# Indent size defaults
		self.setIndentationsUseTabs(True) # XXX: auto-detect - or per-file type
		
		self.setIndentationWidth(4) # used for the size of indent steps - hardcoded to my liking - make this per-file type
		self.setTabWidth(4) # used for the size of tabs - hardcoded to my liking - make this per-file type
		
		self.setAutoIndent(True)
	
	# Initialise placeholder settings
	def temp_init_settings(self):
		from PyQt4.Qsci import QsciLexerPython
		
		# Set Python lexer
		# Set style for Python comments (style number 1) to a fixed-width
		# courier.
		lexer = QsciLexerPython()
		lexer.setDefaultFont(self.font())
		self.setLexer(lexer)
		self.SendScintilla(QsciScintilla.SCI_STYLESETFONT, 1, 'Courier')
		
		# not too small
		#self.setMinimumSize(400, 450)
		self.setMinimumSize(500, 450)
	
	# Event Binding ======================================================
	
	# Bind shortcuts
	def bind_events(self):
		self.keymap = {
			'Ctrl+n'	: self.new_file,
			'Ctrl+o' 	: self.open_file,
			'Ctrl+s'	: self.save_file,
		}
		
		for key, cmd in self.keymap.items():
			shortcut = qgui.QShortcut(qgui.QKeySequence(key), self)
			shortcut.activated.connect(cmd)
	
	# Event Handling =====================================================
	
	# Create a new file
	def new_file(self):
		self.fileN = "untitled.txt"
		self.path = None
		
		self.bookmarks.clear()
		
		self.setText("")
	
	# Open file
	def open_file(self):
		# TODO: warn if existing file is not saved...
		
		# get a file to open
		fname = qgui.QFileDialog.getOpenFileName(self, 'Open file', '.')
		fname = str(fname)
		
		# load the file if valid
		if fname:
			try:
				# load new file
				self.setText(open(fname).read())
				
				self.fileN = os.path.split(fname)[-1]
				self.path = fname
			except:
				print "Oops! Something went wrong when trying to load '%s'" % (fname)
			
	# Save File
	def save_file(self):
		# if file doesn't exist, ask where to save...
		if not (self.path and os.path.exists(self.path)):
			# get filename
			fname = qgui.QFileDialog.getSaveFileName(self, "Save File", 
					"./%s" % (self.fileN),
					"Text/Code Files (*.c, *.h, *.py, *.txt)");
			fname = str(fname)
		else:
			# use saved file's path
			fname = self.path
			
		# write the file if the path is valid
		if fname:
			ff = qcore.QFile(fname)
			if not ff.open(qcore.QIODevice.WriteOnly | qcore.QIODevice.Text):
				return
			
			print qcore.QDir.currentPath(), ff.fileName()
			ok = self.write(ff)
			print ok
	
	
	# Click in margin - For now, this is for bookmarking only
	def on_margin_clicked(self, nmargin, nline, modifiers):
		# Toggle marker for the line the margin was clicked on
		if self.markersAtLine(nline) != 0:
			self.markerDelete(nline, self.ARROW_MARKER_NUM)
			self.bookmarks.remove(nline)
		else:
			self.markerAdd(nline, self.ARROW_MARKER_NUM)
			self.bookmarks.add(nline)


################################################

if __name__ == "__main__":
	app = qgui.QApplication(sys.argv)
	
	editor = NippyEdit()
	editor.show()
	
	app.exec_()

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
	ARROW_MARKER_MASK = 256 # XXX: hardcoded for now - dunno why!
	
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
			# file management
			'Ctrl+N'		: self.new_file,
			'Ctrl+O' 		: self.open_file,
			'Ctrl+S'		: self.save_file,
			
			'F1'			: self.open_file,
			
			# view
			# TODO: normal pluskey doesn't work
			'Ctrl+Plus'		: self.zoomIn,
			'Ctrl+Minus'	: self.zoomOut,
			
			# go to line
			'Ctrl+G'		: self.goto_line_tool,
			
			# go to marker
			'Ctrl+F2'		: self.toggle_bookmark,
			
			'F2'			: self.goto_next_bookmark,
			'Shift+F2'		: self.goto_prev_bookmark,
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
		self.toggle_bookmark(nline)
			
	# Toggle bookmark on line
	# < (line): (int) line number, zero-indexed - current line is used if not provided
	def toggle_bookmark(self, line=None):
		if line is None:
			line = self.getCursorPosition()[0]
		
		if self.markersAtLine(line) != 0:
			self.markerDelete(line, self.ARROW_MARKER_NUM)
			self.bookmarks.remove(line)
		else:
			self.markerAdd(line, self.ARROW_MARKER_NUM)
			self.bookmarks.add(line)
			
			
	# Helper method to go to a line
	# < line: (int) zero-based index for line number to navigate to
	def goto_line(self, line):
		# Find first non-blank on that line
		# NOTE: This shouldn't be too bad, unless the line is too long...
		#       We define "too long" as anything longer than most style guides recommend
		line_text = str(self.text(line))
		
		if len(line_text) < 200:
			offset = len(line_text) - len(line_text.lstrip())
		else:
			offset = 0
		
		# go to that point
		self.setCursorPosition(line, offset)
			
	# Jump to next bookmark
	def goto_next_bookmark(self):
		curLine, curPos = self.getCursorPosition()
		
		# wrap around if we don't go anywhere
		line = self.markerFindNext(curLine + 1, self.ARROW_MARKER_MASK)
		if line == -1:
			line = self.markerFindNext(0, self.ARROW_MARKER_MASK)
			
		self.goto_line(line)
	
	# Jump to previous bookmark
	def goto_prev_bookmark(self):
		curLine, curPos = self.getCursorPosition()
		
		# wrap around if we don't go anywhere
		line = self.markerFindPrevious(curLine - 1, self.ARROW_MARKER_MASK)
		if line == -1:
			line = self.markerFindPrevious(self.lines() - 1, self.ARROW_MARKER_MASK)
		
		self.goto_line(line)
	
	# Tool to go to the specified line
	def goto_line_tool(self):
		curLine, curPos = self.getCursorPosition()
		totLines = self.lines()
		
		# TODO: replace this with a custom dialog
		line, ok = qgui.QInputDialog.getInt(self, "Go To Line...",
						"Current Line: %d / %d" % (curLine + 1, totLines),
						curLine,
						1, totLines)
		
		if ok:
			# NOTE: for display, the numbers start from 1, but the API starts from 0
			self.goto_line(line - 1)
			self.setFocus(True)


################################################

if __name__ == "__main__":
	app = qgui.QApplication(sys.argv)
	
	editor = NippyEdit()
	editor.show()
	
	app.exec_()

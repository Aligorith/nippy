# Nippy Text Editor
# Author: Joshua Leung
#         Based on Eli Bendersky's example
#
# First rough prototype

import sys
import os

import PyQt4.QtCore as qcore
import PyQt4.QtGui as qgui

#from PyQt4.Qsci import QsciScintilla
from PyQt4.Qsci import *

from PyQt4.QtGui import QColor, QFont, QFontMetrics

from nippyedit import filetypes


import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

################################################
# Nippy Editor

# XXX: this should only be a single editor tab, contained within the larger editor
class NippyEdit(QsciScintilla):
	BOOKMARK_MARKER_NUM = 8
	BOOKMARK_MARKER_MASK = 256 # XXX: hardcoded for now - dunno why!
	
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
		font = QFont('Consolas')
		#font.setFamily('Courier')
		font.setFixedPitch(True)
		font.setPointSize(10)
		self.setFont(font)
		self.setMarginsFont(font)

		# Margin 0 is used for line numbers
		fontmetrics = QFontMetrics(font)
		self.setMarginsFont(font)
		self.setMarginWidth(0, fontmetrics.width("0000") + 8)
		self.setMarginLineNumbers(0, True)
		self.setMarginsBackgroundColor(QColor("#dedede"))
		self.setMarginsForegroundColor(QColor("#555555"))
		
		# Clickable margin 1 for showing markers
		self.setMarginSensitivity(1, True)
		self.marginClicked.connect(self.on_margin_clicked)
		self.markerDefine(QsciScintilla.Circle, self.BOOKMARK_MARKER_NUM)
		self.setMarkerBackgroundColor(QColor("#FFD54D"), self.BOOKMARK_MARKER_NUM)
		self.setMarkerForegroundColor(QColor("#BB663D"), self.BOOKMARK_MARKER_NUM)
		
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
		# not too small
		#self.setMinimumSize(400, 450)
		self.setMinimumSize(750, 600)
		
		# set default window title
		self.setWindowTitle("Nippy")
	
	# Event Binding ======================================================
	
	# Bind shortcuts
	def bind_events(self):
		self.keymap = {
			# file management
			'Ctrl+N'		: self.new_file,
			'Ctrl+O' 		: self.open_file,
			'Ctrl+S'		: self.save_file,
			
			'F1'			: self.open_file, # XXX: this should be reserved for our "smart" file opening tool
			
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
			
			# line operations
			'Ctrl+Shift+Up'		: self.move_line_up,
			'Ctrl+Shift+Down'	: self.move_line_down,
		}
		
		for key, cmd in self.keymap.items():
			shortcut = qgui.QShortcut(qgui.QKeySequence(key), self)
			shortcut.activated.connect(cmd)
	
	# Event Handling =====================================================
	
	# File IO ------------------------------------------------------------
	# XXX: this should be done one level up
	# XXX: these need reviewing to ensure that no text munging takes place
	
	# Load specified file
	# < path: (str) path to file to load, including the file name
	def load_file(self, path):
		# load the file...
		if path and os.path.exists(path):
			# load the file if it exists...
			ff = qcore.QFile(path)
			if not ff.open(qcore.QIODevice.ReadOnly):
				# TODO: print warning!
				print "ERROR: Could not open file '%s'" % (path)
				return
			
			#print qcore.QDir.currentPath(), ff.fileName()
			ok = self.read(ff)
			#print ok
			
			# store refs to file
			self.fileN = os.path.split(str(path))[-1]
			self.path  = path
		else:
			# generate an empty file to start from
			self.setText("")
			
			self.fileN = "untitled" # XXX: file number?
			self.path  = None
			
		# clear old data - this shouldn't need to happen, since these should be single-use
		self.bookmarks.clear()
		
		# configure lexer and formatting
		self.detect_language()
	
	# Auto-detect language used, and set lexer + formatting settings accordingly
	def detect_language(self):
		# get filetype stuff...
		ft = filetypes.get_filetype(self.fileN)
		
		if ft:
			# recognised format
			lexer_type = ft.get('lexer', None)
			if lexer_type:
				lexer = lexer_type()
			else:
				lexer = None
			
			do_wrap = ft.get('wrap', False)
		else:
			# unrecognised format
			lexer   = None
			do_wrap = False
			
		
		# set lexer
		if lexer:
			lexer.setDefaultFont(self.font())
			self.setLexer(lexer)
			
			# Set style for comments (style number 1) to a fixed-width courier
			self.SendScintilla(QsciScintilla.SCI_STYLESETFONT, 1, 'Consolas')
		else:
			self.setLexer(None)
			
		# set word-wrapping settings
		if do_wrap:
			self.setWrapMode(QsciScintilla.WrapWord)
		else:
			self.setWrapMode(QsciScintilla.WrapNone)
		
	
	# Create a new file
	def new_file(self):
		self.load_file(None)
		self.setWindowTitle("untitled - Nippy")
	
	# Open file
	def open_file(self):
		# TODO: warn if existing file is not saved...
		
		# get a file to open
		fname = qgui.QFileDialog.getOpenFileName(self, 'Open file', '.')
		
		# load the file if valid
		if fname:
			self.load_file(fname)
			self.setWindowTitle("%s - Nippy" % (self.fileN))
			
	# Save File
	def save_file(self):
		# if file doesn't exist, ask where to save...
		if not (self.path and os.path.exists(self.path)):
			# get filename
			path = qgui.QFileDialog.getSaveFileName(self, "Save File", 
					"./%s" % (self.fileN),
					filetypes.FILETYPES_DLG_FILTER_STR,
					filetypes.FILETYPES_DLG_FILTER_DEFAULT)
		else:
			# use saved file's path
			path = self.path
			
		# write the file if the path is valid
		# TODO: need a way of adding an extra newline at end
		if path:
			ff = qcore.QFile(path)
			if not ff.open(qcore.QIODevice.WriteOnly):
				print "ERROR: Could not open file '%s' for saving" % (path)
				return
			
			#print qcore.QDir.currentPath(), ff.fileName()
			ok = self.write(ff)
			#print ok
			
			# save the new path + filename, since it could be different
			self.fileN = os.path.split(str(path))[-1]
			self.path  = str(path)
			
			# XXX: only do this if something changed...
			self.detect_language()
			
		# update window title
		self.setWindowTitle("%s - Nippy" % (self.fileN))
	
	# Bookmarks Handling -------------------------------------------------
	
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
			self.markerDelete(line, self.BOOKMARK_MARKER_NUM)
			self.bookmarks.remove(line)
		else:
			self.markerAdd(line, self.BOOKMARK_MARKER_NUM)
			self.bookmarks.add(line)
	
	# Go To... -----------------------------------------------------------
	
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
		line = self.markerFindNext(curLine + 1, self.BOOKMARK_MARKER_MASK)
		if line == -1:
			line = self.markerFindNext(0, self.BOOKMARK_MARKER_MASK)
			
		self.goto_line(line)
	
	# Jump to previous bookmark
	def goto_prev_bookmark(self):
		curLine, curPos = self.getCursorPosition()
		
		# wrap around if we don't go anywhere
		line = self.markerFindPrevious(curLine - 1, self.BOOKMARK_MARKER_MASK)
		if line == -1:
			line = self.markerFindPrevious(self.lines() - 1, self.BOOKMARK_MARKER_MASK)
		
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
			
	# Editing Tools ------------------------------------------------------
	
	# Move line up
	def move_line_up(self):
		self.SendScintilla(QsciScintilla.SCI_MOVESELECTEDLINESUP, 0, 0)
		
	# Move line down
	def move_line_down(self):
		self.SendScintilla(QsciScintilla.SCI_MOVESELECTEDLINESDOWN, 0, 0)


################################################

if __name__ == "__main__":
	app = qgui.QApplication(sys.argv)
	
	editor = NippyEdit()
	
	if len(sys.argv) > 1:
		for fileN in sys.argv[1:]:
			editor.load_file(fileN)
			break; # XXX: we currently only allow a single editor
	
	editor.show()
	app.exec_()

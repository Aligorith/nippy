# Find dialog for Nippy
#
# Author: Joshua Leung

import PyQt4
from PyQt4 import QtCore as qcore
from PyQt4 import QtGui as qgui
from PyQt4 import Qsci

####################################
# Standard Find Dialog

class FindDialog(qgui.QDialog):
	# ctor
	# < editor: (NippyEdit) editor instance that this is being used for
	# < query: (str) initial query to use
	def __init__(self, editor, query):
		super(FindDialog, self).__init__(editor)
		
		self.editor = editor
		self.query = query
		
		self.setWindowTitle("Find...")
		self.setModal(False)
		
		self.setup_ui()
		
	# Setup UI for widget
	def setup_ui(self):
		# create widgets
		self.make_widgets()
		
		
		# set up layouts
		layout = qgui.QHBoxLayout()
		layout.setMargin(7)
		self.setLayout(layout)
		
		# left: previous match
		layout.addWidget(self.prevBut)
		
		# middle
		col = qgui.QVBoxLayout()
		layout.addLayout(col)
		
		# TODO: do we need a label to indicate the find type + 
		col.addWidget(self.queryBox)
		
		row = qgui.QHBoxLayout()
		row.addWidget(self.caseSensitive)
		row.addWidget(self.exactMatchesOnly)
		row.addWidget(self.rawString)
		col.addLayout(row)
		
		# end
		layout.addWidget(self.nextBut)
		
		
		# give focus to the text widget
		self.queryBox.setFocus(True)
		
		
	# create widgets
	def make_widgets(self):
		# previous match 
		# XXX: needs an icon
		self.prevBut = qgui.QPushButton("<")
		self.prevBut.setToolTip("Go to next match in backwards direction (wraps around)")
		self.prevBut.setFixedSize(40, 40)
		
		# next match
		# XXX: needs an icon
		self.nextBut = qgui.QPushButton(">")
		self.nextBut.setToolTip("Go to next match in forward direction (wraps around)")
		self.nextBut.setFixedSize(40, 40)
		
		# query box
		# TODO: as a dropdown for previous search queries
		# TODO: slightly taller
		self.queryBox = qgui.QLineEdit(self.query)
		self.queryBox.setToolTip("Text to search for")
		#self.queryBox.setStyleSheet("""\
		#	QLineEdit { padding: 10px; }
		#""")
		
		# checkboxes for options
		# TODO: persist settings betwene invocations of the dialog
		self.caseSensitive = qgui.QCheckBox("Case")
		self.caseSensitive.setToolTip("Search is case sensitive")
		
		self.exactMatchesOnly = qgui.QCheckBox("Exact")
		self.exactMatchesOnly.setToolTip("Match whole word exactly, instead of just partial strings")
		
		self.rawString = qgui.QCheckBox("Raw")
		self.rawString.setToolTip("Use the query string as written, without converting escape sequences")
		self.rawString.setCheckState(qcore.Qt.Checked)

####################################
# Find in Files

# TODO...

####################################

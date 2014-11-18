# Nippy Text Editor
# Author: Joshua Leung
#
# Defines for how various file types are handled

import os
from PyQt4.Qsci import *

###########################################
# Custom Lexers for foramts not supported natively
# e.g. subclass QsciLexerCustom

# TODO: QML

# TODO: Markdown
# TODO: restructuredtxt

###########################################
# File-Type Defines

# For each item, we require the following things:
# - name: (str) An identifier for the language (displayed to users)
# - lexer: (QsciLexer) Lexer to use (still need to create new instance first though)
# - ext: ([str]) A list of extensions
# - (fnames): ([str]) Optional list of filenames (including extension) which are of this type
# - (wrap) : (bool) Whether word wrapping is enabled by default for the type
FILETYPE_DEFINES = [
	{ 'name' : 'Normal Text',                                   'ext' : ['.txt'],   'wrap' : True},
	{ 'name' : 'Batch Script',   'lexer' : QsciLexerBatch,      'ext' : ['.bat'] },
	{ 'name' : 'C',              'lexer' : QsciLexerCPP,        'ext' : ['.c'] },
	{ 'name' : 'C++',            'lexer' : QsciLexerCPP,        'ext' : ['.cpp', '.cc', '.cxx', '.hpp'] },
	{ 'name' : 'C/C++ Header',   'lexer' : QsciLexerCPP,        'ext' : ['.h'] },
	{ 'name' : 'C#',             'lexer' : QsciLexerCSharp,     'ext' : ['.cs'] },
	{ 'name' : 'CSS',            'lexer' : QsciLexerCSS,        'ext' : ['.css'] },
	{ 'name' : 'CMake',          'lexer' : QsciLexerCMake,      'ext' : ['.cmake'],         'fnames' : ['CMakeFiles.txt'] },
	{ 'name' : 'HTML',           'lexer' : QsciLexerHTML,       'ext' : ['.html', '.htm'] },
	{ 'name' : 'Java',           'lexer' : QsciLexerJava,       'ext' : ['.java'] },
	{ 'name' : 'JavaScript',     'lexer' : QsciLexerJavaScript, 'ext' : ['.js'] },
	{ 'name' : 'JSON',           'lexer' : QsciLexerJavaScript, 'ext' : ['.json'] },  # NOTE: JSON = Javascript subset
	{ 'name' : 'LaTeX',          'lexer' : QsciLexerTeX,        'ext' : ['.tex'],  'wrap' : True }, # XXX: needs a better lexer
	#{ 'name' : 'Markdown',       'lexer' : MarkdownLexer,       'ext' : ['.md'],   'wrap' : True },
	{ 'name' : 'Python',         'lexer' : QsciLexerPython,     'ext' : ['.py', '.pyw'],    'fnames' : ['SConstruct', 'SConscript'] },
	{ 'name' : 'Shell Script',   'lexer' : QsciLexerBash,       'ext' : ['.sh', '.zsh'] },
	{ 'name' : 'XML',            'lexer' : QsciLexerXML,        'ext' : ['.xml'],  'wrap' : True},
	{ 'name' : 'YAML',           'lexer' : QsciLexerYAML,       'ext' : ['.yml'],  'wrap' : True },
]


############################################
# Strings of filetypes for UI

def extensions_to_string(ft):
	return ','.join("*%s" % (x) for x in ft['ext'])
	
def filetype_to_string(ft):
	return "%s source file (%s)" % (ft['name'], extensions_to_string(ft))
	

# Default filter type - *.txt
FILETYPES_DLG_FILTER_DEFAULT = filetype_to_string(FILETYPE_DEFINES[0])

# String of all extension types
FILETYPES_DLG_STRINGS     = ["All Files (*.*)"] + [filetype_to_string(ft) for ft in FILETYPE_DEFINES]
FILETYPES_DLG_FILTER_STR  = ';;'.join(FILETYPES_DLG_STRINGS)

###########################################
# API

# Get the file-type info from a given filename
def get_filetype(fileN):
	# sanity check
	if not fileN:
		return None
	
	# get the extension
	name, ext = os.path.splitext(str(fileN))
	
	# TODO: construct an inverse map which will be faster
	for ft in FILETYPE_DEFINES:
		if (ext[0] == '.') and (ext in ft.get('ext', [])):
			return ft
		elif fileN in ft.get('fnames', []):
			return ft
	
	return None

###########################################

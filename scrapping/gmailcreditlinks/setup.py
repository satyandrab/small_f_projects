
#	Project Name	:	PyToEXE
#	Project Date	:	03-04-2010
#	Author			:	livetogogo
#	Contact			:	livetogogo@gmail.com
#	Web				:	http://www.pythontr.org
#	Ver				:	1.1

#   Only valid for <Python2.x> version of py2exe module!!!
#   Download  : http://sourceforge.net/projects/py2exe/

from distutils.core import setup
import py2exe
setup (windows = [{"script":'D:/workspace/scrapping/gmailcreditlinks/gmail_selenium.py', "icon_resources":[(1,"pytoexe.ico")]}])

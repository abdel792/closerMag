import os
import globalVars
import urllib
import zipfile

def onInstall():
	pyppeteerUrl = "http://cyber25.free.fr/programs/pyppeteer.zip"
	zipPyppeteerPath, _ = urllib.request.urlretrieve(pyppeteerUrl)
	if not os.path.exists (os.path.join(os.environ['LOCALAPPDATA'], 'pyppeteer')):
		with zipfile.ZipFile(zipPyppeteerPath, "r") as f:
			f.extractall(os.environ['LOCALAPPDATA'])
	libUrl = "http://cyber25.free.fr/nvda-modules/lib.zip"
	zipLibPath, _ = urllib.request.urlretrieve(libUrl)
	with zipfile.ZipFile(zipLibPath, "r") as f:
		f.extractall(os.path.join(os.path.dirname(__file__), "globalPlugins", "conjugaison"))


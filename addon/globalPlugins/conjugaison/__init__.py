# globalPlugins/conjugaison/__init__.py.
# This file is covered by the GNU General Public License.
# You can read the licence by clicking Help->Licence in the NVDA menu
# or by visiting http://www.gnu.org/licenses/old-l+backspace

import addonHandler
import globalPluginHandler
import unicodedata
import wx
import sys
import gui
import config
from gui import NVDASettingsDialog
import os
from .conjugaisonSettings import ADDON_NAME, ADDON_SUMMARY, ConjugaisonSettingsPanel
from .contextHelp import showAddonHelp
import re
import urllib
import threading
import ui
import tempfile 
addonHandler.initTranslation()

if hasattr (gui, 'contextHelp'):
	saveShowHelp = gui.contextHelp.showHelp
	class EnterAVerbDialog(
	gui.contextHelp.ContextHelpMixin,
	wx.TextEntryDialog,  # wxPython does not seem to call base class initializer, put last in MRO
	):
		helpId = "promptToEnterAVerb"
else:
	class EnterAVerbDialog(
	wx.TextEntryDialog):
		pass

class GlobalPlugin (globalPluginHandler.GlobalPlugin):
	scriptCategory = ADDON_SUMMARY
	_instance = False
	contextHelp = False

	def __init__ (self, *args, **kwargs):
		super (GlobalPlugin, self).__init__(*args, **kwargs)
		self.verbe = ""
		NVDASettingsDialog.categoryClasses.append(ConjugaisonSettingsPanel)
		self.createMenu()

	def createMenu (self):
		self.toolsMenu = gui.mainFrame.sysTrayIcon.toolsMenu
		self.conjugationItem = self.toolsMenu.Append (wx.ID_ANY,
		# Translators: Item in the tools menu for the Addon conjugaison.
		_("Conju&gaison..."),
		# Translators: The tooltyp text for the conjugaison item.
		_("Allows you to conjugate a French verb using the site capeutservir.com"))

		gui.mainFrame.sysTrayIcon.Bind (wx.EVT_MENU, self.onConjugationDialog, self.conjugationItem)

	def terminate (self):
		try:
			NVDASettingsDialog.categoryClasses.remove(ConjugaisonSettingsPanel)
		except:
			pass
		try:
			if wx.version().startswith("4"):
				self.toolsMenu.Remove(self.conjugationItem)
			else:
				self.toolsMenu.RemoveItem(self.conjugationItem)
		except:
			pass

	def event_gainFocus (self, obj, nextHandler):
		if hasattr (gui, 'contextHelp'):
			if any (x == ADDON_SUMMARY for x in (obj.name, obj.parent.parent.name)) or self.contextHelp:
				gui.contextHelp.showHelp = showAddonHelp
			else:
				gui.contextHelp.showHelp = saveShowHelp
		nextHandler ()				

	def script_enterAVerb(self,gesture):
		self.onConjugationDialog ()

	# Translators: Message presented in input help mode.
	script_enterAVerb.__doc__ = _("Displays a dalogue box prompting the user to enter a French verb to conjugate.")

	def script_activateAddonSettingsDialog (self, gesture):
		wx.CallAfter (self.onAddonSettingsDialog, None)

	# Translators: Message presented in input help mode.
	script_activateAddonSettingsDialog.__doc__ = _("Allows you to display the conjugation add-on settings panel.")
	

	def onConjugationDialog (self, evt = None):
		if hasattr(gui, 'contextHelp'):
			self.contextHelp = True
			gui.contextHelp.showHelp = showAddonHelp
		if not self._instance:
			d = EnterAVerbDialog(
				gui.mainFrame,
				# Translators: Dialog text for the verb editing dialog.
				_("Enter a verb to conjugate"),
				# Translators: Title for the verb editing  dialog
				_("Verb to conjugate:"))
			def callback(result):
				if result in (wx.ID_OK, wx.ID_CANCEL):
					self._instance = False
					if hasattr (gui, 'contextHelp'):
						gui.contextHelp.showHelp = saveShowHelp
						self.contextHelp = False
				if result == wx.ID_OK:
					self.verb = d.Value
					self.conjugate()
			gui.runScriptModalDialog(d, callback)
			self._instance = True

	def onAddonSettingsDialog (self, evt):
		gui.mainFrame._popupSettingsDialog(NVDASettingsDialog, ConjugaisonSettingsPanel)

	def conjugate (self):
		title = msg = infinitif = ""
		if not re.match(r"^[^\W\d_]+$", self.verb):
			gui.messageBox (
			#Translators: A message to remind you that no text has been entered.
			_("Either you didn't enter anything or your verb is not correct. Please try again"),
			#Translators: Title of the blank field reminder dialog box.
			_("Input error")
			)
			self.onConjugationDialog ()
			return
		verb = unicodedata.normalize('NFD', self.verb).encode('ascii', 'ignore').decode("utf-8")
		req =urllib.request.urlopen(f"https://www.capeutservir.com/verbes/{verb}.html").read().decode("utf-8")
		pattern1 = r"<(?:th|td)[^>]*?>(.*?)<(?:/th|/td)>"
		rfinditer = re.compile(pattern1, re.M)
		pattern2 = r"</?span[^>]*>"
		rsub = re.compile(pattern2, re.M)
		lst = [rsub.sub("", x.group(1)) for x in rfinditer.finditer(req)]
		lst = [x for x in lst if not x in ('', '&nbsp;')]
		pattern3 = r"<th class[^=]*=[^\"]*\"mode\"[^>]*>(.*?)</th>"
		rfinditer = re.compile(pattern3, re.S)
		modes = [x.group(1) for x in rfinditer.finditer(req)]
		pattern4 = r"<div class[^=]*=[^\"]*\"fleft verb-meta-info\"[^>]*>(.*?)</div>"
		rsearch = re.compile(pattern4, re.S)
		pattern5 = r"</?(?:span|sup|b)[^>]*>"
		rsub = re.compile(pattern5, re.M)
		temps = [x for x in lst if not x in modes and not any(y in x for y in ("<ul", "&nbsp;"))]
		order = [0, 1, 3, 2, 4, 5, 7, 6, 8, 9, 11, 10, 12, 13, 15, 14, 16, 17, 18, 20, 19, 21, 22, 24, 23, 25, 26, 27, 29, 28, 30, 31, 32, 33, 34, 36, 35, 37, 38, 39, 41, 40, 42]
		try:
			lst = [lst[x] for x in order]
		except IndexError:
			title = _("Error")
			msg = f"<h1>{title}</h1>"
			msg += _("Can't conjugate the verb {verb}").format(verb=self.verb)
		if not msg:
			group = rsub.sub("", rsearch.search(req).group(1)).strip()
			infinitif = f"<h1>{group.replace(' Groupe: ---', '')} Le verbe {self.verb} est un auxiliaire.</h1>" if "---" in group else f"<h1>{group}.</h1>"
			frm = []
			frm.append(infinitif)
			for item in lst:
				if item in modes:
					frm.append(f"<h1>{item}</h1>")
				elif item in temps:
					frm.append(f"<h2>{item}</h2>")
				else:
					frm.append(item)
			msg = f'<body>{"".join(frm)}</body>'
			title = f"Conjuguer le verbe {self.verb}"
		if config.conf["conjugaison"]["displayMode"] == "HTMLMessage":
			t = threading.Thread (target = ui.browseableMessage, args = [msg, title, True])
			t.run()
		else:
			addonTempDir = os.path.join(tempfile.gettempdir(), ADDON_NAME)
			if not os.path.exists(addonTempDir):
				os.mkdir(addonTempDir)
			file = os.path.join (addonTempDir, "conjugaison.html")
			htmlText = f"""<!DOCTYPE html>
			<html lang='fr'>
			<meta charset = 'utf-8' />
			<head>
			<title>{title}</title>
			</head>
			{msg}
			</html>"""
			with open (file, mode = "w", encoding = "utf-8") as f:
				f.write (htmlText)
			os.startfile (file)

	__gestures = {
		"kb:control+f5":"enterAVerb"
	}
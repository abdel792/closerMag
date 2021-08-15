# globalPlugins/conjugaison/__init__.py.
# This file is covered by the GNU General Public License.
# You can read the licence by clicking Help->Licence in the NVDA menu
# or by visiting http://www.gnu.org/licenses/old-l+backspace

import addonHandler
import globalPluginHandler
import wx
import sys
from logHandler import log
import gui
import config
from gui import NVDASettingsDialog
import os
from .conjugaisonSettings import ADDON_NAME, ADDON_SUMMARY, ConjugaisonSettingsPanel
from .contextHelp import showAddonHelp

path = os.path.join(os.path.dirname(__file__), 'lib')
sys.path.append(path)
from requests_html import HTMLSession
sys.path.remove(path)

import threading
import ui
import tempfile 
addonHandler.initTranslation()

session = HTMLSession()

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
		if self.verb == '':
			gui.messageBox (
			#Translators: A message to remind you that no text has been entered.
			_("You did not enter any text, please validate the OK button to start over"),
			#Translators: Title of the blank field reminder dialog box.
			_("No text entered")
			)
			self.onConjugationDialog ()
			return
		response =session.get ("https://www.capeutservir.com/verbes/{0}.html".format(self.verb))
		tds = response.html.find('td')
		order = [0, 1, 3, 2, 4, 5, 7, 6, 8, 9, 11, 10, 12, 13, 15, 14, 16, 17, 18, 20, 19, 21, 22, 24, 23, 25, 26, 27, 29, 28, 30, 31, 33, 35, 36, 38, 37, 39, 40, 41, 43, 42, 44]
		try:
			lst = [response.html.find('td')[x].text for x in order]
		except IndexError:
			title = _("Error")
			msg = "<h1>{0}</h1>".format(title)
			msg += _("Can't conjugate the verb {0}").format(self.verb)
		groupe=response.html.xpath('//div[@class="fleft verb-meta-info"]')
		if not msg:
			if '---' in groupe[0].text:
				infinitif = "<h1>{0}</h1>".format(groupe[0].text.split(self.verb)[0] + self.verb + " Le verbe {0} est un auxiliaire.".format(self.verb))
			else:
				infinitif = "<h1>{0}</h1>".format(groupe[0].text)
			frm=[]
			frm.append(infinitif)
			for item in lst:
				if "\n" in item:
					frm.append("<ul><li>{0}</li></ul>".format(item.replace("\n", "</li><li>")))
				else:
					if any (item == x for x in ["Indicatif", "Subjonctif", "Conditionnel", "Impératif", "Participe"]):
						frm.append("<h1>{0}</h1>".format(item))
					else:
						if not item.endswith("ant"):
							frm.append("<h2>{0}</h2>".format(item))
						else:
							frm.append("<ul><li>{0}</li></ul>".format(item))
			msg = '<body>{0}</body>'.format("".join(frm))
			title = response.html.find('title', first = True).text
		if config.conf["conjugaison"]["displayMode"] == "HTMLMessage":
			t = threading.Thread (target = ui.browseableMessage, args = [msg, title, True])
			t.run()
		else:
			addonTempDir = os.path.join(tempfile.gettempdir(), ADDON_NAME)
			if not os.path.exists(addonTempDir):
				os.mkdir(addonTempDir)
			file = os.path.join (addonTempDir, "conjugaison.html")
			htmlText = """<!DOCTYPE html>
			<html lang='fr'>
			<meta charset = 'utf-8' />
			<head>
			<title>{title}</title>
			</head>
			{body}
			</html>""".format (title = title, body = msg)
			with open (file, mode = "w", encoding = "utf-8") as f:
				f.write (htmlText)
			os.startfile (file)

	__gestures = {
		"kb:control+f5":"enterAVerb"
	}
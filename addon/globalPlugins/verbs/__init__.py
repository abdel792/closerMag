# globalPlugins/verbs/__init__.py.
# This file is covered by the GNU General Public License.
# You can read the licence by clicking Help->Licence in the NVDA menu
# or by visiting http://www.gnu.org/licenses/old-l+backspace

import addonHandler
import globalPluginHandler
from typing import Callable
import unicodedata
import wx
import gui
import config
from gui import NVDASettingsDialog
import os
from .verbsSettings import ADDON_NAME, ADDON_SUMMARY, VerbsSettingsPanel
from .contextHelp import showAddonHelp
import re
import urllib
import ui
import tempfile
addonHandler.initTranslation()

# gettex translation function.
_: Callable[[str], str]

if hasattr(gui, 'contextHelp'):
	saveShowHelp = gui.contextHelp.showHelp

	class EnterAVerbDialog(
			gui.contextHelp.ContextHelpMixin,
			wx.TextEntryDialog,  # wxPython does not seem to call base class initializer, put last in MRO
	):
		helpId = "promptToEnterAVerb"
else:
	class EnterAVerbDialog(  # type: ignore[no-redef]
			wx.TextEntryDialog
	):
		pass


def displayInDefaultBrowser(fileName, title, body):
	addonTempDir = os.path.join(tempfile.gettempdir(), ADDON_NAME)
	if not os.path.exists(addonTempDir):
		os.mkdir(addonTempDir)
	file = os.path.join(addonTempDir, f"{fileName}.html")
	htmlText = f"""<!DOCTYPE html>
	<html lang='fr'>
	<meta charset = 'utf-8' />
	<head>
	<title>{title}</title>
	</head>
	{body}
	</html>"""
	with open(file, mode="w", encoding="utf-8") as f:
		f.write(htmlText)
	os.startfile(file)


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	scriptCategory = ADDON_SUMMARY
	_instance = False
	contextHelp = False

	def __init__(self, *args, **kwargs):
		super(GlobalPlugin, self).__init__(*args, **kwargs)
		self.verbe = ""
		NVDASettingsDialog.categoryClasses.append(VerbsSettingsPanel)
		self.createMenu()

	def createMenu(self):
		self.toolsMenu = gui.mainFrame.sysTrayIcon.toolsMenu
		verbsMenu = wx.Menu()

		self.mainItem = self.toolsMenu.AppendSubMenu(
			verbsMenu,
			# Translators: Item in the tools menu for the Addon verbs.
			_("Ver&bs"),
			# Translators: The tooltyp text for the verbs submenu.
			_("{0} add-on and its tools").format(ADDON_NAME)
		)

		self.conjugationItem = verbsMenu.Append(wx.ID_ANY,
		# Translators: Item in the verbs submenu for verb conjugation.
		_("Conju&gaison..."),
		# Translators: The tooltyp text for the conjugaison item.
		_("Allows you to conjugate a French verb using the site capeutservir.com"))

		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onConjugationDialog, self.conjugationItem)

		self.irregularVerbsItem = verbsMenu.Append(wx.ID_ANY,
		# Translators: Item in the verbs submenu to display irregular verbs.
		_("English ir&regular verbs..."),
		# Translators: The tooltyp text for the irregular verbs item.
		_("Allows you to view the list of English irregular verbs using the site capeutservir.com"))

		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onIrregularVerbsDialog, self.irregularVerbsItem)

	def terminate(self):
		try:
			NVDASettingsDialog.categoryClasses.remove(VerbsSettingsPanel)
		except Exception:
			pass
		try:
			if wx.version().startswith("4"):
				self.toolsMenu.Remove(self.mainItem)
			else:
				self.toolsMenu.RemoveItem(self.mainItem)
		except Exception:
			pass

	def event_gainFocus(self, obj, nextHandler):
		if hasattr(gui, 'contextHelp'):
			if any(x == ADDON_SUMMARY for x in (obj.name, obj.parent.parent.name)) or self.contextHelp:
				gui.contextHelp.showHelp = showAddonHelp
			else:
				gui.contextHelp.showHelp = saveShowHelp
		nextHandler()

	def script_enterAVerb(self, gesture):
		self.onConjugationDialog()

	# Translators: Message presented in input help mode.
	script_enterAVerb.__doc__ = _(
		"Displays a dalogue box prompting the user to enter a French verb to conjugate."
	)

	def script_displayIrregularVerbs(self, gesture):
		self.onIrregularVerbsDialog()

	# Translators: Message presented in input help mode.
	script_displayIrregularVerbs.__doc__ = _("""
		Displays the list of English irregular verbs with their preterite,
		past participle, as well as their French translations.
	""")

	def script_activateAddonSettingsDialog(self, gesture):
		wx.CallAfter(self.onAddonSettingsDialog, None)

	# Translators: Message presented in input help mode.
	script_activateAddonSettingsDialog.__doc__ = _("Allows you to display the verbs add-on settings panel.")

	def onIrregularVerbsDialog(self, evt=None):
		title = _("English irregular verbs")
		url = "https://www.capeutservir.com/verbes/uk_verbes_irreguliers.php"
		page = urllib.request.urlopen(url).read().decode("utf-8")
		pattern = r"<td>(?:<b>|<i>)?(.*?)(?:</b>|</i>)?</td>"
		verbs = [x.group(1) for x in re.finditer(pattern, page, re.S)]
		addition = (
			# Translators: Titled for the infinitive of the irregular verb.
			_("Infinitive"),
			# Translators: Titled for the preterite of the irregular verb.
			_("Preterite"),
			# Translators: Titled for the past participle of the irregular verb.
			_("Past participle"),
			# Translators: Titled for the French translation of the irregular verb.
			_("French translation")
		)
		i = 0
		lst = []
		for item in verbs:
			lst.append(addition[i])
			lst.append(item)
			i += 1
			if i > 3:
				i = 0
		lstForHtml = [(f"<h1>{item}</h1>" if item in addition else f"<ul><li>{item}</li></ul>") for item in lst]
		body = f"<body>{''.join(lstForHtml)}</body>"
		if config.conf["verbs"]["displayIrregularVerbsMode"] == "simpleMessage":
			ui.browseableMessage(title=title, message="\r\n".join(lst))
		elif config.conf["verbs"]["displayIrregularVerbsMode"] == "HTMLMessage":
			ui.browseableMessage(title=title, message=body, isHtml=True)
		else:
			displayInDefaultBrowser(fileName="irregularVerbs", title=title, body=body)

	def onConjugationDialog(self, evt=None):
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
					if hasattr(gui, 'contextHelp'):
						gui.contextHelp.showHelp = saveShowHelp
						self.contextHelp = False
				if result == wx.ID_OK:
					self.verb = d.Value
					self.conjugate()
			gui.runScriptModalDialog(d, callback)
			self._instance = True

	def onAddonSettingsDialog(self, evt):
		gui.mainFrame._popupSettingsDialog(NVDASettingsDialog, VerbsSettingsPanel)

	def conjugate(self):  # noqa: C901
		if re.match(r"^[^\W\d_]+$", self.verb):
			verb = unicodedata.normalize('NFD', self.verb).encode('ascii', 'ignore').decode("utf-8")
			req = urllib.request.urlopen(f"https://www.capeutservir.com/verbes/{verb}.html").read().decode("utf-8")
			pattern1 = r"<(?:th|td)[^>]*?>(.*?)<(?:/th|/td)>"
			rfinditer = re.compile(pattern1, re.M)
			pattern2 = r"</?span[^>]*>"
			rsub = re.compile(pattern2, re.M)
			lst = [rsub.sub("", x.group(1)) for x in rfinditer.finditer(req)]
			lst = [x for x in lst if x not in ('', '&nbsp;')]
			pattern3 = r"<th class[^=]*=[^\"]*\"mode\"[^>]*>(.*?)</th>"
			rfinditer = re.compile(pattern3, re.S)
			modes = [x.group(1) for x in rfinditer.finditer(req)]
			pattern4 = r"<div class[^=]*=[^\"]*\"fleft verb-meta-info\"[^>]*>(.*?)</div>"
			rsearch = re.compile(pattern4, re.S)
			pattern5 = r"</?(?:span|sup|b)[^>]*>"
			rsub = re.compile(pattern5, re.M)
			temps = [x for x in lst if x not in modes and not any(y in x for y in ("<ul", "&nbsp;"))]
			order = (0, 1, 3, 2, 4, 5, 7, 6, 8, 9, 11, 10, 12, 13, 15,
				         14, 16, 17, 18, 20, 19, 21, 22, 24, 23,         14, 16, 17, 18, 20, 19, 21, 22, 24, 23,
				         25, 26, 27, 29, 28, 30, 31, 32, 33, 34, 36, 35, 37, 38, 39, 41, 40, 42)
		if not re.match(r"^[^\W\d_]+$", self.verb) or not len(lst):
			gui.messageBox(
				# Translators: A message to indicate that the text entered is not correctly written.
				_("Either you didn't enter anything or your verb is not correct. Please try again"),
				# Translators: Title of the message indicating the input error.
				_("Input error")
			)
			self.onConjugationDialog()
			return
		group = rsub.sub("", rsearch.search(req).group(1)).strip()
		cleanLst = []
		pattern7 = r"(?:<li>)([^<]*?)(?:</li>)"
		for item in lst:
			cleanLst.append(item)
			if re.search(pattern7, item):
				cleanLst.remove(item)
				cleanLst.extend([x.group(1) for x in re.finditer(pattern7, item)])
		title = f"Conjuguer le verbe {self.verb}"
		infinitif = f"<h1>{group.replace(' Groupe: ---', '')} Le verbe {self.verb} est un auxiliaire.</h1>"\
			if "---" in group else f"<h1>{group}.</h1>"
		frm = []
		frm.append(infinitif)
		for item in lst:
			if item in modes:
				frm.append(f"<h1>{item}</h1>")
			elif item in temps:
				frm.append(f"<h2>{item}</h2>")
			else:
				frm.append(item)
		msg = f"<body>{''.join(frm)}</body>"
		if config.conf["verbs"]["displayConjugationMode"] == "HTMLMessage":
			wx.CallAfter(ui.browseableMessage, title=title, message=msg, isHtml=True)
		elif config.conf["verbs"]["displayConjugationMode"] == "defaultBrowser":
			displayInDefaultBrowser(fileName="conjugaison", title=title, body=msg)
		else:
			infinitif = f"{group.replace(' Groupe: ---', '')} Le verbe {self.verb} est un auxiliaire."\
				if "---" in group else f"{group}."
			cleanLst.insert(0, infinitif)
			msg = "\r\n".join(cleanLst)
			wx.CallAfter(ui.browseableMessage, title=title, message=msg)

	__gestures = {
		"kb:control+f5": "enterAVerb",
		"kb:control+shift+f5": "displayIrregularVerbs"
	}

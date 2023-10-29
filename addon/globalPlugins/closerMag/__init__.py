# globalPlugins/closerMag/__init__.py.
# This file is covered by the GNU General Public License.
# You can read the licence by clicking Help->Licence in the NVDA menu
# or by visiting http://www.gnu.org/licenses/old-l+backspace

import addonHandler
import globalPluginHandler
import core
import threading
from typing import Callable
import wx
import gui
import config
from gui import NVDASettingsDialog
import os
from .closerMagSettings import ADDON_NAME, ADDON_SUMMARY, CloserMagSettingsPanel
from .closerMagDisplay import FirstListThread, ArticlesThread
from .contextHelp import showAddonHelp
import ui
import tempfile
addonHandler.initTranslation()
event = threading.Event()

# gettex translation function.
_: Callable[[str], str]

if hasattr(gui, 'contextHelp'):
	saveShowHelp = gui.contextHelp.showHelp


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
	<body>
	{body}
	</body>
	</html>""".replace("\t", "")
	with open(file, mode="w", encoding="utf-8") as f:
		f.write(htmlText)
	os.startfile(file)


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	scriptCategory = ADDON_SUMMARY
	_instance = False
	contextHelp = False

	def __init__(self, *args, **kwargs):
		super(GlobalPlugin, self).__init__(*args, **kwargs)
		NVDASettingsDialog.categoryClasses.append(CloserMagSettingsPanel)
		self.createMenu()

	def createMenu(self):
		self.toolsMenu = gui.mainFrame.sysTrayIcon.toolsMenu

		self.closerMagItem = self.toolsMenu.Append(wx.ID_ANY,
		# Translators: Item in the tools menu for displaying closerMag articles.
		_("C&loserMag..."),
		# Translators: The tooltyp text for the closerMag item.
		_("Allows you to view the latest 37 articles from the closermag.fr site"))

		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onCloserMagDialog, self.closerMagItem)

	def terminate(self):
		try:
			NVDASettingsDialog.categoryClasses.remove(CloserMagSettingsPanel)
		except Exception:
			pass
		try:
			if wx.version().startswith("4"):
				self.toolsMenu.Remove(self.closerMagItem)
			else:
				self.toolsMenu.RemoveItem(self.closerMagItem)
		except Exception:
			pass

	def event_gainFocus(self, obj, nextHandler):
		if hasattr(gui, 'contextHelp'):
			if obj.parent and obj.parent.parent and any(
				x == ADDON_SUMMARY for x in (obj.name, obj.parent.parent.name)
			) or self.contextHelp:
				gui.contextHelp.showHelp = showAddonHelp
			else:
				gui.contextHelp.showHelp = saveShowHelp
		nextHandler()

	def script_displayCloserMagArticles(self, gesture):
		self.onCloserMagDialog()

	# Translators: Message presented in input help mode.
	script_displayCloserMagArticles.__doc__ = _(
		"Allows you to display the last 37 articles appearing on the site closermag.fr."
	)

	def script_activateAddonSettingsDialog(self, gesture):
		wx.CallAfter(self.onAddonSettingsDialog, None)

	# Translators: Message presented in input help mode.
	script_activateAddonSettingsDialog.__doc__ = _("Allows you to display the closerMag add-on settings panel.")

	def onCloserMagDialog(self, evt=None):
		title = _("Recent articles on closermag.fr")
		isHtml = config.conf["closerMag"]["displayCloserMagMode"] in ("HTMLMessage", "defaultBrowser")
		thread1 = FirstListThread(event)
		thread1.start()
		event.wait(0.3)
		event.clear()
		thread2 = ArticlesThread(event, isHtml=isHtml)
		thread2.start()
		event.wait(0.3)
		event.clear()
		message = "\r\n".join(thread2.result)
		if config.conf["closerMag"]["displayCloserMagMode"] in ("simpleMessage", "HTMLMessage"):
			core.callLater(0, ui.browseableMessage, title=title, message=message, isHtml=isHtml)
		else:
			displayInDefaultBrowser(fileName="closerMagArticles", title=title, body=message)

	def onAddonSettingsDialog(self, evt):
		gui.mainFrame._popupSettingsDialog(NVDASettingsDialog, CloserMagSettingsPanel)

	__gestures = {
		"kb:control+shift+f9": "displayCloserMagArticles",
	}

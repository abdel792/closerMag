# globalPlugins/closerMag/closerMagSettings.py.
# This file is covered by the GNU General Public License.
# You can read the licence by clicking Help->Licence in the NVDA menu
# or by visiting http://www.gnu.org/licenses/old-l+backspace

import wx
from typing import Callable, Dict, Tuple
import gui
import gui.guiHelper
import config

# We initialize translation support
import addonHandler
addonHandler.initTranslation()
if hasattr(gui.settingsDialogs, "SettingsPanel"):
	from gui.settingsDialogs import SettingsPanel
else:
	from gui import SettingsPanel

# Constants
ADDON_SUMMARY: str = addonHandler.getCodeAddon().manifest["summary"]
ADDON_NAME: str = addonHandler.getCodeAddon().manifest["name"]

# gettex translation function.
_: Callable[[str], str]

confSpec: Dict = {
	"displayCloserMagMode": "string(default = HTMLMessage)",
}
config.conf.spec["closerMag"] = confSpec


class CloserMagSettingsPanel(SettingsPanel):

	# Translators: The title of the add-on configuration dialog box.
	title: str = ADDON_SUMMARY
	helpId: str = "closerMagSettings"
	DISPLAY_MODES: Tuple[Tuple[str, str], Tuple[str, str], Tuple[str, str]] = (
		("HTMLMessage",
		 # Translators: Display the result in an NVDA message of type HTML.
		 _("Display in HTML message")),
		("simpleMessage",
		 # Translators: Displays the result in a simple NVDA browseable message.
		 _("Display in a simple NVDA browseable message")),
		("defaultBrowser",
		 # Translators: Display the result in default browser.
		 _("Display in default browser"))
	)

	def makeSettings(self, settingsSizer):
		# Translators: The label for an item to select the display mode for closermag's articles.
		self.displayCloserMagModeText = _("closermag.fr articles display mode")
		self.showSettingsDialog(settingsSizer)

	def showSettingsDialog(self, settingsSizer):
		settingsSizerHelper = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		displayCloserMagModeChoices = [name for mode, name in self.DISPLAY_MODES]
		self.displayCloserMagModesList = settingsSizerHelper.addLabeledControl(
			self.displayCloserMagModeText,
			wx.Choice,
			choices=displayCloserMagModeChoices
		)
		curCloserMagMode = config.conf["closerMag"]["displayCloserMagMode"]
		for index, (mode, name) in enumerate(self.DISPLAY_MODES):
			if mode == curCloserMagMode:
				self.displayCloserMagModesList.SetSelection(index)
				break

	def onSave(self):
		displayCloserMagMode = self.DISPLAY_MODES[self.displayCloserMagModesList.GetSelection()][0]
		config.conf["closerMag"]["displayCloserMagMode"] = displayCloserMagMode

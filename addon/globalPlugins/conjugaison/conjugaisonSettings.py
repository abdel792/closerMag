# globalPlugins/conjugaison/conjugaisonSettings.py.
# This file is covered by the GNU General Public License.
# You can read the licence by clicking Help->Licence in the NVDA menu
# or by visiting http://www.gnu.org/licenses/old-l+backspace

import wx
import gui
import gui.guiHelper
import config

# We initialize translation support
import addonHandler
addonHandler.initTranslation ()

from gui import SettingsPanel

### Constants
ADDON_SUMMARY = addonHandler.getCodeAddon ().manifest["summary"]
ADDON_NAME = addonHandler.getCodeAddon ().manifest["name"]

confSpec = {
	"displayMode" : "string(default = HTMLMessage)",
	}
config.conf.spec["conjugaison"] = confSpec

class ConjugaisonSettingsPanel (SettingsPanel):

	# Translators: The title of the add-on configuration dialog box.
	title = ADDON_SUMMARY
	helpId = "conjugaisonSettings"
	DISPLAY_MODES = (
		("HTMLMessage",
		# Translators: Display the conjugation in an NVDA message of type HTML.
		_("Display in HTML message")),
		("defaultBrowser",
		# Translators: Display the conjugation in default browser.
		_("Display in default browser")))

	def makeSettings (self, settingsSizer):
		# Translators: The label for an item to select the display mode for conjugations.
		self.displayModeText = _("Display modes:")
		self.showSettingsDialog(settingsSizer)

	def showSettingsDialog (self, settingsSizer):
		settingsSizerHelper = gui.guiHelper.BoxSizerHelper (self, sizer = settingsSizer)
		displayModeChoices = [name for mode, name in self.DISPLAY_MODES]
		self.displayModesList = settingsSizerHelper.addLabeledControl(self.displayModeText, wx.Choice, choices = displayModeChoices)
		curMode = config.conf["conjugaison"]["displayMode"]
		for index, (mode, name) in enumerate(self.DISPLAY_MODES):
			if mode == curMode:
				self.displayModesList.SetSelection(index)
				break

	def onSave (self):
		displayMode = self.DISPLAY_MODES[self.displayModesList.GetSelection()][0]
		config.conf["conjugaison"]["displayMode"] = displayMode

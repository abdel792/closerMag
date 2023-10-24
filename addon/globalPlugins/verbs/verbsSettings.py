# globalPlugins/verbs/verbsSettings.py.
# This file is covered by the GNU General Public License.
# You can read the licence by clicking Help->Licence in the NVDA menu
# or by visiting http://www.gnu.org/licenses/old-l+backspace

import wx
from typing import Callable
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
ADDON_SUMMARY = addonHandler.getCodeAddon().manifest["summary"]
ADDON_NAME = addonHandler.getCodeAddon().manifest["name"]

# gettex translation function.
_: Callable[[str], str]
confSpec = {
	"displayConjugationMode": "string(default = HTMLMessage)",
	"displayIrregularVerbsMode": "string(default = HTMLMessage)",
}
config.conf.spec["verbs"] = confSpec


class VerbsSettingsPanel(SettingsPanel):

	# Translators: The title of the add-on configuration dialog box.
	title = ADDON_SUMMARY
	helpId = "verbsSettings"
	DISPLAY_MODES = (
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
		# Translators: The label for an item to select the display mode for conjugations.
		self.displayConjugationModeText = _("Display conjugation modes:")
		self.displayIrregularVerbsModeText = _("Display irregular verbs modes:")
		self.showSettingsDialog(settingsSizer)

	def showSettingsDialog(self, settingsSizer):
		settingsSizerHelper = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		displayConjugationModeChoices = [name for mode, name in self.DISPLAY_MODES]
		self.displayConjugationModesList = settingsSizerHelper.addLabeledControl(
			self.displayConjugationModeText,
			wx.Choice,
			choices=displayConjugationModeChoices
		)
		curConjugationMode = config.conf["verbs"]["displayConjugationMode"]
		for index, (mode, name) in enumerate(self.DISPLAY_MODES):
			if mode == curConjugationMode:
				self.displayConjugationModesList.SetSelection(index)
				break

		displayIrregularVerbsModeChoices = [name for mode, name in self.DISPLAY_MODES]
		self.displayIrregularVerbsModesList = settingsSizerHelper.addLabeledControl(
			self.displayIrregularVerbsModeText,
			wx.Choice,
			choices=displayIrregularVerbsModeChoices
		)
		curIrregularVerbsMode = config.conf["verbs"]["displayIrregularVerbsMode"]
		for index, (mode, name) in enumerate(self.DISPLAY_MODES):
			if mode == curIrregularVerbsMode:
				self.displayIrregularVerbsModesList.SetSelection(index)
				break

	def onSave(self):
		displayConjugationMode = self.DISPLAY_MODES[self.displayConjugationModesList.GetSelection()][0]
		displayIrregularVerbsMode = self.DISPLAY_MODES[self.displayIrregularVerbsModesList.GetSelection()][0]
		config.conf["verbs"]["displayConjugationMode"] = displayConjugationMode
		config.conf["verbs"]["displayIrregularVerbsMode"] = displayIrregularVerbsMode

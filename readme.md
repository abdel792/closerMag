# Verbs #

* Authors : Abdel.
* Download [stable version][1]
* Download [development version][2]

This add-on allows you to display the conjugation of a French verb, as well as the list of English irregular verbs using the site: "https://www.capeutservir.com".

It adds a menu to the NVDA Tools menu named "Verbs".

Validating on this element will display the following submenus:

* An item named "Conjugaison", which allows you to open a dialog box to enter a French verb of our choice to conjugate;
* An item named "English irregular verbs", which allows you to display the list of English irregular verbs.

## The "Conjugaison" submenu

When you validate on the "Conjugaison" item, you obtain a dialog box composed of the following elements:

* An input field to type your verb to be conjugated;
{: #promptToEnterAVerb }
* An "OK" button to display an html page containing your conjugation;
* A "Cancel" button to close the dialog box.

## The "English irregular verbs" submenu

When you validate on the "English irregular verbs" item, The complete list of English irregular verbs should be displayed, with the following indications for each verb:

* Infinitive, to know the infinitive of the verb;
* Preterite, to know its preterite;
* Past participle, to know its past participle;
* French translation, to know its translation into French.

## Add-on settings ## {: #verbsSettings }

In the add-on's settings panel, you should find the following:

* Display conjugation mode which allows to define the display mode of the conjugation;
* Display irregular verbs mode which allows to define the display mode of the irregular verbs;
* Each of these 2 display modes offers the following 3 choices:
    * Display in an HTML message, which allows you to display the result in a browseable HTML message  (this is the default choice);
    * Display in a simple message, which allows you to display the result in a simple browseable message, without HTML formatting;
    * Display in default browser, to display the result in your default browser.
* An "OK" button to save your configuration;
* A "Cancel" button to cancel and close the dialog box.
* An "Apply" button to apply your configuration;

## Notes ##

* By default, the "control + F5" gesture is assigned to the script which displays the dialog inviting the user to enter a verb to conjugate;
* By default, the "control + Shift + F5" gesture is assigned to the script which displays the list of English irregular verbs;
* A script without an assigned gesture allows you to open the add-on settings panel;
* You can assign  new gestures to run this scripts in the "Input gestures" menu and, more precisely, in the "Verbs" category;
* If you are using nvda-2021.1 or later, you will be able to access the help from the input field of the verb to be conjugated, as well as from the add-on settings panel by simply pressing the "F1" key. as soon as the focus is on one of these 2 controls.

## Compatibility ##

* This add-on is compatible with NVDA 2019.3 and beyond.

## Changes for version 23.10.24 ##

* Renamed the add-on from "Conjugaison" to "Verbs";
* Added display of English irregular verbs.

## Changes for version 23.10.20 ##

* Removed the use of the "requests_html" library and used the built-in "urllib" module instead;
* Added support for Latin characters when entering the verb to conjugate in the prompt.

## Changes for version 21.08.1 ##

* Reduced the size of the add-on and included the download and installation of the external libraries from the "installTasks.py" module.

## Changes for version 21.08 ##

* Initial version.
  
  
  [[!tag dev stable]]

[1]: https://github.com/abdel792/verbs/releases/download/v23.10.24/verbs-23.10.24.nvda-addon

[2]: http://cyber25.free.fr/nvda-addons/verbs-23.10.24-dev.nvda-addon

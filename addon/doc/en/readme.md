### CloudVision

The add-on allows you to get a description of the image using artificial intelligence.

It works through Google Chrome OCR, PiccyBot, and Mathpix for mathematical formulas and equations.

Previously, there were Microsoft and Be My Eyes, but the former blocked access, and the latter began to protect themselves from non-official use of the API.

The add-on settings are in the  NVDA menu, parameters, CloudVision Settings.

Keyboard shortcuts:

* NVDA+CTRL+I - get a description of the navigator object or jpg/png file if it is in focus in Windows explorer. If you press twice quickly, the result will appear in the virtual viewer, you can read with arrows, select, copy, and so on;
* NVDA+ALT+F - recognize full screen;
* NVDA+ALT+C - recognize an image from the clipboard;
* NVDA+ALT+A - ask a question to bot about the last recognized image;
* Analyze object with Mathpix (for mathematical formulas) - the combination is not assigned, you can assign it yourself in the input gestures;
* Copy the last recognized result to the clipboard - the combination is not assigned, you can assign it yourself in the input gestures;
* NVDA+ALT+P - switching prompts (briefly, in detail, your own).

## Mathpix Integration

To use Mathpix for recognizing mathematical formulas and equations:

1. Get an API key from [mathpix.com](https://mathpix.com)
2. Enter your API key in the CloudVision settings dialog
3. Enable the "Use Mathpix for math formulas recognition" option

You can use Mathpix in two ways:
* When enabled in settings, Mathpix will be used alongside other recognition services during standard recognition (NVDA+CTRL+I)
* You can assign a keyboard shortcut to the "Analyze object with Mathpix" command in NVDA's input gestures dialog to use Mathpix directly


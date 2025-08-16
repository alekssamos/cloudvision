The add-on allows you to get a description of the image using artificial intelligence.

It works through the service visionbot.ru which uses recognition technologies
from Google, Microsoft and, more recently, Be My AI from Be My eyes. The add-on also supports
Mathpix for recognizing mathematical formulas and equations.

The add-on settings are in the  NVDA menu, parameters, CloudVision Settings.

Keyboard shortcuts:
* NVDA+CTRL+I - get a description of the navigator object or jpg/png file if it is in focus in Windows explorer. If you press twice quickly, the result will appear in the virtual viewer, you can read with arrows, select, copy, and so on.
* NVDA+ALT+F - recognize full screen
* NVDA+ALT+C - recognize an image from the clipboard
* NVDA+ALT+A - ask a question to the Be My AI (you need to log in or register to your account in the CloudVision settings)
* Analyze object with Mathpix (for mathematical formulas) - the combination is not assigned, you can assign it yourself in the input gestures
* Copy the last recognized result to the clipboard - the combination is not assigned, you can assign it yourself in the input gestures.

Logging in via Google, Apple and other services is not supported. Please, if an error occurs, create a new account with a new fresh email.

## Mathpix Integration

To use Mathpix for recognizing mathematical formulas and equations:

1. Get an API key from [mathpix.com](https://mathpix.com)
2. Enter your API key in the CloudVision settings dialog
3. Enable the "Use Mathpix for math formulas recognition" option

You can use Mathpix in two ways:
* When enabled in settings, Mathpix will be used alongside other recognition services during standard recognition (NVDA+CTRL+I)
* You can assign a keyboard shortcut to the "Analyze object with Mathpix" command in NVDA's input gestures dialog to use Mathpix directly

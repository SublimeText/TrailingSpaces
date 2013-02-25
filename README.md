## Synopsis

This is a [Sublime Text 2](http://www.sublimetext.com/2) plugin, with some support for ST3 as well
(not official yet). It allows you to…

**highlight trailing spaces and delete them in a flash!**

ST2 provides a way to automatically delete trailing spaces *upon file save*.
Depending on your settings, it may be more handy to just highlight them and/or
delete them by hand, at any time. This plugin provides just that!

## Installation

It should be available through [Sublime Package Contol](http://wbond.net/sublime_packages/package_control) and
this is the recommended way of installing the plugin.

You can still install it by hand if you want. Go to your `Packages` subdirectory under ST2's data directory:

* Windows: `%APPDATA%\Sublime Text 2`
* OS X: `~/Library/Application Support/Sublime Text 2/Packages`
* Linux: `~/.config/sublime-text-2`
* Portable Installation: `Sublime Text 2/Data`

Then clone this repository using [git](http://git-scm.com):

    git clone git://github.com/SublimeText/TrailingSpaces.git

That's it!

## Configuration

In order to use the deletion feature, one must bind the deletion command to a shortcut. To add the mapping,
you must define it into "Key Bindings - User":

``` js
{ "keys": ["ctrl+shift+t"], "command": "delete_trailing_spaces" }
```

With this setting, pressing <kbd>Ctrl + Shift + t</kbd> will delete all trailing spaces at once in the current file!

## Options

Several options are available to customize the plugin look 'n feel and behaviour. The
config keys goes into config files accessible throught the "Preferences" menu.

It is recommended using a specific settings file for this plugin. Under your ST's location (see above), you
will create it at `Packages/User/trailing_spaces.sublime-settings`.

### Change the highlighting color

One may also change the highlighting color, providing a scope name such
as "invalid", "comment"... in "File Settings - User":

``` js
{ "trailing_spaces_highlight_color": "invalid" }
```

Actually, "invalid" is the default value. If you'd like to use a custom color,
it should be defined as a color scope in your theme file. This is a dummy, fully-fledged
example (feel free to cut irrelevant pieces for your settings):

``` xml
<dict>
  <key>name</key>
  <string>Invalid - Illegal</string>
  <key>scope</key>
  <string>invalid.illegal</string>
  <key>settings</key>
  <dict>
    <key>background</key>
    <string>#F93232</string>
    <key>fontStyle</key>
    <string></string>
    <key>foreground</key>
    <string>#F9F2CE</string>
  </dict>
</dict>
```

And you would use the value of "invalid.illegal" in your setting to make use of your custom color.

### Making it invisible

You can make trailing spaces "invisible" and still rely on the deletion command. To do that, just
set the highlight color to an empty string:

``` js
{ "trailing_spaces_highlight_color": "" }
```

### Disabling highlighting for large files

Highlighting may be disabled for large files, for it may cause slowiness. The default threshold
is around 1 million of characters. This is configurable (in "File Settings - User"); unit is number of chars:

``` js
{ "trailing_spaces_file_max_size": 1000}
```

Even though the trailing spaces are not highlighted, one can still delete them
using the deletion command.

### Disabling highlighting on the current line

Highlighting trailing spaces for the currently edited line can be annoying and it is possible
to disable it, so the warning color is not seen after every space character when adding to a
line of code:

``` js
{ "trailing_spaces_include_current_line": false}
```

Even though the trailing spaces are not highlighted, one can still delete them
using the deletion command.

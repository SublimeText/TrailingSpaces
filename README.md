## Synopsis

This is a [Sublime Text 2](http://www.sublimetext.com/2) plugin, with some support for ST3 as well
(not official yet). It allows you to…

**highlight trailing spaces and delete them in a flash!**

ST2 provides a way to automatically delete trailing spaces *upon file save* (see below).
Depending on your settings, it may be more handy to just highlight them and/or
delete them by hand, at any time. This plugin provides just that!

## Installation

It should be available through [Sublime Package Contol](http://wbond.net/sublime_packages/package_control) and
this is the recommended way of installing the plugin.

You can still install it by hand if you want. Go to your `Packages` subdirectory under ST2's data directory:

* Windows: `%APPDATA%\Sublime Text 2`
* OS X: `~/Library/Application Support/Sublime Text 2`
* Linux: `~/.config/sublime-text-2`
* Portable Installation: `Sublime Text 2/Data`

Then clone this repository using [git](http://git-scm.com):

    git clone git://github.com/SublimeText/TrailingSpaces.git

That's it!

## Configuration

In order to use the deletion feature, one must bind the deletion command to a shortcut. To add the mapping,
you must define it into "Preferences / Key Bindings - User":

``` js
{ "keys": ["ctrl+shift+t"], "command": "delete_trailing_spaces" }
```

With this setting, pressing <kbd>Ctrl + Shift + t</kbd> will delete all trailing spaces at once in the current file!

*Beware*: I like this shortcut but it overrides the default ST's mapping for reopening last closed file. Pick what you like.

## Options

Several options are available to customize the plugin look 'n feel and behavior. The
config keys goes into a specific settings file for this plugin. Under your ST's location (see above), you
will need to create the file `Packages/User/trailing_spaces.sublime-settings`.

### Changing the highlighting color

You may change the highlighting color, providing a scope name such as "invalid", "comment"… just like that:

``` js
{ "trailing_spaces_highlight_color": "invalid" }
```

Actually, "invalid" is the default value. If you would like to use a custom color,
it should be defined as a color scope in your current theme file. Here is a dummy, fully-fledged
example (feel free to cut irrelevant pieces for your settings) of a custom color scope:

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
set the highlighting color to an empty string:

``` js
{ "trailing_spaces_highlight_color": "" }
```

*Beware*: this is **not** the same as disabling the highlighting (see below). With this setting, the plugin still
runs when opening a file and live afterwards, you just won't see the trailing spaces (they are highlighted with
a "transparent color"). Most of the time, what you will want is "On-demand highlighting" (again, see below).

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
{ "trailing_spaces_include_current_line": false }
```

Even though the trailing spaces are not highlighted, one can still delete them
using the deletion command.

### On-demand highlighting / no highlighting

The highlighting feature is entirely optionnal: as long as you defined a mapping to the deletion
command, you can run it and it will perform as expected, detecting and erasing all trailing spaces
although they are not made "visible". You can disable highlighting with this setting:

``` js
{ "trailing_spaces_enabled": false }
```

Still, you may want to toggle highlighting, just to check them out. In order to do that, define a
mapping to the toggling command:

``` js
// I like "d", as in "detect".
{ "keys": ["ctrl+shift+d"], "command": "toggle_trailing_spaces" }
```

----

Oh, and for those who wonder: several options must be comma-separated, like this:

``` js
{
  "option_1": value1,
  "option_2": value2
}
```

## Deleting trailing spaces upon file save

Sublime Text can delete trailing spaces on saving files. In order to enable this behavior, edit the
"Preferences / Settings - User" file and add the following setting:

``` js
"trim_trailing_white_space_on_save": true
```

This is of course compatible with using this plugin, which obviously does not provide a redundant option
for this behavior.

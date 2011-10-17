## Synopsis

This is a [Sublime Text 2](http://www.sublimetext.com/2) plugin.

**Highlight trailing spaces and delete them in a flash.**

ST2 provides a way to automatically delete trailing spaces upon file save.
Depending on your settings, it may be more handy to just highlight them and/or
delete them by hand. This plugin provides just that!

## Installation

Go to your `Packages` subdirectory under ST2's data directory:

* Windows: `%APPDATA%\Sublime Text 2`
* OS X: `~/Library/Application Support/Sublime Text 2`
* Linux: `~/.config/sublime-text-2`
* Portable Installation: `Sublime Text 2/Data`

Then clone this repository:

    git clone git://github.com/SublimeText/TrailingSpaces.git

That's it!

## Options

Several options are available to customize the plugin look 'n feel. The
config keys goes into config files accessible throught the "Preferences"
menu.

### Bind the deletion command to a shortcut

In order to use the deletion feature, one must add the mapping by hand
(this should probably go into "Key Bindings - User"):

``` js
{ "keys": ["ctrl+shift+t"], "command": "delete_trailing_spaces" }

Here, pressing Ctrl + Shift + t will delete all trailing spaces.
```

### Change the highlighting color

One may also change the highlighting color, providing a scope name such
as "invalid", "comment"... in "File Settings - User":

``` js
{ "trailing_spaces_highlight_color": "invalid" }
```

Actually, "invalid" is the default value. If you'd like to use a custom color,
it should be defined as a color scope in your theme file. Feel free to ask me
how to do it.

### Disabling highlighting for large files

Highlighting may be disabled for large files. The default threshold is around
1M chars. This is configurable (in "File Settings - User"); unit is number of chars:

``` js
{ "trailing_spaces_file_max_size": 1000}
```

Even though the trailing spaces are not highlighted, one can still delete them
using the deletion command.

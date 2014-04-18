Trailing Spaces
===============

A [Sublime Text 2](http://www.sublimetext.com/2) and
[3](http://www.sublimetext.com/3) plugin that allows you to…

**highlight trailing spaces and delete them in a flash!**

---

- [Synopsis](#synopsis)
- [Installation](#installation)
	- [Alternative installation methods](#alternative-installation-methods)
		- [From github](#from-github)
		- [Manually](#manually)
- [Usage](#usage)
	- [Deletion](#deletion)
	- [Toggling highlighting](#toggling-highlighting)
- [Options](#options)
	- [Changing the highlighting color](#changing-the-highlighting-color)
	- [Keeping trailing spaces invisible](#keeping-trailing-spaces-invisible)
	- [Include Current Line](#include-current-line)
	- [Include Empty Lines](#include-empty-lines)
	- [Modified Lines Only](#modified-lines-only)
	- [Trim On Save](#trim-on-save)
	- [Save After Trim](#save-after-trim)
	- [Live Matching vs On-demand Matching](#live-matching-vs-on-demand-matching)
	- [Ignore Syntax](#ignore-syntax)
	- [For power-users only!](#for-power-users-only)
		- [Disabled for large files](#disabled-for-large-files)
		- [The matching pattern](#the-matching-pattern)
- [About Sublime Text's built-in features](#about-sublime-texts-built-in-features)

Synopsis
--------

Sublime Text provides a way to automate deletion of trailing spaces *upon file
saving* (more on this at the end of this file). Depending on your settings, it
may be more handy to just highlight them and/or delete them by hand, at any
time. This plugin provides just that, and a *lot* of options to fine-tune the
way you want to decimate trailing spaces.

Installation
------------

It is available through
[Sublime Package Contol](http://wbond.net/sublime_packages/package_control) and
this is the recommended way of installation (brings configuration instructions,
automatic updates with changelogs…).

### Alternative installation methods

#### From github

You can install from github if you want, although Package Control automates
just that. Go to your `Packages` subdirectory under ST2's data directory:

* Windows: `%APPDATA%\Sublime Text 2`
* OS X: `~/Library/Application Support/Sublime Text 2`
* Linux: `~/.config/sublime-text-2`
* Portable Installation: `Sublime Text 2/Data`

Then clone this repository:

    git clone git://github.com/SublimeText/TrailingSpaces.git

#### Manually

[Download](https://github.com/SublimeText/TrailingSpaces/archive/master.zip)
the plugin as a zip. Copy the *Trailing Spaces* directory to its location
(see prior section).

Usage
-----

### Deletion

The main feature you gain from using this plugin is that of deleting all
trailing spaces in the currently edited document. In order to use this
deletion feature, you may either:

* click on "Edit / Trailing Spaces / Delete";
* bind the deletion command to a keyboard shortcut:

To add a key binding, open "Preferences / Key Bindings - User" and add:

``` js
{ "keys": ["ctrl+shift+t"], "command": "delete_trailing_spaces" }
```

With this setting, pressing <kbd>Ctrl + Shift + t</kbd> will delete all
trailing spaces at once in the current file! For OSX users, quoting wbond:
"When porting a key binding across OSes, it is common for the ctrl key on
Windows and Linux to be swapped out for super on OS X"
(eg. use "super+ctrl+t" instead).

*Beware*: the binding from this example overrides the default ST's mapping
for reopening last closed file. You can look at the default bindings in
"Preferences / Key Bindings - Default".

### Toggling highlighting

At any time, you can toggle highlighting on and off. You may either:

- click on "Edit / Trailing Spaces / Highlight Regions"
- bind the toggling command to a keyboard shortcut:

``` js
// I like "d", as in "detect" (overrides a default binding, though).
{ "keys": ["ctrl+shift+d"], "command": "toggle_trailing_spaces" }
```

Options
-------

Several options are available to customize the plugin's behavior. Those
settings are stored in a configuration file, as JSON. You must use a specific
file: Go to "Preferences / Package Settings / Trailing Spaces / Settings
\- User" to add you custom settings. You can look at the default values in
"Settings - Default", in the same menu.

A few of them are also accessible through the "Edit / Trailing Spaces" menu.
Sometimes, editing a setting will require a fresh Sublime Text to be applied
properly, so try relaunching ST before reporting an issue ;)

All settings are global (ie. applied to all opened documents).

### Changing the highlighting color

*Default: "invalid"*

You may change the highlighting color, providing a color scope name such as
 "error", "comment"… just like that:

``` js
{ "trailing_spaces_highlight_color": "comment" }
```

The scope should be defined in your current theme file. Here is a dummy,
fully-fledged example (feel free to cut irrelevant pieces for your settings)
of such a custom color scope:

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

You would then use the value of "invalid.illegal".

### Keeping trailing spaces invisible

You can make trailing spaces "invisible" yet still rely on the deletion
command. To do that, set the highlight scope to an empty string:

``` js
{ "trailing_spaces_highlight_color": "" }
```

Beware: this is **not** the same as *disabling* the highlighting (see "On-
Demand Matching" below). With this setting, the plugin still runs when opening
a file, and in the background afterwards; you just won't see the trailing
spaces (they are being highlighted with a "transparent" color).

### Include Current Line

*Default: true*

Highlighting of trailing spaces in the currently edited line can be annoying:
each time you are about to start a new word, the space you type is matched as
a trailing spaces. Currently edited line can thus be ignored:

``` js
{ "trailing_spaces_include_current_line": false }
```

Even though the trailing spaces are not highlighted on this line, they are
still internally matched and will be delete when firing the deletion command.

### Include Empty Lines

*Default: true*

When firing the deletion command, empty lines are matched as trailing regions,
and end up being deleted. You can specifically ignore them:

``` js
{ "trailing_spaces_include_empty_lines": false }
```

They will not be highlighted either.

### Modified Lines Only

*Default: false (reopen ST to update)*

When firing the deletion command, trailing regions *in the entire document* are
deleted. There are some use-cases when deleting trailing spaces *only on lines
you edited* is smarter; for instance when commiting changes to some third-party
source code.

At any time, you can change which area is covered when deleting trailing
regions. You may either:

- click on "Edit / Trailing Spaces / Modified Lines Only"
- specify as a setting:

``` js
{ "trailing_spaces_modified_lines_only": true }
```

There is also a command to toggle this feature on and off. You may thus define
a key binding:

``` js
{ "keys": ["pick+a+shortcut"], "command": "toggle_trailing_spaces_modified_lines_only" }
```

### Trim On Save

*Default: false*

Setting this to `true` will ensure trailing spaces are deleted when you save
your document. It abides by the other settings, such as *Modified Lines Only*.

``` js
{ "trailing_spaces_trim_on_save": true }
```

### Save After Trim

*Default: false*

You may not want to always trim trailing spaces on save, but the other way
around could prove useful. Setting this to `true` will automatically save your
document after you fire the deletion command:

``` js
{ "trailing_spaces_save_after_trim": true }
```

It is obviously ignored if *Trim On Save* is on.

### Live Matching vs On-demand Matching

*Default: true (reopen ST to update)*

By default, trailing regions are matched every time you edit the document, and
when you open it.

This feature is entirely optional and you may set it off: firing the deletion
command will cause the trailing spaces to be deleted as expected even though
they were not matched prior to your request. If you are afraid of the plugin
to cause slowness (for instance, you already installed several *heavy*
plugins), you can disable live matching:

``` js
{ "trailing_spaces_enabled": false }
```

In this case, for no trailing regions are matched until you request them to be
deleted, no highlighting occurs—it is in fact disabled, regardless of your
"scope" setting. If you want to check the trailing spaces regions, you can
toggle highlighting on and off. In this case, it may come in handy to define
a binding for the toggling command. When "On-demand Matching" is on and some
trailing spaces are highlighted, added ones will obviously not be. Toggling
highlight off and on will refresh them.

### Ignore Syntax

*Default: []*

With this option you can ignore specific files/views based on the syntax used.
An item has to match a case-sensitive substring of the syntax used in the view:

``` js
// Views with a syntax that contains "Diff" are ignored
{ "trailing_spaces_syntax_ignore": ["Diff"]}
```

### For power-users only!

#### Disabled for large files

The plugin is disabled altogether for large files, for it may cause slowness.
The default threshold is around 1 million of characters. This is
configurable (in "File Settings - User") and the unit is number of chars:

``` js
{ "trailing_spaces_file_max_size": 1000}
```

#### The matching pattern

*Default: [ \t]+*

Trailing spaces are line-ending regions containing at least one simple space,
tabs, or both. This pattern should be all you ever need, but if you *do* want
to abide by another definition to cover edge-cases, go ahead:

``` js
// *danger* will match newline chars and many other folks
"trailing_spaces_regexp": "[\\s]+"
```

About Sublime Text's built-in features
--------------------------------------

Trailing Spaces is designed to be a drop-in replacement of the limited
*Trim Whitespace On Save* built-in feature. ST is indeed able to delete
trailing spaces upon saving files, and maybe that's all you need!

In order to enable this behavior, edit "Preferences / Settings - User"
to add the following:

``` js
{ "trim_trailing_white_space_on_save": true }
```

As Trailing Spaces bypasses this setting, you will have to uninstall it to
benefit from this setting.

Made a little less obvious in the documentation are settings to showcase
whitespaces (*not only trailing ones!*):

``` js
{ "draw_white_space": "all" }
```

and to ensure a newline is kept at end of file upon saving:

``` js
{ "ensure_newline_at_eof_on_save": true }
```

The former will display *all* whitespaces in your files. There is another value
of "selection" which display whitespaces under (you got it) your current text
selection.

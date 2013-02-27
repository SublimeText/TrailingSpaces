'''
Provides both a trailing spaces highlighter and a deletion command.

See README.md for details.

@author: Jean-Denis Vauguet <jd@vauguet.fr>, Oktay Acikalin <ok@ryotic.de>
@license: MIT (http://www.opensource.org/licenses/mit-license.php)
@since: 2011-02-25
'''

import sublime
import sublime_plugin

DEFAULT_MAX_FILE_SIZE = 1048576
DEFAULT_COLOR_SCOPE_NAME = "invalid"
DEFAULT_IS_ENABLED = True

# Global settings object.
ts_settings = None
trailing_spaces_enabled = DEFAULT_IS_ENABLED
startup_queue = []

# Load settings and set whether the plugin is on or off.
def plugin_loaded():
    global ts_settings, trailing_spaces_enabled, startup_queue
    ts_settings = sublime.load_settings('trailing_spaces.sublime-settings')
    trailing_spaces_enabled = bool(ts_settings.get('trailing_spaces_enabled',
                                                   DEFAULT_IS_ENABLED))
    for view in startup_queue:
        highlight_trailing_spaces(view)


# Determine if the view is a find results view.
def is_find_results(view):
    return view.settings().get('syntax') and "Find Results" in view.settings().get('syntax')


# Return an array of regions matching trailing spaces.
def find_trailing_spaces(view):
    sel = view.sel()[0]
    line = view.line(sel.b)
    include_empty_lines = bool(ts_settings.get('trailing_spaces_include_empty_lines',
                                               DEFAULT_IS_ENABLED))
    include_current_line = bool(ts_settings.get('trailing_spaces_include_current_line',
                                                DEFAULT_IS_ENABLED))
    regexp = ts_settings.get('trailing_spaces_regexp') + "$"
    no_empty_lines_regexp = "(?<=\S)%s$" % regexp
    offending_lines = view.find_all(regexp if include_empty_lines else no_empty_lines_regexp)

    if include_current_line:
        return offending_lines
    else:
        current_offender = view.find(regexp if include_empty_lines else no_empty_lines_regexp, line.a)
        removal = False if current_offender == None else line.intersects(current_offender)
        return [i for i in offending_lines if i != current_offender] if removal else offending_lines


# Mark and highlight trailing spaces.
def highlight_trailing_spaces(view):
    if ts_settings is None:
        startup_queue.append(view)
        return
    max_size = ts_settings.get('trailing_spaces_file_max_size',
                               DEFAULT_MAX_FILE_SIZE)
    color_scope_name = ts_settings.get('trailing_spaces_highlight_color',
                                       DEFAULT_COLOR_SCOPE_NAME)
    if view.size() <= max_size and not is_find_results(view):
        regions = find_trailing_spaces(view)
        view.add_regions('TrailingSpacesHighlightListener',
                         regions, color_scope_name, "", sublime.HIDE_ON_MINIMAP)


# Clear all the highlighted regions.
def clear_trailing_spaces_highlight(window):
    for view in window.views():
        view.erase_regions('TrailingSpacesHighlightListener')


# Toggle the highlighting on or off.
class ToggleTrailingSpacesCommand(sublime_plugin.WindowCommand):
    def run(self):
        global trailing_spaces_enabled
        trailing_spaces_enabled = False if trailing_spaces_enabled else True

        # If toggling on, go ahead and perform a pass;
        # else, clear the highlighting in all views.
        if trailing_spaces_enabled:
            highlight_trailing_spaces(self.window.active_view())
        else:
            clear_trailing_spaces_highlight(self.window)


# Highlight matching regions.
class TrailingSpacesHighlightListener(sublime_plugin.EventListener):
    def on_modified(self, view):
        if trailing_spaces_enabled:
            highlight_trailing_spaces(view)

    def on_activated(self, view):
        if trailing_spaces_enabled:
            highlight_trailing_spaces(view)

    def on_load(self, view):
        if trailing_spaces_enabled:
            highlight_trailing_spaces(view)


# Deletes the matching regions.
#
# Note to self: TextCommand have an attached edit so we don't need to create an
# explicit Edit buffer.
class DeleteTrailingSpacesCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        regions = find_trailing_spaces(self.view)
        if regions:
            # Trick: reversing the regions takes care of the growing offset
            # while deleting the successive regions.
            regions.reverse()
            for r in regions:
                self.view.erase(edit, r)

            msg_parts = {"nbRegions": len(regions),
                         "plural":    's' if len(regions) > 1 else ''}
            msg = "Deleted %(nbRegions)s trailing spaces region%(plural)s" % msg_parts
        else:
            msg = "No trailing spaces to delete!"

        sublime.status_message(msg)


# Call the plugin_loaded callback manually if on ST2.
if not int(sublime.version()) > 3000:
    plugin_loaded()

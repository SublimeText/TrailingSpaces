'''
Provides both a trailing spaces highlighter and a deletion command.

See README.md for details.

@author: Jean-Denis Vauguet <jd@vauguet.fr>, Oktay Acikalin <ok@ryotic.de>
@license: MIT (http://www.opensource.org/licenses/mit-license.php)
@since: 2011-02-25
'''

import sublime
import sublime_plugin
import difflib
import codecs

DEFAULT_MAX_FILE_SIZE = 1048576
DEFAULT_IS_ENABLED = True
DEFAULT_MODIFIED_LINES_ONLY = False

# Global settings object and flags.
# Flags duplicate some of the (core) JSON settings, in case the settings file has
# been corrupted or is empty (ST2 really dislikes that!)
ts_settings_filename = "trailing_spaces.sublime-settings"
ts_settings = None
trailing_spaces_live_matching = DEFAULT_IS_ENABLED
trim_modified_lines_only = DEFAULT_MODIFIED_LINES_ONLY
startup_queue = []
on_disk = None


# Private: Loads settings and sets whether the plugin (live matching) is enabled.
#
# Returns nothing.
def plugin_loaded():
    global ts_settings_filename, ts_settings, trailing_spaces_live_matching
    global current_highlighting_scope, trim_modified_lines_only, startup_queue
    global DEFAULT_COLOR_SCOPE_NAME, on_disk

    ts_settings = sublime.load_settings(ts_settings_filename)
    trailing_spaces_live_matching = bool(ts_settings.get("trailing_spaces_enabled",
                                         DEFAULT_IS_ENABLED))
    current_highlighting_scope = ts_settings.get("trailing_spaces_highlight_color",
                                                 "invalid")
    DEFAULT_COLOR_SCOPE_NAME = current_highlighting_scope
    trim_modified_lines_only = bool(ts_settings.get("trailing_spaces_modified_lines_only",
                                                    DEFAULT_MODIFIED_LINES_ONLY))

    if trailing_spaces_live_matching:
        for view in startup_queue:
            match_trailing_spaces(view)
    else:
        current_highlighting_scope = ""
        if ts_settings.get("trailing_spaces_highlight_color") != current_highlighting_scope:
            persist_settings()


# Private: Updates user's settings with in-memory values.
#
# Allows for persistent settings from the menu.
#
# Returns nothing.
def persist_settings():
    sublime.save_settings(ts_settings_filename)


# Private: Determine if the view is a "Find results" view.
#
# view - the view, you know
#
# Returns True or False.
def is_find_results(view):
    return view.settings().get('syntax') and "Find Results" in view.settings().get('syntax')


# Private: Get the regions matching trailing spaces.
#
# As the core regexp matches lines, the regions are, well, "per lines".
#
# view - the view, you know
#
# Returns both the list of regions which map to trailing spaces and the list of
# regions which are to be highlighted, as a list [matched, highlightable].
def find_trailing_spaces(view):
    sel = view.sel()[0]
    line = view.line(sel.b)
    include_empty_lines = bool(ts_settings.get("trailing_spaces_include_empty_lines",
                                               DEFAULT_IS_ENABLED))
    include_current_line = bool(ts_settings.get("trailing_spaces_include_current_line",
                                                DEFAULT_IS_ENABLED))
    regexp = ts_settings.get("trailing_spaces_regexp") + "$"
    no_empty_lines_regexp = "(?<=\S)%s$" % regexp

    offending_lines = view.find_all(regexp if include_empty_lines else no_empty_lines_regexp)

    if include_current_line:
        return [offending_lines, offending_lines]
    else:
        current_offender = view.find(regexp if include_empty_lines else no_empty_lines_regexp, line.a)
        removal = False if current_offender == None else line.intersects(current_offender)
        highlightable = [i for i in offending_lines if i != current_offender] if removal else offending_lines
        return [offending_lines, highlightable]


# Private: Find the fraking trailing spaces in the view and flags them as such!
#
# It will refresh highlighted regions as well. Does not execute if the
# document's size exceeds the file_max_size setting, or if the fired in a view
# which is not a legacy document (helper/build views and so on).
#
# view - the view, you know
#
# Returns nothing.
def match_trailing_spaces(view):
    if ts_settings is None:
        startup_queue.append(view)
        return

    # Silently pass if file is too big.
    if max_size_exceeded(view):
        return

    if not is_find_results(view):
        (matched, highlightable) = find_trailing_spaces(view)
        add_trailing_spaces_regions(view, matched)
        highlight_trailing_spaces_regions(view, highlightable)


# Private: Checks whether the document is bigger than the max_size setting.
#
# view - the view, you know
#
# Returns True or False.
def max_size_exceeded(view):
    return view.size() > ts_settings.get('trailing_spaces_file_max_size',
                                         DEFAULT_MAX_FILE_SIZE)


# Private: Marks specified regions as trailing spaces.
#
# view - the view, you know
# regions - regions qualified as trailing spaces
#
# Returns nothing.
def add_trailing_spaces_regions(view, regions):
    view.erase_regions('TrailingSpacesMatchedRegions')
    view.add_regions('TrailingSpacesMatchedRegions',
                     regions,
                     "",
                     "",
                     sublime.HIDE_ON_MINIMAP)


# Private: Highlights specified regions as trailing spaces.
#
# It will use the scope enforced by the state of the toggable highlighting.
#
# view - the view, you know
# regions - regions qualified as trailing spaces
#
# Returns nothing.
def highlight_trailing_spaces_regions(view, regions):
    view.erase_regions("TrailingSpacesHighlightedRegions")
    view.add_regions('TrailingSpacesHighlightedRegions',
                     regions,
                     current_highlighting_scope or "",
                     "",
                     sublime.HIDE_ON_MINIMAP)


# Private: Toggles highlighting of all trailing spaces in the view.
#
# It has no effect is the plugin is disabled.
#
# view - the view, you know
#
# Returns True (highlighting was turned on) or False (turned off).
def toggle_highlighting(view):
    global current_highlighting_scope

    # If the scope is that of an invisible, there is nothing to toggle.
    if DEFAULT_COLOR_SCOPE_NAME == "":
        return "disabled!"

    # If performing live, highlighted trailing regions must be updated
    # internally.
    if not trailing_spaces_live_matching:
        (matched, highlightable) = find_trailing_spaces(view)
        highlight_trailing_spaces_regions(view, highlightable)

    scope = DEFAULT_COLOR_SCOPE_NAME if current_highlighting_scope == "" else ""
    current_highlighting_scope = scope
    highlight_trailing_spaces_regions(view, view.get_regions('TrailingSpacesHighlightedRegions'))
    return "off" if current_highlighting_scope == "" else "on"


# Clear all the highlighted regions in all views.
#
# FIXME: this is not used! Delete?
#
# window - the window, you know
#
# Returns nothing.
def clear_trailing_spaces_highlight(window):
    for view in window.views():
        view.erase_regions('TrailingSpacesMatchedRegions')


# Find edited lines since last save, as line numbers, based on diff.
#
# It uses a Differ object to compute the diff between the file as red on the
# disk, and the current buffer (which may differ from the disk's state). See
# http://docs.python.org/2/library/difflib.html for details about diff codes.
#
# It relies on a full diff, so it may be expensive computation for very large
# files (diff generation + looping through all lines).
#
# old - a buffer of lines, as in "old version"
# new - a buffer of lines, as in "new version"
#
# Returns the list of edited line numbers.
def modified_lines_as_numbers(old, new):
    d = difflib.Differ()
    diffs = d.compare(old, new)

    # Pretty Naive Algorithm (tm):
    # - split off the "Differ code", to check whether:
    #   - the line is in either in both files or just b: increment the line number
    #   - the line is only in b: it qualifies as an edited line!
    # Starting from -1 as ST2 is internally 0-based for lines.
    lineNum = -1
    edited_lines = []
    for line in diffs:
        code = line[:2]
        # those lines with "? " are not real! watch out!
        if code in ("  ", "+ "):
            lineNum += 1
        if code == "+ ":
            edited_lines.append(lineNum)

    return False if not edited_lines else edited_lines


# Private: Find the dirty lines.
#
# view - the view, you know
#
# Returns the list of regions matching dirty lines.
def get_modified_lines(view):
    try:
        on_disk
        on_buffer = view.substr(sublime.Region(0, view.size())).splitlines()
    except UnicodeDecodeError:
        sublime.status_message("File format incompatible with this feature (UTF-8 files only)")
        return

    lines = []
    line_numbers = modified_lines_as_numbers(on_disk, on_buffer)
    if line_numbers:
        lines = [view.full_line(view.text_point(number,0)) for number in line_numbers]
    return lines


# Private: Finds the trailing spaces regions to be deleted.
#
# It abides by the user settings: while in mode "Only Modified Lines", it returns
# the subset of trailing spaces regions which are within dirty lines; otherwise, it
# returns all trailing spaces regions for the document.
#
# view - the view, you know
#
# Returns a list of regions to be deleted.
def find_regions_to_delete(view):
    # If the plugin has been running in the background, regions have been matched.
    # Otherwise, we must find trailing spaces right now!
    if trailing_spaces_live_matching:
        regions = view.get_regions('TrailingSpacesMatchedRegions')
    else:
        (regions, highlightable) = find_trailing_spaces(view)

    # Filtering is required in case triming is restricted to dirty regions only.
    if trim_modified_lines_only:
        modified_lines = get_modified_lines(view)

        # If there are no dirty lines, don't do nothing.
        if not modified_lines:
            return

        # Super-private: filters trailing spaces regions to dirty lines only.
        #
        # As one cannot perform a smart find_all within arbitrary boundaries, we must do some
        # extra work:
        # - we want to loop through the modified lines set, not the whole trailing regions
        # - but we need a way to match modified lines with trailings to those very regions
        #
        # Hence the reversed dict on regions: keys are the text_point of the begining of
        # each region, values are the region's actual boundaries. As a Region is unhashable,
        # trailing regions are being recreated later on from those two values.
        #
        # We loop then loop through the modified lines: for each line, we get its begining
        # text_point, and check whether it matches a line with trailing spaces in the
        # reversed dict. If so, this is a match (a modified line with trailing spaces), so
        # we can re-create and store a Region for the relevant trailing spaces boundaries.
        #
        # Returns the filtered list of trailing spaces regions for the modified lines set.
        def only_those_with_trailing_spaces():
            regions_by_begin = {}
            matches = []
            for region in regions:
                begin = view.line(region).begin()
                regions_by_begin[begin] = (region.begin(), region.end())

            for line in modified_lines:
                text_point = line.begin()
                if text_point in regions_by_begin:
                    matches.append(sublime.Region(regions_by_begin[text_point][0], regions_by_begin[text_point][1]))

            return matches

        regions = only_those_with_trailing_spaces()

    return regions

# Private: Deletes the trailing spaces regions.
#
# view - the view, you know
# edit - the Edit object spawned by the deletion command
#
# Returns the number of deleted regions.
def delete_trailing_regions(view, edit):
    regions = find_regions_to_delete(view)

    if regions:
        # Trick: reversing the regions takes care of the growing offset while
        # deleting the successive regions.
        regions.reverse()
        for r in regions:
            view.erase(edit, r)
        return len(regions)
    else:
        return 0


# Public: Toggles the highlighting on or off.
class ToggleTrailingSpacesCommand(sublime_plugin.WindowCommand):
    def run(self):
        view = self.window.active_view()
        if max_size_exceeded(view):
            sublime.status_message("File is too big, trailing spaces handling disabled.")
            return

        state = toggle_highlighting(view)
        ts_settings.set("trailing_spaces_highlight_color", current_highlighting_scope)
        persist_settings()
        sublime.status_message('Highlighting of trailing spaces is %s' % state)

    def is_checked(self):
        return current_highlighting_scope != ""


# Public: Toggles "Modified Lines Only" mode on or off.
class ToggleTrailingSpacesModifiedLinesOnlyCommand(sublime_plugin.WindowCommand):
    def run(self):
        global trim_modified_lines_only

        was_on = ts_settings.get("trailing_spaces_modified_lines_only")
        ts_settings.set("trailing_spaces_modified_lines_only", not was_on)
        persist_settings()

        # TODO: use ts_settings.add_on_change() when it lands in ST3
        trim_modified_lines_only = ts_settings.get('trailing_spaces_modified_lines_only')
        message = "Let's trim trailing spaces everywhere" if was_on \
                  else "Let's trim trailing spaces only on modified lines"
        sublime.status_message(message)

    def is_checked(self):
        return ts_settings.get("trailing_spaces_modified_lines_only")


# Public: Matches and highlights trailing spaces on key events, according to the
# current settings.
class TrailingSpacesListener(sublime_plugin.EventListener):
    def on_modified(self, view):
        if trailing_spaces_live_matching:
            match_trailing_spaces(view)

    def on_activated(self, view):
        if trailing_spaces_live_matching:
            match_trailing_spaces(view)

    def on_selection_modified(self, view):
        if trailing_spaces_live_matching:
            match_trailing_spaces(view)

    def on_activated(self, view):
        self.freeze_last_version(view)
        if trailing_spaces_live_matching:
            match_trailing_spaces(view)

    def on_pre_save(self, view):
        self.freeze_last_version(view)
        if ts_settings.get("trailing_spaces_trim_on_save"):
            view.run_command("delete_trailing_spaces")

    # Toggling messes with what is red from the disk, and it breaks the diff
    # used when modified_lines_only is true. Honestly, I don't know why (yet).
    # Anyway, let's cache the persisted version of the document's buffer for
    # later use on specific event, so that we always have a decent version of
    # "what's on the disk" to work with.
    def freeze_last_version(self, view):
        global on_disk

        file_name = view.file_name()
        # For some reasons, the on_activated hook gets fired on a ghost document
        # from time to time.
        if file_name:
            on_disk = codecs.open(file_name, "r", "utf-8").read().splitlines()


# Public: Deletes the trailing spaces.
class DeleteTrailingSpacesCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if max_size_exceeded(self.view):
            sublime.status_message("File is too big, trailing spaces handling disabled.")
            return

        deleted = delete_trailing_regions(self.view, edit)

        if deleted:
            if ts_settings.get("trailing_spaces_save_after_trim") \
            and not ts_settings.get("trailing_spaces_trim_on_save"):
                sublime.set_timeout(lambda: self.save(self.view), 10)

            msg_parts = {"nbRegions": deleted,
                         "plural":    's' if deleted > 1 else ''}
            message = "Deleted %(nbRegions)s trailing spaces region%(plural)s" % msg_parts
        else:
            message = "No trailing spaces to delete!"

        sublime.status_message(message)

    def save(self, view):
        if view.file_name() is None:
            view.run_command('prompt_save_as')
        else:
            view.run_command('save')


# ST3 features a plugin_loaded hook which is called when ST's API is ready.
#
# We must therefore call our init callback manually on ST2. It must be the last
# thing in this plugin (thanks, beloved contributors!).
if not int(sublime.version()) > 3000:
    plugin_loaded()

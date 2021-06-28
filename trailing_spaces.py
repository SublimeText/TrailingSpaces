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
import re

from os.path import isfile
from collections import ChainMap
from sublime_lib import NamedSettingsDict

SETTINGS_FILENAME = 'trailing_spaces.sublime-settings'
# Only need defaults for settings that are not exposed in default settings.
DEFAULT_SETTINGS = {
    'syntax_ignore': [],
}

# dictionary of currently active view ids and last visible regions
active_views = {}
current_highlight_color = None
on_disk = None
# Highlight color as defined in settings. Plugin mutates that setting when disabled so
# that has to be stored.
INITIAL_HIGHLIGHT_COLOR = None
HIGHLIGHT_REGION_KEY = 'TrailingSpacesHighlightedRegions'
settings = None


def plugin_loaded():
    global settings, current_highlight_color, INITIAL_HIGHLIGHT_COLOR

    # A settings layer that handled settings that included `trailing_spaces_` prefix (now deprecated).
    class DeprecatedSettingsDict(NamedSettingsDict):
        def __getitem__(self, key):
            return super().__getitem__('trailing_spaces_%s' % key)

    deprecated_settings = DeprecatedSettingsDict(SETTINGS_FILENAME)
    settings = ChainMap(deprecated_settings, NamedSettingsDict(SETTINGS_FILENAME), DEFAULT_SETTINGS)

    current_highlight_color = settings['highlight_color']
    INITIAL_HIGHLIGHT_COLOR = current_highlight_color

    if not settings['enabled']:
        current_highlight_color = ""
        if settings['highlight_color'] != current_highlight_color:
            settings[0].save()


# Private: Makes sure all timers are stopped.
#
# Returns nothing.
def plugin_unloaded():
    global on_disk

    # clear all active views to kill all timeouts
    active_views.clear()
    on_disk = None


# Private: Returns all regions within region that match regex.
#
# view - the view, you know
# regions - a list of regions to search
# regex - the regex pattern to search for
#
# Returns all matching trailing regions within regions.
def view_find_all_in_regions(view, regions, regex):
    found = []

    # find all matches in the region's text
    for region in regions:
        text = view.substr(region)
        # translate positions to the region's starting position
        matches = re.finditer(regex, text, re.MULTILINE)
        found.extend(sublime.Region(m.start() + region.begin(), m.end() + region.begin()) for m in matches)

    return found


# Private: Get the regions matching trailing spaces.
#
# As the core regexp matches lines, the regions are, well, "per lines".
#
# view - the view, you know
# scan_only_visible - whether to limit scanning to only visible region
#
# Returns both the list of regions which map to trailing spaces and the list of
# regions which are to be highlighted, as a list [matched, highlightable].
def find_trailing_spaces(view, scan_only_visible=True):
    include_empty_lines = settings['include_empty_lines']
    include_current_line = settings['include_current_line']
    regexp = settings['regexp'] + "$"

    if not include_empty_lines:
        regexp = "(?<=\\S)%s$" % regexp

    trailing_regions = []

    non_visible_highlighting = settings['non_visible_highlighting']

    if scan_only_visible:
        # find all matches in the currently visible region plus a little before and after
        searched_region = view.visible_region()
        searched_region.a = max(searched_region.a - non_visible_highlighting, 0)
        searched_region.b = min(searched_region.b + non_visible_highlighting, view.size())

        searched_region = view.line(searched_region)  # align to line start and end
        trailing_regions = view_find_all_in_regions(view, [searched_region], regexp)
    else:
        trailing_regions = view.find_all(regexp)

    ignored_scopes = ",".join(settings['scope_ignore'])
    # filter out ignored scopes
    trailing_regions = [
        region for region in trailing_regions
        if not ignored_scopes or not view.match_selector(region.begin(), ignored_scopes)
    ]

    sel = view.sel()

    if include_current_line or len(sel) == 0:
        return [trailing_regions, trailing_regions]
    else:
        selection_lines = [view.line(region.b) for region in sel]
        # find all matches in the current line and exclude them from highlighting
        selection_offenders = view_find_all_in_regions(view, selection_lines, regexp)
        highlightable = [r for r in trailing_regions if r not in selection_offenders]
        return [trailing_regions, highlightable]


# Private: Find the freaking trailing spaces in the view and flags them as such!
#
# It will refresh highlighted regions as well. Does not execute if the
# document's size exceeds the file_max_size setting, or if the fired in a view
# which is not a legacy document (helper/build views and so on).
#
# view - the view, you know
#
# Returns nothing.
def match_trailing_spaces(view):
    # Silently pass ignored views.
    if ignore_view(view):
        return

    # Silently pass if file is too big.
    if max_size_exceeded(view):
        return

    (matched, highlightable) = find_trailing_spaces(view)
    highlight_trailing_spaces_regions(view, highlightable)


# Private: Checks if the view should be ignored.
#
# view - the view to check.
#
# Returns True if the view should be ignored, False otherwise.
def ignore_view(view):
    if view.is_scratch():
        return True

    view_settings = view.settings()
    view_syntax = view_settings.get('syntax')

    if not view_syntax or view_settings.get('is_widget'):
        return False

    for syntax_ignore in settings['syntax_ignore']:
        if syntax_ignore in view_syntax:
            return True

    return False


# Private: Checks whether the document is bigger than the max_size setting.
#
# view - the view, you know
#
# Returns True or False.
def max_size_exceeded(view):
    return view.size() > settings['file_max_size']


# Private: Highlights specified regions as trailing spaces.
#
# It will use the scope enforced by the state of the toggable highlighting.
#
# view - the view, you know
# regions - regions qualified as trailing spaces
#
# Returns nothing.
def highlight_trailing_spaces_regions(view, regions):
    view.erase_regions(HIGHLIGHT_REGION_KEY)
    if regions:
        view.add_regions(HIGHLIGHT_REGION_KEY, regions, current_highlight_color or "", "", sublime.HIDE_ON_MINIMAP)


# Private: Toggles highlighting of all trailing spaces in the view.
#
# It has no effect is the plugin is disabled.
#
# view - the view, you know
#
# Returns True (highlighting was turned on) or False (turned off).
def toggle_highlighting(view):
    global current_highlight_color

    # If the scope is that of an invisible, there is nothing to toggle.
    if INITIAL_HIGHLIGHT_COLOR == "":
        return "disabled!"

    # If performing live, highlighted trailing regions must be updated
    # internally.
    if not settings['enabled']:
        (matched, highlightable) = find_trailing_spaces(view)
        highlight_trailing_spaces_regions(view, highlightable)

    scope = INITIAL_HIGHLIGHT_COLOR if current_highlight_color == "" else ""
    current_highlight_color = scope
    highlight_trailing_spaces_regions(view, view.get_regions(HIGHLIGHT_REGION_KEY))
    return "off" if current_highlight_color == "" else "on"


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
    on_buffer = view.substr(sublime.Region(0, view.size())).splitlines()
    lines = []
    line_numbers = modified_lines_as_numbers(on_disk, on_buffer)
    if line_numbers:
        lines = [view.full_line(view.text_point(number, 0)) for number in line_numbers]
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
    (regions, highlightable) = find_trailing_spaces(view, scan_only_visible=False)

    # Filtering is required in case triming is restricted to dirty regions only.
    if settings['modified_lines_only']:
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
        settings['highlight_color'] = current_highlight_color
        settings[0].save()
        sublime.status_message('Highlighting of trailing spaces is %s' % state)

    def is_checked(self):
        return current_highlight_color != ""


# Public: Toggles "Modified Lines Only" mode on or off.
class ToggleTrailingSpacesModifiedLinesOnlyCommand(sublime_plugin.WindowCommand):
    def run(self):
        was_on = settings['modified_lines_only']
        settings['modified_lines_only'] = not was_on
        settings[0].save()

        message = "Let's trim trailing spaces everywhere" if was_on \
                  else "Let's trim trailing spaces only on modified lines"
        sublime.status_message(message)

    def is_checked(self):
        return settings['modified_lines_only']


# Public: Matches and highlights trailing spaces on key events, according to the
# current settings.
class TrailingSpacesListener(sublime_plugin.EventListener):
    def on_modified_async(self, view):
        if settings['enabled']:
            match_trailing_spaces(view)

    def on_selection_modified_async(self, view):
        if settings['enabled']:
            match_trailing_spaces(view)

    def on_activated_async(self, view):
        if settings['modified_lines_only']:
            self.freeze_last_version(view)

        if settings['enabled']:
            match_trailing_spaces(view)

            # continuously watch view for changes to the visible region
            if not view.id() in active_views:
                # track
                active_views[view.id()] = view.visible_region()
                self.update_on_region_change(view)

    def on_pre_save(self, view):
        if settings['modified_lines_only']:
            self.freeze_last_version(view)

        if settings['trim_on_save']:
            view.run_command("delete_trailing_spaces")

    def on_close(self, view):
        # untrack
        active_views.pop(view.id(), None)

    def update_on_region_change(self, view):
        # remove views not currently visible
        if not self.is_view_visible(view):
            active_views.pop(view.id(), None)
            return

        # compare the currently visible region to the previous (if any) and
        # update if there were changes
        if view.visible_region() != active_views.get(view.id(), view.visible_region()):
            match_trailing_spaces(view)
            active_views[view.id()] = view.visible_region()

        # continue only if the view is still active
        if settings['enabled'] and view.id() in active_views:
            sublime.set_timeout_async(lambda: self.update_on_region_change(view),
                                      settings['update_interval'])

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
        if file_name and not view.is_scratch() and isfile(file_name):
            encoding = view.encoding()

            if encoding == "Hexadecimal":  # not supported?
                on_disk = None
                return

            if encoding == "Undefined":
                encoding = view.settings().get("default_encoding", "UTF-8")

            match = re.match(r'.+\(([^)]+)\)$', encoding)
            encoding = match.group(1) if match else encoding

            with codecs.open(file_name, "r", encoding) as f:
                on_disk = f.read().splitlines()

    def is_view_visible(self, view):
        window = view.window()
        if not window:
            return False

        # panel views don't trigger on_close but are also not valid anymore
        # after being hidden, so try to detect these cases here
        if view.size() == 0 and not view.file_name():
            return False

        # see if this view is visible in its group
        group = window.get_view_index(view)[0]
        if group != -1:
            return view.id() == window.active_view_in_group(group).id()

        # check if this view is the active panel
        active_panel = window.active_panel() or ""

        # find_output_panel only works without the "output."" prefix
        if active_panel.startswith("output."):
            active_panel = active_panel[len("output."):]

        panel_view = window.find_output_panel(active_panel)
        if panel_view and view.id() == panel_view.id():
            return True

        return False


# Public: Deletes the trailing spaces.
class DeleteTrailingSpacesCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if max_size_exceeded(self.view):
            sublime.status_message("File is too big, trailing spaces handling disabled.")
            return

        deleted = delete_trailing_regions(self.view, edit)

        if deleted:
            if settings['save_after_trim'] and not settings['trim_on_save']:
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

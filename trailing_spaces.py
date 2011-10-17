'''
Provides both a trailing spaces highlighter and a deletion command.

Config summary (see README.md for details):

    # key binding
    { "keys": ["ctrl+shift+t"], "command": "delete_trailing_spaces" }

    # file settings
    {
      "trailing_spaces_highlight_color": "invalid",
      "trailing_spaces_file_max_size": 1000
    }

@author: Jean-Denis Vauguet <jd@vauguet.fr>, Oktay Acikalin <ok@ryotic.de>
@license: MIT (http://www.opensource.org/licenses/mit-license.php)
@since: 2011-02-25
'''

import sublime, sublime_plugin

DEFAULT_MAX_FILE_SIZE = 1048576
DEFAULT_COLOR_SCOPE_NAME = "invalid"

# Return an array of regions matching trailing spaces.
def find_trailing_spaces(view):
    trails = view.find_all('[ \t]+$')
    regions = []
    for trail in trails:
      regions.append(trail)
    return regions

# Highlight matching regions.
class TrailingSpacesHighlightListener(sublime_plugin.EventListener):
    def on_modified(self, view):
        max_size = view.settings().get('trailing_spaces_file_max_size',
                                       DEFAULT_MAX_FILE_SIZE)
        color_scope_name = view.settings().get('trailing_spaces_highlight_color',
                                               DEFAULT_COLOR_SCOPE_NAME)
        if view.size() <= max_size:
            regions = find_trailing_spaces(view)
            view.add_regions('TrailingSpacesHighlightListener',
                             regions, color_scope_name,
                             sublime.DRAW_EMPTY)

# Allows to erase matching regions.
class DeleteTrailingSpacesCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        regions = find_trailing_spaces(self.view)

        if regions:
            # deleting a region changes the other regions positions, so we
            # handle this maintaining an offset
            offset = 0
            for region in regions:
                r = sublime.Region(region.a + offset, region.b + offset)
                self.view.erase(edit, sublime.Region(r.a, r.b))
                offset -= r.size()

            msg_parts = {"nbRegions": len(regions),
                         "plural":    's' if len(regions) > 1 else ''}
            msg = "Deleted %(nbRegions)s trailing spaces region%(plural)s" % msg_parts
        else:
            msg = "No trailing spaces to delete!"

        sublime.status_message(msg)

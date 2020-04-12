import sublime


SETTINGS_FILENAME = 'trailing_spaces.sublime-settings'
DEFAULT_ENABLED = True
DEFAULT_HIGHLIGHT_COLOR = 'region.redish'
DEFAULT_MAX_FILE_SIZE = 1048576
DEFAULT_MODIFIED_LINES_ONLY = False
DEFAULT_NON_VISIBLE_HIGHLIGHTING = 500
DEFAULT_UPDATE_INTERVAL = 250


class Settings(object):
    def __init__(self):
        self._settings = None

    @property
    def is_initialized(self):
        return self._settings is not None

    def initialize(self):
        self._settings = sublime.load_settings(SETTINGS_FILENAME)

    def deinitialize(self):
        self._settings = None

    def persist(self):
        sublime.save_settings(SETTINGS_FILENAME)

    def get_enabled(self):
        return self._settings.get('trailing_spaces_enabled', DEFAULT_ENABLED)

    def get_highlight_color(self):
        return self._settings.get('trailing_spaces_highlight_color', DEFAULT_HIGHLIGHT_COLOR)

    def set_highlight_color(self, value):
        return self._settings.set('trailing_spaces_highlight_color', value)

    def get_include_empty_lines(self):
        return self._settings.get('trailing_spaces_include_empty_lines', DEFAULT_ENABLED)

    def get_include_current_line(self):
        return self._settings.get('trailing_spaces_include_current_line', DEFAULT_ENABLED)

    def get_modified_lines_only(self):
        return self._settings.get('trailing_spaces_modified_lines_only', DEFAULT_MODIFIED_LINES_ONLY)

    def set_modified_lines_only(self, value):
        return self._settings.set('trailing_spaces_modified_lines_only', value)

    def get_non_visible_highlighting(self):
        return self._settings.get('trailing_spaces_non_visible_highlighting', DEFAULT_NON_VISIBLE_HIGHLIGHTING)

    def get_trim_on_save(self):
        return self._settings.get('trailing_spaces_trim_on_save')

    def get_save_after_trim(self):
        return self._settings.get('trailing_spaces_save_after_trim')

    def get_scope_ignore(self):
        return self._settings.get('trailing_spaces_scope_ignore', [])

    def get_file_max_size(self):
        return self._settings.get('trailing_spaces_file_max_size', DEFAULT_MAX_FILE_SIZE)

    def get_regexp(self):
        return self._settings.get('trailing_spaces_regexp')

    def get_syntax_ignore(self):
        return self._settings.get('trailing_spaces_syntax_ignore', [])

    def get_update_interval(self):
        return self._settings.get('trailing_spaces_syntax_ignore', DEFAULT_UPDATE_INTERVAL)

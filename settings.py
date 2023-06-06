from typing import Any, List
import sublime


class TrailingSpacesSettings:
    SETTINGS_FILENAME = 'trailing_spaces.sublime-settings'

    def __init__(self):
        self._settings = sublime.Settings(0)

    def load(self) -> None:
        self._settings = sublime.load_settings(self.SETTINGS_FILENAME)

    def save(self) -> None:
        sublime.save_settings(self.SETTINGS_FILENAME)

    def _get(self, key: str, value_type: Any) -> Any:
        value = self._settings.get(key)
        if not isinstance(value, value_type):
            raise Exception(f'Invalid value for setting "{key}". Expected "{value_type}", got "{type(value)}')
        return value

    def _set(self, key: str, value: Any, value_type: Any) -> None:
        if not isinstance(value, value_type):
            raise Exception(f'Invalid value when setting "{key}". Expected "{value_type}", got "{type(value)}')
        self._settings.set(key, value)

    # -- Getters and setters for supported options ---------------------------------------------------------------------

    @property
    def enabled(self) -> bool:
        return self._get('enabled', bool)

    @property
    def file_max_size(self) -> int:
        return self._get('file_max_size', int)

    @property
    def highlight_color(self) -> str:
        return self._get('highlight_color', str)

    @highlight_color.setter
    def highlight_color(self, value: str) -> None:
        self._set('highlight_color', value, str)

    @property
    def include_current_line(self) -> bool:
        return self._get('include_current_line', bool)

    @property
    def include_empty_lines(self) -> bool:
        return self._get('include_empty_lines', bool)

    @property
    def modified_lines_only(self) -> bool:
        return self._get('modified_lines_only', bool)

    @modified_lines_only.setter
    def modified_lines_only(self, value: bool) -> None:
        self._set('modified_lines_only', value, bool)

    @property
    def non_visible_highlighting(self) -> int:
        return self._get('non_visible_highlighting', int)

    @property
    def regexp(self) -> str:
        return self._get('regexp', str)

    @property
    def save_after_trim(self) -> bool:
        return self._get('save_after_trim', bool)

    @property
    def scope_ignore(self) -> List[str]:
        return self._get('scope_ignore', list)

    @property
    def syntax_ignore(self) -> List[str]:
        value = self._settings.get('syntax_ignore')
        return value if isinstance(value, list) else []

    @property
    def trim_on_save(self) -> bool:
        return self._get('trim_on_save', bool)

    @property
    def update_interval(self) -> int:
        return self._get('update_interval', int)

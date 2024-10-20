from pathlib import Path

import pynvim

from usage_tracker.db import DatabaseQueries
from usage_tracker.logger import Logger
from usage_tracker.corpus_json import save_to_json


@pynvim.plugin
class LoggerPlugin:
    def __init__(self, vim: pynvim.Nvim) -> None:
        self._vim = vim
        self._logger: Logger | None = None
        self._data_dir = Path(vim.funcs.stdpath('data')) / 'utracker'
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._db_path = self._data_dir / 'log.db'

    @pynvim.command('UTrackerRun', nargs='?', sync=True)
    def cmd_start_logger(self, args: list[str]) -> None:
        if len(args) == 0:
            session_name = 'nvim'
        else:
            session_name = args[0]
        if self._logger is not None and self._logger.running:
            return
        try:
            self._logger = Logger(DatabaseQueries(self._db_path), session_name)
            self._logger.start()
            self._vim.api.notify('Logger started', 2, {})
        except Exception as e:
            self._vim.api.notify(f'Logger failed: {e}', 4, {})

    @pynvim.command('UTrackerStop', sync=True)
    def cmd_stop_logger(self) -> None:
        if not self._logger or not self._logger.running:
            return
        self._logger.stop()
        self._vim.api.notify('Logger stopped', 2, {})

    @pynvim.command('UTrackerPause', sync=True)
    def cmd_pause_logger(self) -> None:
        if not self._logger or not self._logger.running or self._logger.is_paused:
            return
        self._logger.pause()
        self._vim.api.notify('Logger paused', 2, {})

    @pynvim.command('UTrackerResume', sync=True)
    def cmd_resume_logger(self) -> None:
        if not self._logger or self._logger.running or not self._logger.is_paused:
            return
        self._logger.resume()
        self._vim.api.notify('Logger resumed', 2, {})

    @pynvim.command('UTrackerStatus', sync=True)
    def cmd_get_status(self) -> None:
        self._vim.api.notify(
            f"""
            Logger status:
                Initiated: {self._logger is None}
                Running: {False if not self._logger else self._logger.running}
                Logging being suppressed: {False if not self._logger else self._logger.is_paused}
            """,
            2,
            {},
        )

    @pynvim.command('UTrackerExport', nargs='?')
    def cmd_export(self, args: list[str]) -> None:
        if len(args) == 0:
            session_name = 'nvim'
        else:
            session_name = args[0]
        db = DatabaseQueries(self._db_path)
        data = db.get_genkey_stats(session_name)
        output_path = save_to_json(data, self._data_dir)
        self._vim.api.notify(f'Exported to {output_path.absolute()}', 2, {})

    @pynvim.autocmd('VimLeavePre', pattern='*', sync=True)
    def vim_leave_handler(self) -> None:
        if not self._logger or not self._logger.running:
            return
        self._logger.stop()


# TODO:
# - Update readme
## Perhaps the option to set your own autocmd should address these needs
# - Add option to silent notification on resume and paused
# - Add option to log all (outside of vim)
# - Add ways to view tracked data in a buffer
# - Remove default autocmd, provide default suggested set of autocmd instead

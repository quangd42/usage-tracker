import os

import pynvim

from usage_tracker.db import DatabaseQueries
from usage_tracker.logger import Logger


@pynvim.plugin
class LoggerPlugin:
    def __init__(self, vim: pynvim.Nvim) -> None:
        self._vim = vim
        self._logger: Logger | None = None
        data_dir = vim.funcs.stdpath('data')
        self._db_path = os.path.join(data_dir, 'utracker-log.db')

    @pynvim.command('UTrackerRun', sync=True)
    def start_logger(self) -> None:
        if self._logger is None:
            self._logger = Logger(DatabaseQueries(self._db_path), 'nvim')
        try:
            self._logger.start()
            self._vim.api.notify('Logger started', 2, {})
        except Exception as e:
            self._vim.api.notify(f'Logger failed: {e}', 4, {})

    @pynvim.command('UTrackerStop', sync=True)
    def stop_logger(self) -> None:
        if not self._logger or not self._logger.running:
            return
        self._logger.stop()
        self._vim.api.notify('Logger stopped', 2, {})

    @pynvim.command('UTrackerPause', sync=True)
    def pause_logger(self) -> None:
        if not self._logger or not self._logger.running or self._logger.is_paused:
            return
        self._logger.pause()
        self._vim.api.notify('Logger paused', 2, {})

    @pynvim.command('UTrackerResume', sync=True)
    def resume_logger(self) -> None:
        if not self._logger or self._logger.running or not self._logger.is_paused:
            return
        self._logger.resume()
        self._vim.api.notify('Logger resumed', 2, {})

    @pynvim.command('UTrackerStatus', sync=True)
    def logger_status(self) -> None:
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

    @pynvim.autocmd('VimLeavePre', pattern='*', sync=True)
    def vim_leave_handler(self) -> None:
        if not self._logger or not self._logger.running:
            return
        self._logger.stop()

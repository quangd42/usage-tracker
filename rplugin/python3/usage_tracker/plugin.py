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
        self._db_path = os.path.join(data_dir, 'utrack-log.db')

    @pynvim.command('UTrackerRun', nargs='*', sync=True)
    def start_logger(self, args):
        try:
            self._logger = Logger(DatabaseQueries(self._db_path), 'nvim')
            self._logger.start()
            self._vim.api.notify('Logger started', 2, {})
        except Exception as e:
            self._vim.api.notify(f'Logger failed: {e}', 4, {})

    @pynvim.command('UTrackerStop', nargs='*', sync=True)
    def stop_logger(self, args):
        if self._logger and self._logger.running:
            self._logger.stop()
            self._vim.api.notify('Logger stopped', 2, {})

    @pynvim.autocmd('VimLeavePre', pattern='*')
    def vim_leave_handler(self):
        if self._logger:
            self._logger.stop()

    @pynvim.autocmd('InsertEnter', pattern='*', sync=False)
    def insert_enter_handler(self):
        if self._logger:
            self._logger.pause()
            self._vim.api.notify('Logger paused', 2, {})

    @pynvim.autocmd('InsertLeave', pattern='*', sync=False)
    def insert_leave_handler(self):
        if self._logger and self._logger.is_paused:
            self._logger.resume()
            self._vim.api.notify('Logger resumed', 2, {})

    @pynvim.autocmd('BufEnter', pattern='*', sync=False)
    def buf_enter_handler(self):
        if self._logger and self._logger.is_paused:
            self._logger.resume()
            self._vim.api.notify('Logger resumed', 2, {})

    @pynvim.autocmd('FocusLost', pattern='*', sync=False)
    def vim_focus_lost_handler(self):
        if self._logger and not self._logger.is_paused:
            self._logger.pause()
            self._vim.api.notify('Logger paused', 2, {})

    @pynvim.autocmd('FocusGained', pattern='*', sync=False)
    def vim_focus_gained_handler(self):
        if self._logger:
            insert_mode = self._vim.api.get_mode()['mode'] == 'i'
            if insert_mode and not self._logger.is_paused:
                self._logger.pause()
                self._vim.api.notify('Logger paused', 2, {})
            elif not insert_mode and self._logger.is_paused:
                self._logger.resume()
                self._vim.api.notify('Logger resumed', 2, {})

import pynvim

from usage_tracker.db import DatabaseQueries
from usage_tracker.logger import Logger

DB_PATH = 'nvim-log.db'


@pynvim.plugin
class LoggerPlugin:
    def __init__(self, vim: pynvim.Nvim) -> None:
        self.vim = vim
        self.logger = Logger(DatabaseQueries(DB_PATH), 'nvim')

    # @pynvim.command('Cmd', range='', nargs='*', sync=True)
    # def command_handler(self, args, range):
    #     self.vim.current.line = 'Command: Called %d times, args: %s, range: %s' % (
    #         args,
    #         range,
    #     )

    @pynvim.command('UTrackerRun', nargs='*', sync=True)
    def start_logger(self, args):
        try:
            self.logger.start()
            self.vim.api.notify('Logger started', 2, {})
        except Exception as e:
            self.vim.api.notify(f'Logger failed: {e}', 4, {})

    @pynvim.command('UTrackerStop', nargs='*', sync=True)
    def stop_logger(self, args):
        try:
            self.logger.stop()
            self.vim.api.notify('Logger stopped', 2, {})
        except Exception as e:
            self.vim.api.notify(f'Logger failed: {e}', 4, {})

    @pynvim.autocmd('VimLeavePre', pattern='*')
    def vim_leave_handler(self):
        self.logger.stop()

    @pynvim.autocmd('InsertEnter', pattern='*', sync=False)
    def insert_enter_handler(self):
        try:
            # self.logger.pause()
            self.vim.api.notify('Logger paused', 2, {})
        except Exception:
            pass

    @pynvim.autocmd('InsertLeave', pattern='*', sync=False)
    def insert_leave_handler(self):
        try:
            # self.logger.resume()
            self.vim.api.notify('Logger resumed', 2, {})
        except Exception:
            pass

    @pynvim.autocmd('FocusLost', pattern='*', sync=False)
    def vim_focus_lost_handler(self):
        try:
            self.logger.resume()
            self.vim.api.notify('Logger resumed', 2, {})
        except Exception:
            pass

    @pynvim.autocmd('FocusGained', pattern='*', sync=False)
    def vim_focus_gained_handler(self):
        try:
            if self.vim.api.get_mode() == 'Insert':
                self.logger.pause()
            else:
                self.logger.resume()
        except Exception:
            pass

    @pynvim.function('Func')
    def logger_start_func(self, args):
        try:
            self.logger.start()
            self.vim.api.notify('Logger started', 2, {})
        except Exception as e:
            self.vim.api.notify(f'Logger failed: {e}', 4, {})

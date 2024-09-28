import pynvim

from logger.logger import Logger, LoggerException


@pynvim.plugin
class LoggerPlugin(object):
    def __init__(self, vim):
        self.vim = vim
        self.calls = 0
        self.logger = Logger("nvim")

    @pynvim.command("Cmd", range="", nargs="*", sync=True)
    def command_handler(self, args, range):
        self._increment_calls()
        self.vim.current.line = "Command: Called %d times, args: %s, range: %s" % (
            self.calls,
            args,
            range,
        )

    @pynvim.command("LoggerRun", nargs="*", sync=True)
    def start_logger(self, args):
        try:
            self.logger.start()
            self.vim.api.notify("Logger started", 2, {})
        except LoggerException as e:
            self.vim.api.notify(f"Logger failed: {e}", 4, {})

    @pynvim.autocmd("VimLeave", pattern="*")
    def stop_logger(self):
        self.logger.stop()

    @pynvim.autocmd("InsertEnter", pattern="*", sync=False)
    def insert_enter_handler(self):
        self.logger.pause()

    @pynvim.autocmd("InsertLeave", pattern="*", sync=False)
    def insert_leave_handler(self):
        self.logger.resume()

    @pynvim.function("Func")
    def function_handler(self, args):
        self._increment_calls()
        self.vim.current.line = "Function: Called %d times, args: %s" % (
            self.calls,
            args,
        )

    def _increment_calls(self):
        if self.calls == 5:
            raise Exception("Too many calls!")
        self.calls += 1

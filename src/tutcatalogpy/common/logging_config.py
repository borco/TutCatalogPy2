import logging
import sys
from typing import Final

from tutcatalogpy.common.logging_handler import LoggingHandler

GUI_FORMATTER_VERBOSE_FORMAT: Final[str] = """
<div>
    <div class="header">
        <span class="levelname {levelname}">&nbsp;{levelname} : {name}&nbsp;</span>
        <span class="time">{asctime}</span>
        <span class="source">{pathname}:{lineno}</span>
    </div>
    <div class="message">{message}</div>
</div>
"""

GUI_FORMATTER_DEFAULT_FORMAT: Final[str] = """
<tr>
    <td width="80" class="levelname">{levelname}</td>
    <td class="message">{message} <span class="defaultname">{name}:{lineno}</span></td>
</tr>
"""

GUI_FORMATTER_EXCEPTION_FORMAT: Final[str] = """<pre class="exception_info">%s</pre>"""

GUI_FORMATTER_DURATION_FORMAT: Final[str] = """<td width="80"></td><td class="duration" width="80">%s</td><td width="5"></td><td>%s</td>"""

GUI_FORMATTER_RAW_HTML_FORMAT: Final[str] = """<pre class="code">\n%s\n</pre>"""

DURATION_LEVEL_NUM: Final[int] = 25
logging.addLevelName(DURATION_LEVEL_NUM, "DURATION")

RAW_HTML_LEVEL_NUM: Final[int] = 26
logging.addLevelName(RAW_HTML_LEVEL_NUM, "RAW_HTML")


def duration(self, duration: str, filename: str):
    # Yes, logger takes its '*args' as 'args'.
    self._log(DURATION_LEVEL_NUM, '%12s | %s', (duration, filename))


def raw_html(self, code: str) -> None:
    self._log(RAW_HTML_LEVEL_NUM, code, ())


logging.Logger.duration = duration
logging.Logger.raw_html = raw_html


class GuiFormatter(logging.Formatter):

    def __init__(self, format):
        super().__init__(fmt=format, datefmt='%H:%M:%S', style='{')

    def format(self, record: logging.LogRecord) -> str:
        if record.levelno == DURATION_LEVEL_NUM:
            tokens = record.getMessage().split('|')
            tokens = list(filter(None, tokens))  # removes empty tokens
            if len(tokens) == 2:
                duration, filename = tokens
                return GUI_FORMATTER_DURATION_FORMAT % (duration, filename)
            return super().format(record)
        elif record.levelno == RAW_HTML_LEVEL_NUM:
            text = record.getMessage()
            text = (
                text
                .replace('<', '＜')
                .replace('>', '＞')
                .replace('&', '＆')
            )
            return GUI_FORMATTER_RAW_HTML_FORMAT % (text,)
        return super().format(record)

    def formatException(self, exc_info) -> str:
        message = super().formatException(exc_info)
        return GUI_FORMATTER_EXCEPTION_FORMAT % message


class SqlFilter(logging.Filter):
    def __init__(self, level: int = logging.INFO):
        super().__init__()
        self.level: int = level
        self.enabled: bool = False

    def filter(self, record: logging.LogRecord) -> bool:
        return (
            not record.name.startswith('sqlalchemy.engine') or (
                self.enabled and
                record.levelno >= self.level
            )
        )


console_formatter = logging.Formatter(
    fmt="""{levelname:10} {message:100} {asctime:<10} {pathname}:{lineno}""",
    datefmt='%H:%M:%S',
    style='{'
)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(console_formatter)

gui_formatter = GuiFormatter(GUI_FORMATTER_DEFAULT_FORMAT)
gui_handler = LoggingHandler()
gui_handler.setFormatter(gui_formatter)

app_logger = logging.getLogger()
app_logger.setLevel(logging.INFO)
app_logger.addHandler(gui_handler)
app_logger.addHandler(console_handler)

sql_logger = logging.getLogger('sqlalchemy.engine')
sql_logger.setLevel(logging.INFO)
sql_filter = SqlFilter()

console_handler.addFilter(sql_filter)
gui_handler.addFilter(sql_filter)

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def toggle_debug(checked: bool) -> None:
    app_logger.setLevel(logging.DEBUG if checked else logging.INFO)
    log.info('%s DEBUG logging', 'Enabled' if checked else 'Disabled')


def toggle_verbose(checked: bool) -> None:
    global gui_formatter
    gui_formatter = GuiFormatter(GUI_FORMATTER_VERBOSE_FORMAT if checked else GUI_FORMATTER_DEFAULT_FORMAT)
    gui_handler.setFormatter(gui_formatter)
    log.info('%s VERBOSE logging', 'Enabled' if checked else 'Disabled')


def toggle_sql(checked: bool) -> None:
    sql_filter.enabled = checked
    log.info('%s SQL logging.', 'Enabled' if checked else 'Disabled')


if __name__ == '__main__':
    from tutcatalogpy.viewer.main import run

    run()

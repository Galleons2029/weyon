import os


class BaseConfig(type):
    """这个配置类的元类使得配置能够和环境变量结合，这样便于docker等容器化部署时进行单项配置"""

    def __new__(cls, name, bases, attrs):
        for key, value in attrs.items():
            if key in os.environ and not callable(value):
                attrs[key] = os.environ[key]
        return type.__new__(cls, name, bases, attrs)


def logs_config():
    import logging

    import coloredlogs

    FIELD_STYLES = dict(
        asctime=dict(color='green'),
        name=dict(color='blue'),
        filename=dict(color='magenta'),
        pathname=dict(color='magenta'),
        lineno=dict(color='yellow'),
        levelname=dict(color='cyan', bold=True),
        processName=dict(color='green', bold=True),
    )
    """Mapping of log format names to default font styles."""

    LEVEL_STYLES = dict(
        debug=dict(color='blue'),
        info=dict(color='green'),
        warning=dict(color='yellow'),
        error=dict(color='red'),
        critical=dict(background='red', bold=True),
    )

    basic_format = '{asctime} - {module:^20} - {name:^20} - {filename}[line:{lineno}] - [{levelname}]: {message}'

    basic_format_colored = coloredlogs.ColoredFormatter(
        fmt=basic_format,
        style='{',
        level_styles=LEVEL_STYLES,
        field_styles=FIELD_STYLES
    )

    def __console_handle():
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(basic_format_colored)
        return console_handler

    def __file_handle(filename):
        file_handler = logging.FileHandler(filename, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter(basic_format, style='{'))
        return file_handler

    handlers = [__console_handle()]
    logging.basicConfig(level=logging.DEBUG,
                        format=basic_format,
                        style="{",
                        handlers=handlers)

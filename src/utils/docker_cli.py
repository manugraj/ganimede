import json
from enum import Enum
from string import Template

import delegator
from cleantext import clean

from src.model.message import Status

DEFAULT_DELIMITER = "NL_CMD"


class ResponseFormat(Enum):
    JSON = "JSON"
    STRING = "STRING"


class CommandType(Enum):
    docker = "docker"
    docker_compose = "docker-compose"


_COMMANDS = {
    CommandType.docker: {
        1: {
            "type": ResponseFormat.JSON,
            "command": 'docker $command --format="{{json .}}"$delimiter'
        },
        2: {
            "type": ResponseFormat.STRING,
            "command": 'docker $command'
        }
    },
    CommandType.docker_compose: {
        1: {
            "type": ResponseFormat.STRING,
            "command": 'docker-compose $command'
        }
    }
}


def docker(command):
    return _exe_and_parse(CommandType.docker, command)


def _parse_result(cmd_type: CommandType, command, format_type, response, return_code):
    response_data = {"command": f"{cmd_type.value} {command}",
                     "status": f"{Status.SUCCESS.value if return_code == 0 else Status.FAILURE.value}",
                     "type": format_type.value, "data": []}
    if format_type == ResponseFormat.JSON:
        for x in response.split(DEFAULT_DELIMITER):
            if x and len(x) > 3:
                try:
                    response_data["data"].append(json.loads(x))
                except ValueError:
                    response_data["data"] = _clean(response)
                    response_data["type"] = ResponseFormat.STRING.value
    else:
        response_data["data"] = _clean(response)
    return response_data


def docker_compose(command):
    return _exe_and_parse(CommandType.docker_compose, command)


def _exe_and_parse(cmd_type, command):
    format_type, return_code, response = _run(cmd_type, command, DEFAULT_DELIMITER)
    return _parse_result(cmd_type, command, format_type, response, return_code)


def _run(cmd_type: CommandType, command: str, formatter: str, exe_count: int = 1):
    command_tmpl = _COMMANDS[cmd_type][exe_count]
    cmd = delegator.run(Template(command_tmpl["command"]).substitute(command=command, delimiter=formatter))

    if cmd.return_code == 0:
        return command_tmpl["type"], 0, cmd.out

    if exe_count >= len(_COMMANDS[cmd_type]):
        return ResponseFormat.STRING, cmd.return_code, cmd.err

    return _run(cmd_type, command, formatter, exe_count + 1)


def _clean(response):
    return clean(response,
                 fix_unicode=True,
                 to_ascii=True,
                 lower=False,
                 no_line_breaks=False,
                 no_urls=False,
                 no_emails=False,
                 no_phone_numbers=False,
                 no_numbers=False,
                 no_digits=False,
                 no_currency_symbols=False,
                 no_punct=False,
                 replace_with_punct="",
                 lang="en"
                 )

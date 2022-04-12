#!/usr/bin/env python3

# TODO: replace dumb sleep with better confirmation of available terminal
# TODO: automatically start tmux session, if it hasn't been started
# TODO: if tmux session isn't attached to in process list, automatically start terminal emulator

# https://docs.platformio.org/en/latest//scripting/custom_targets.html#examples
import os
import shlex
import sys
import time
import traceback
from pathlib import Path
from typing import Union, List, Optional

import libtmux
from libtmux import Session, Pane


def escape_args(args: List[str]) -> str:
    return ' '.join(shlex.quote(arg) for arg in args)


def system(string):
    print(f'Running cmd string: {string}')
    result = os.system(string)
    print('Done')
    return result


def run(cmd_path: Union[str, Path], args: List[str]) -> int:
    """
    'Safely' executes an arbitrary system command, making sure to escape every argument.
    Note: does not escape cmd path.
    :param cmd_path: Path to command to execute
    :param args: Arguments to pass to target command
    :return: Status code of program
    """
    cmd_string = str(cmd_path) + ' ' + escape_args(args)
    return system(cmd_string)


def pathstr(path: Path):
    """" Converts Path to string and normalizes by adding trailing /
    This ensures that rsync doesn't get confused when recursively copying directories
    :param path: The path upon which we will operate
    """
    path = str(path)
    if path[-1] == '/':
        return path
    else:
        return path + '/'


class ConnectSerialMonitorOnTmux:
    def __init__(self, port, baud):
        self.port = port
        self.baud = baud

    @staticmethod
    def get_session(session_name: str = 'clion') -> Optional[Session]:
        """
        Purpose:
        Try to connect to a session. Handle possible exceptions.

        :param session_name: The name of the Tmux session to which we must attempt connection
        :return: The session object, OR none if we failed to connect
        """
        # noinspection PyUnresolvedReferences
        try:
            server = libtmux.Server()
            return server.find_where({"session_name": session_name})
        except libtmux.exc.LibTmuxException as e:
            print('FAILED! Is the session open?')
            exc_type, exc_value, exc_traceback = sys.exc_info()
            # noinspection PyTypeChecker
            traceback.print_exception(exc_type, exc_value, exc_traceback,
                                      limit=2, file=sys.stdout)
            return None

    def run_from_pane(self, pane: Pane):
        """
        # Purpose:
        Restarts our remote GUI program for quick & easy testing cycles

        # Behavior:
        Sends our commands to do the following:
        - Ctrl+C multiple times to make sure the terminal has nothing running inside
        - cd to build directory on remote device
        - Run our compiled binary

        :param pane: The pane to which we send our commands
        :return: None
        """
        for i in range(3):
            print('Sending Ctrl+C...')
            pane.cmd('send-keys', 'C-c')  # Ctrl+C to make sure console is clear
        time.sleep(0.01)
        pane.send_keys(f'pio device monitor --raw --port {self.port} --baud {self.baud}')

    # noinspection PyBroadException
    def do_server_script(self) -> None:
        """
        Iterates through sessions & panes, and calls run_from_pane() against each until one works
        :return:
        """
        session = self.get_session()
        if session is None:
            print('Opening session has failed. Goodbye.')
            exit(1)

        for window in session.list_windows():
            print(f'Window found: {window}')
            for pane in window.list_panes():
                print(f'Pane found: {pane}')
                try:
                    if self.run_from_pane(pane):
                        return
                except Exception as e:
                    print(
                        'Exception encountered on pane. If there is an alternative, we will try the next one. '
                        'Traceback:')
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    # noinspection PyTypeChecker
                    traceback.print_exception(exc_type, exc_value, exc_traceback,
                                              limit=2, file=sys.stdout)


def main(*args, **kwargs):
    """
    Program entrypoint
    :return:
    """
    port: str = ''
    baud: str = ''

    port = env.GetProjectOption("port")
    baud = env.GetProjectOption("monitor_speed")

    is_path: bool = False
    port_path = Path(port)
    port_path_test = port_path
    for i in range(3):
        if port_path_test.exists():
            is_path = True
            break
        port_path_test = port_path_test.parent

    if is_path:
        while True:
            try:
                port_path.open('r')
                break
            except FileNotFoundError:
                time.sleep(0.1)

    # print('Reading platformio.ini...')
    # config = configparser.ConfigParser()
    # config.read('platformio.ini')
    # for section in config.sections():
    #     for key in config[section].keys():
    #         value = config[section][key]
    #         print(f'{key.strip()}: {value.strip()}')
    #         if key == 'port':
    #             port = value
    #         if key == 'monitor_baud':
    #             baud = value

    run_tmux = ConnectSerialMonitorOnTmux(port, baud)
    run_tmux.do_server_script()


Import("env")

env.AddCustomTarget(name="tmux-monitor", dependencies=["upload"], actions=main)

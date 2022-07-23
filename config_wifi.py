import logging
import PySimpleGUI as sg


def config_wifi(scan_data):
    if sg.running_linux():
        sg.execute_command_subprocess("wicd-gtk", wait=False, cwd=None, pipe_output=False)
    elif sg.running_mac():
        sg.execute_command_subprocess('open', 'x-apple.systempreferences:com.apple.preference.network', wait=False, cwd=None, pipe_output=False)
    else:
        logging.ERROR("This software is only designed to run on Linux and MacOS")
    return


if __name__ == '__main__':
    scan_data = "test info"
    config_wifi(scan_data)

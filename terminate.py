import PySimpleGUI as sg
import sys


##############################################################################################################
#          EXIT BUTTON PRESSED   (or window closed)                                                          #
##############################################################################################################
def terminate(number, msg):
    if sg.running_linux():
        # REBOOT ON EXIT BECAUSE USER SHOULD NEVER BE GIVEN ACCESS TO THE LINUX OS!!!
        response = sg.execute_command_subprocess("echo", "'Use4Sonautics!' | sudo -S shutdown -r now",
                                                 wait=True, pipe_output=True)
        print(response)
        sys.exit(f'{number}: {msg}')
    else:
        # Just exit for macOS because Mac user may be running other applications!!
        sys.exit(f'{number}: {msg}')


if __name__ == '__main__':
    terminate(-1, "Testing terminate()")

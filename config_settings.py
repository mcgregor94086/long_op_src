__author__ = ''
import PySimpleGUI as sg
from GUI_defs import settings_layout


def config_settings(scan_data):
    window = scan_data['window']
    settings_window = sg.Window('SonaScan Settings', settings_layout)
    window['_ACTION_STATUS_LINE_1_'].update("Editing Settings...")
    window.Refresh()
    while True:
        settings_event, settings_values = settings_window.read()
        print(settings_event, settings_values)
        if settings_event == sg.WIN_CLOSED or settings_event == 'Exit' or settings_event == 'Cancel':
            break
        elif settings_event == 'Submit':
            print(settings_values)
            scan_data['simulate_uploading'], scan_data['simulate_modeling'], \
            scan_data['show_images_html'],  scan_data['show_3D_model'] = settings_values
            break
    settings_window.close()
    # window.write_event_value('-END SETTINGS-', scan_data)
    return scan_data

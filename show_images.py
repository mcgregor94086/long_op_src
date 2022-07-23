__author__ = ''

import os
import webbrowser

from scandir_index_maker import scandir_index_maker


def show_images(scan_data):
    print(f'\nENTERING show_images({scan_data})')

    scan_dir = scan_data['scan_dir']
    # print(f'show_images(): scan_dir = {scan_dir}')
    # print('show_images(): show_images()', scan_data)
    scandir_index_maker(scan_data)
    url_to_show = 'file://' + os.path.join(os.path.realpath(scan_data['scan_dir']),'index.html')
    print(f'17: show_images(): scan_dir = {os.path.realpath(scan_data["scan_dir"])}')
    webbrowser.open(url_to_show)

    print(f'EXITING show_images({scan_data})\n')
    return


if __name__ == '__main__':
    scan_data = {'scan_dir': '/sonautics/data/DEMO/index.html'}
    show_images(scan_data)

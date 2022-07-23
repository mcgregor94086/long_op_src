
# ############################## DEFINE AND SET UP WORKING DIRECTORIES IF THEY DON'T EXIT #########################
import os
from pathlib import Path

sonautics_root_dir_path = '/sonautics'
try:
    os.makedirs(sonautics_root_dir_path, mode=770, exist_ok=True)
except OSError as error:
    print("Directory '%s' can not be created")

sonautics_data_dir_path = os.path.join(sonautics_root_dir_path, 'data')
try:
    os.makedirs(sonautics_data_dir_path, mode=770, exist_ok=True)
except OSError as error:
    print("Directory '%s' can not be created")

sonautics_logs_dir_path = os.path.join(sonautics_root_dir_path, 'logs')
try:
    os.makedirs(sonautics_logs_dir_path, mode=770, exist_ok=True)
except OSError as error:
    print("Directory '%s' can not be created")

sonautics_scans_dir_path = os.path.join(sonautics_data_dir_path, 'scans')
try:
    os.makedirs(sonautics_logs_dir_path, mode=770, exist_ok=True)
except OSError as error:
    print("Directory '%s' can not be created")

demo_dir = os.path.join(sonautics_scans_dir_path, 'DEMO')
try:
    os.makedirs(demo_dir, mode=770, exist_ok=True)
except OSError as error:
    print("Directory '%s' can not be created")

# local file paths
src_dir = os.path.join(sonautics_root_dir_path, "src")
data_dir = os.path.join(sonautics_root_dir_path, "data")
Path(data_dir).mkdir(parents=True, exist_ok=True)
db_dir = os.path.join(data_dir, "db")
deferred_dir = os.path.join(data_dir, "deferred")
scans_dir = os.path.join(data_dir, "scans")
Path(scans_dir).mkdir(parents=True, exist_ok=True)
demo_dir = os.path.join(scans_dir, "DEMO")
demo_photoscene_dir = os.path.join(demo_dir, "photoscene-DEMO")
demo_stl = os.path.join(demo_photoscene_dir, "OZDNR.stl")
# /Volumes/rootfs/sonautics/data/DEMO/photoscene-DEMO/OZDNR.STL
failed_dir = os.path.join(data_dir, "failed")
logs_dir = os.path.join(data_dir, "logs")
models_dir = os.path.join(data_dir, "models")
releases_dir = os.path.join(sonautics_root_dir_path, "sonascan_releases")
current_src_target = os.path.join(releases_dir,"current_src")
fallback_src_target = os.path.join(releases_dir, "fallback_src")
# current_src_real_dir = os.readlink(current_src_target)
# fallback_src_real_dir = os.readlink(fallback_src_target)

images_dir = os.path.join(sonautics_root_dir_path, "images")

templates_dir = os.path.join(sonautics_root_dir_path, "templates")
order_pdf_file = os.path.join(templates_dir, 'Microsonic-Hearing-Protection-Order-Form-Fillable.pdf')
view_stl_file = os.path.join(templates_dir, 'view_stl_file.html')

# ############################## END WORKING DIRECTORIES DEFINITION #########################

# SonaServer  file paths
SERVER_USERNAME = 'scansteruser'
SERVER_HOSTNAME = 'cloud1.tri-di.com'
SERVER_WEB_ROOT = SERVER_USERNAME + '@' + SERVER_HOSTNAME + ':' + SERVER_HOSTNAME + '/'
SERVER_DATA_PATH = SERVER_WEB_ROOT + 'sonautics/data/'
SERVER_SCAN_DIR_ROOT_PATH = os.path.join(SERVER_DATA_PATH, 'scans/')
SERVER_UPLOAD_DIR_ROOT_PATH = os.path.join(SERVER_DATA_PATH, 'uploaded/')
SERVER_MODEL_ROOT_PATH = os.path.join(SERVER_DATA_PATH, 'models/')
SERVER_FAILED_ROOT_PATH = os.path.join(SERVER_DATA_PATH, 'failed/')
SERVER_DB_ROOT_PATH = os.path.join(SERVER_DATA_PATH, 'db/')
SERVER_DEFERRED_ROOT_PATH = os.path.join(SERVER_DATA_PATH, 'deferred/')
SERVER_DEMO_ROOT_PATH = os.path.join(SERVER_DATA_PATH, 'DEMO/')
SERVER_LOGS_ROOT_PATH = os.path.join(SERVER_DATA_PATH, 'logs/')
SERVER_RELEASES_ROOT_PATH = os.path.join(SERVER_WEB_ROOT, 'sonautics/sonascan_releases/')
HOST_RELATIVE_RELEASES_ROOT_PATH = os.path.join(SERVER_HOSTNAME, 'sonautics/sonascan_releases')
SERVER_IMAGES_ROOT_PATH = os.path.join(SERVER_WEB_ROOT, 'sonautics/images/')
SERVER_SRC_ROOT_PATH = os.path.join(SERVER_WEB_ROOT, 'sonautics/src/')
SERVER_TEMPLATES_ROOT_PATH = os.path.join(SERVER_WEB_ROOT, 'sonautics/templates/')

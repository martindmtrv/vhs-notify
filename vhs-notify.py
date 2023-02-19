import obspython as obs
import os
import random
from PIL import Image
import requests

# ------
delay = 10
ntfy_server = ""
pixels = 10
# ------


# Description displayed in the Scripts dialog window
def script_description():
  return """VHS Recording Automater!
    Will start recording when something is present on the frame and stop when it detects static or blue screen
  """

"""
  This function will force OBS to screenshot the current preview, then load it into memory and delete the fs screenshot
"""
def extract_screenshot():
  # potential race condition? I don't know if this is blocking call
  obs.obs_frontend_take_screenshot()
  fp = obs.obs_frontend_get_last_screenshot()


  # open the ss and store FULLY in memory
  img = Image.open(fp)
  img.load()

  # delete it from fs
  os.remove(fp)

  return img

"""
This function will select n random pixels from the center/upper line of the screen and return them
"""
def get_random_central_pixels(n: int, w: int, h: int) -> list:
  pixels = []
  for _ in range(n):
    x = random.randint(w)
    y = random.randint(h)

    pixels.append((x, y))

  return pixels

def is_blueish(p: tuple) -> bool:
  # approx check for blue
  return p[0] <= 10 and p[2] >= 135 and p[2] <= 145 and p[1] < 5

def is_static(p: tuple) -> bool:
  # approx check for static 
  return p[0] == p[1] and p[1] == p[2]

# Called at script unload
def script_unload():
  print("Unloading")
  # restore_sceneitem_after_shake()

# Called to set default values of data settings
def script_defaults(settings):
  obs.obs_data_set_default_int(settings, "delay", 10)
  obs.obs_data_set_default_int(settings, "pixels", 10)
  obs.obs_data_set_default_string(settings, "ntfy_server", "")

# Called to display the properties GUI
def script_properties():
  props = obs.obs_properties_create()

  obs.obs_properties_add_int_slider(props, "delay", "Refresh Rate (s)", 1, 30, 1)
  obs.obs_properties_add_int_slider(props, "pixels", "Number of Pixels to Check (higher is less false positives)", 5, 100, 5)
  obs.obs_properties_add_text(props, "ntfy_server", "Ntfy Server Topic URL (optional for notifications)", obs.OBS_TEXT_DEFAULT)

  return props

# Called after change of settings including once after script load
def script_update(settings):
  global delay, ntfy_server, pixels
  ntfy_server = obs.obs_data_get_string(settings, "ntfy_server")
  pixels = obs.obs_data_get_int(settings, "pixels")
  delay = obs.obs_data_get_int(settings, "delay")

# Global animation activity flag
is_active = False

def ss_check_callback():
  ss = extract_screenshot()

  pixels = get_random_central_pixels(pixels, ss.size[0], ss.size[1])
  isEndBlue = True
  isStatic = True
  
  # check if all pixels are blueish -> signalling end of tape
  for p in pixels:
    if not is_blueish(ss.getpixel(p)):
      isEndBlue = False
      break

  # check if all static
  for p in pixels:
    if not is_static(ss.getpixel(p)):
      isStatic = False
      break

  if isEndBlue:
    requests.post(ntfy_server, data="VHS Recording hit End Blue; stopping recording")
    print("notify end blue; stopping recording")
    obs.obs_frontend_recording_stop()
    return


  if isStatic:
    requests.post(ntfy_server, data="VHS Recording hit Static; stopping recording")
    print("notify isstatic, stop recording")
    obs.obs_frontend_recording_stop()
    return
  
  if not obs.obs_frontend_recording_active():
    requests.post(ntfy_server, data="VHS Recording Starting up again")
    print("notify recording start, start recording")
    obs.obs_frontend_recording_start()

# Callback for the hotkey
def on_auto_record_hotkey(pressed):
  global is_active
  is_active = pressed

  if is_active:
    timer_add(delay * 1000, ss_check_callback)
  else:
    timer_remove(ss_check_callback)

# Identifier of the hotkey set by OBS
hotkey_id = obs.OBS_INVALID_HOTKEY_ID

# Called at script load
def script_load(settings):
  global hotkey_id
  hotkey_id = obs.obs_hotkey_register_frontend(script_path(), "VHS Auto-Record", on_auto_record_hotkey)
  hotkey_save_array = obs.obs_data_get_array(settings, "autorecord_hotkey")
  obs.obs_hotkey_load(hotkey_id, hotkey_save_array)
  obs.obs_data_array_release(hotkey_save_array)

# Called before data settings are saved
def script_save(settings):
  obs.obs_save_sources()

  # Hotkey save
  hotkey_save_array = obs.obs_hotkey_save(hotkey_id)
  obs.obs_data_set_array(settings, "autorecord_hotkey", hotkey_save_array)
  obs.obs_data_array_release(hotkey_save_array)
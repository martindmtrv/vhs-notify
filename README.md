# VHS-Notify OBS Plugin
This plugin for OBS allows you to stop and start recording automatically for digitizing old content easier. To setup ensure python is installed and accessible by OBS then import the script. To enable it, you must set a keybinding and toggle it (can use script log to see more info on toggle). You should also determine what RGB approximate values represent the blue screen on your VHS player, since it is not one standard value.

When enabled the script will start recording if it is not already whenever the current preview is not a blue screen or static. If it is already recording and it hits a blue screen or static, it will stop recording and send a POST req to ntfy_server

# Configuration
|Name|Explanation|
|---|---|
|delay|Sets how often to check the preview screen|
|pixels|how many pixels to verify in the screenshot|
|ntfy_server|custom ntfy server for notifications, after an event happens a POST request will be sent to this URL with the event details|
|approx_R|approximate RED value in RGB to represent blue screen|
|approx_G|approximate GREEN value in RGB to represent blue screen|
|approx_B|approximate BLUE value in RGB to represent blue screen|
|alpha|what tolerance to match the approximate color values|
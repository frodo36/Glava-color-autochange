from subprocess import Popen
from time import sleep
import psutil
from color_palette import ColorPalette
from string import digits, ascii_lowercase
from subprocess import check_output

chars = digits + ascii_lowercase + "#"

def process():
    PROCNAME = "glava"
    for proc in psutil.process_iter():
        if proc.name() == PROCNAME:
            proc.kill()

def start(prev_file):
    print("starting")
    while True:
        file = list(check_output(["gsettings get org.gnome.desktop.background picture-uri"], shell=True).decode())
        file = file[8:-2]
        str_file = ""
        for x in file:
            str_file += x
        file = str_file
        if not prev_file == file:
            prev_file = file
            print("wallpaper changed")
            print(file)
            print(prev_file)
            try:
                if not prev_file == file:
                    print("restarting")
                    start(prev_file)
                else:
                    print("trying to find hex")
                    hex_color = str((ColorPalette(file, 1, 'hex')))
            except:
                print("failed, retrying")
                start(prev_file)
            print("succeed")
            final_hex_color = ""
            for x in hex_color:
                if x in chars:
                    final_hex_color += x
            print(final_hex_color)
            glava_config_file = "/home/merlijn/.config/glava/bars.glsl"
            with open(glava_config_file, 'r') as glava_file:
                data = glava_file.readlines()
            data[22] = f"#define COLOR ({final_hex_color} * GRADIENT)\n"
            with open(glava_config_file, 'w') as glava_file:
                glava_file.writelines(data)
            process()
            Popen("glava --desktop", shell=True)
            print("new glava session started")
            print("restarting...")
            start(prev_file)
        
prev_file = "0"
start(prev_file)



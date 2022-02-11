from __future__ import print_function
from subprocess import Popen
from os import system
try:
    import psutil
except:
    system("pip install psutil")
from string import digits, ascii_lowercase
from subprocess import check_output
import binascii
from PIL import Image
import numpy as np
try:
    import scipy
except:
    system("pip install scipy")
import scipy.misc
import scipy.cluster
from os import getlogin
from os import path

chars = digits + ascii_lowercase + "#"

if not path.exists(f"/home/{getlogin()}/.config/glava/bars.glsl"):
    print("Glava config file not found, glava not installed")
    input("Press any key to install...")
    system("git clone https://github.com/jarcode-foss/glava")
    system("cd glava")
    system("meson build --prefix /usr")
    system("ninja -C build")
    system("sudo ninja -C build install",)

def process():
    PROCNAME = "glava"
    for proc in psutil.process_iter():
        if proc.name() == PROCNAME:
            proc.kill()

def get_hex(file):
    NUM_CLUSTERS = 5
    im = Image.open(file)
    im = im.resize((150, 150))      # optional, to reduce time
    ar = np.asarray(im)
    shape = ar.shape
    ar = ar.reshape(scipy.product(shape[:2]), shape[2]).astype(float)
    codes, dist = scipy.cluster.vq.kmeans(ar, NUM_CLUSTERS)
    vecs, dist = scipy.cluster.vq.vq(ar, codes)         # assign codes
    counts, bins = scipy.histogram(vecs, len(codes))    # count occurrences
    index_max = scipy.argmax(counts)                    # find most frequent
    peak = codes[index_max]
    colour = binascii.hexlify(bytearray(int(c) for c in peak)).decode('ascii')
    hex = "#" + colour
    print(hex)
    return hex

def start(prev_file):
    print("starting")
    while True:
        try:
            file = list(check_output(["gsettings get org.gnome.desktop.background picture-uri"], shell=True).decode())
        except:
            start(prev_file)
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
            print("trying to find hex")
            try:
                hex_color = get_hex(file)
            except:
                hex_color = get_hex(file)
            print("succeed")
            final_hex_color = ""
            for x in hex_color:
                if x in chars:
                    final_hex_color += x
            print(final_hex_color)
            glava_config_file = f"/home/{getlogin()}/.config/glava/bars.glsl"
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



#!/usr/bin/python3

# https://github.com/ppannuto/python-saleae
# pip3 install saleae
import saleae

# Set to localhost if Logic is running on the same computer that you are
# running the script on.
#host = "192.168.178.19"
host = "localhost"

s = saleae.Saleae(host=host)
s.capture_start()


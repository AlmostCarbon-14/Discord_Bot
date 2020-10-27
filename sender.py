#!/usr/bin/env python3

import yagmail
import os
import re

app_pass = "mezbhouyxgkhxadh"

send_addr = "conor4508@gmail.com"

recv_addr = "conor4508@gmail.com"

subject = "New RPI Address!"

os.system("ip address > addr.txt")

with open('addr.txt', 'r') as file:
    text = file.read()

text = re.findall(r'[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}\/[0-9]{1,3}', text)

with yagmail.SMTP(send_addr, app_pass) as yag:
    yag.send(recv_addr, subject, text)
    print("Email Sent")

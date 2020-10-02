#!/usr/bin/env python3

import yagmail
import os


app_pass = "mezbhouyxgkhxadh"

send_addr = "conor4508@gmail.com"

recv_addr = "conor4508@gmail.com"

subject = "New RPI Address!"

os.system("ip address > addr.txt")

with open('addr.txt', 'r') as file:
    text = file.read()

with yagmail.SMTP(send_addr, app_pass) as yag:
    yag.send(recv_addr, subject, text)
    print("Email Sent")


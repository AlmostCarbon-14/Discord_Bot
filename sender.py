#!/usr/bin/env python3

import yagmail

app_pass = "mezbhouyxgkhxadh"

send_addr = "conor4508@gmail.com"

recv_addr = "conor4508@gmail.com"

subject = "[Discord Bot Error Detected]"

text = ("*" * 45) + "\n" + "Error Message"

with yagmail.SMTP(send_addr, app_pass) as yag:
    yag.send(recv_addr, subject, text)
    print("Email Sent")


# Copyright (c) 2023 Jan Feldhoff
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import threading
import tkinter as tk
import serial.tools.list_ports
import customtkinter as ctk
import tkinter.messagebox


from MCP_Functions import *
#from GUI_Functions import *

ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


# needed libs (pip install)
# pyserial
# canopen
# tkinter (python native)
# customtkinter

controllers = []

connected = False

def main():
    # ConnectToCan('COM12', 500000)  # standard Baudrate MCP-48-20-02

    # node1 = MCP_Node(126)  # standard NodeId MCP-48-20-02
    #nodes.append(MCP_Node(126))

    # ids 66 and 33

    # node1.ReadFaults()

    from GUI_Functions import app
    app.mainloop()

    # if len(nodes) >= 1:
    #     connected = True

    NetworkDisconnect()


if __name__ == '__main__':
    main()

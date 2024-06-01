import threading
import tkinter as tk
from tkinter import messagebox, ttk, LEFT

import serial.tools.list_ports
import customtkinter as ctk
import tkinter.messagebox

from MCPRegisters import ParameterRegisterData
from MCP_Functions import ConnectToCan, MCP_Node, NetworkDisconnect
from main import controllers

amp_hours = 0


class FELDFaults(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)

        def on_read_button_press():
            error_text = []
            app_text = []
            mot1_text = []
            mot2_text = []
            checked_states = [False] * 7

            # TODO: Brackets are NOT removed correctly (why?)

            for node in controllers:

                faultnum = node.ReadFaults("ErrorRegisterNumber")
                if faultnum is not None:
                    if 1 <= faultnum <= 7:
                        checked_states[faultnum - 1] = True
                # Iterate over the different registers
                for register in ["ErrorRegister", "PreDefinedErrorField", "Application", "Motor1", "Motor2"]:
                    # Read the faults from the current register
                    faults = node.ReadFaults(register)
                    if faults is not None:
                        # Check if faults is a list
                        if isinstance(faults, list):
                            # Iterate over the faults
                            for fault in faults:
                                # Check if fault is a list
                                if isinstance(fault, list):
                                    # Join the elements of fault into a string separated by ' : '
                                    fault = ' : '.join([str(x) for x in fault])
                                else:
                                    # Convert fault to a string
                                    fault = str(fault)
                                # Remove any brackets from fault
                                fault = fault.replace('{', '').replace('}', '').replace('[', '').replace(']',
                                                                                                         '').replace('',
                                                                                                                     '')
                                # Append fault to the appropriate list based on the current register
                                if register == "Application":
                                    app_text.append(node.GetCanID())
                                    app_text.append(": ")
                                    app_text.append(fault)
                                elif register == "Motor1":
                                    mot1_text.append(node.GetCanID())
                                    app_text.append(": ")
                                    mot1_text.append(fault)
                                elif register == "Motor2":
                                    mot2_text.append(node.GetCanID())
                                    app_text.append(": ")
                                    mot2_text.append(fault)
                                elif register == "PreDefinedErrorField":
                                    error_text.append(node.GetCanID())
                                    app_text.append(": ")
                                    error_text.append('\n' + fault)
                                else:
                                    error_text.append(node.GetCanID())
                                    error_text.append(fault)
                        else:
                            # Convert faults to a string and remove any brackets
                            fault = str(faults).replace('{', '').replace('}', '').replace('[', '').replace(']',
                                                                                                           '').replace(
                                '', '')
                            # Append fault to the appropriate list based on the current register
                            if register == "Application":
                                app_text.append(node.GetCanID())
                                app_text.append(": ")
                                app_text.append(fault)
                            elif register == "Motor1":
                                mot1_text.append(node.GetCanID())
                                app_text.append(": ")
                                mot1_text.append(fault)
                            elif register == "Motor2":
                                mot2_text.append(node.GetCanID())
                                app_text.append(": ")
                                mot2_text.append(fault)
                            elif register == "PreDefinedErrorField":
                                error_text.append(node.GetCanID())
                                app_text.append(": ")
                                error_text.append('\n' + fault)
                            else:
                                error_text.append(node.GetCanID())
                                app_text.append(": ")
                                error_text.append(fault)

            update_error_textbox(error_text)
            update_app_textbox(app_text)
            update_mot1_textbox(mot1_text)
            update_mot2_textbox(mot2_text)
            update_checkboxes(checked_states)
            pass

        def on_clear_button_press():

            for node in controllers:
                node.Clear_Errors()
                node.FaultResetMotor("Motor1")
                node.FaultResetMotor("Motor2")

            checked_states = [False] * 7

            update_error_textbox("")
            update_app_textbox("")
            update_mot1_textbox("")
            update_mot2_textbox("")
            update_checkboxes(checked_states)

            update_checkboxes(checked_states)

            pass

        live_timer = threading.Timer(5.0, on_read_button_press)

        def on_live_view_switch_toggle():
            if live_view_switch.get() == 1:
                live_timer.start()
                print("on")
                pass
            else:
                live_timer.cancel()
                print("off")
                pass

        def update_checkboxes(checked_states):
            # Function to update the checked states of the checkboxes
            for CHECKBOX, state in zip(checkboxes, checked_states):
                if state:
                    CHECKBOX.select()
                else:
                    CHECKBOX.deselect()

        def update_error_textbox(text):
            # Function to update the content of the error textbox
            error_textbox.configure(state=ctk.NORMAL)
            error_textbox.delete("1.0", ctk.END)
            error_textbox.insert(ctk.END, text)
            error_textbox.configure(state=ctk.DISABLED)

        def update_app_textbox(text):
            # Function to update the content of the APP textbox
            app_textbox.configure(state=ctk.NORMAL)
            app_textbox.delete("1.0", ctk.END)
            app_textbox.insert(ctk.END, text)
            app_textbox.configure(state=ctk.DISABLED)

        def update_mot1_textbox(text):
            # Function to update the content of the MOT1 textbox
            mot1_textbox.configure(state=ctk.NORMAL)
            mot1_textbox.delete("1.0", ctk.END)
            mot1_textbox.insert(ctk.END, text)
            mot1_textbox.configure(state=ctk.DISABLED)

        def update_mot2_textbox(text):
            # Function to update the content of the MOT2 textbox
            mot2_textbox.configure(state=ctk.NORMAL)
            mot2_textbox.delete("1.0", ctk.END)
            mot2_textbox.insert(ctk.END, text)
            mot2_textbox.configure(state=ctk.DISABLED)

        self.geometry("800x600")  # Set the overall size of the window
        self.title("FELDFaults View")

        # First segment
        first_segment = ctk.CTkFrame(self)
        first_segment.pack(fill=ctk.X)

        read_button = ctk.CTkButton(first_segment, text="READ", command=on_read_button_press)
        read_button.pack(side=ctk.LEFT)

        clear_button = ctk.CTkButton(first_segment, text="CLEAR", command=on_clear_button_press)
        clear_button.pack(side=ctk.LEFT)

        live_view_switch = ctk.CTkSwitch(first_segment, text="Live View", command=on_live_view_switch_toggle)
        live_view_switch.pack(side=ctk.RIGHT)

        # Second segment
        second_segment = ctk.CTkFrame(self)
        second_segment.pack(side=ctk.RIGHT, fill=ctk.Y)

        error_register_label = ctk.CTkLabel(second_segment, text="Error Register")
        error_register_label.pack()

        checkbox_names = ["CURR", "VOLT", "TEMP", "COMM", "DEV", "RES", "MAN"]
        checkboxes = []
        for name in checkbox_names:
            checkbox = ctk.CTkCheckBox(second_segment, text=name, state=ctk.DISABLED)
            checkbox.pack(anchor=ctk.W)
            checkboxes.append(checkbox)

        # Third segment
        third_segment = ctk.CTkFrame(self)
        third_segment.pack(fill=ctk.BOTH, expand=True)

        error_field_label = ctk.CTkLabel(third_segment, text="Error Field")
        error_field_label.pack()

        error_textbox = ctk.CTkTextbox(third_segment, state=ctk.DISABLED)
        error_textbox.pack(fill=ctk.BOTH, expand=True)

        # Fourth segment
        fourth_segment = ctk.CTkFrame(self)
        fourth_segment.pack(fill=ctk.BOTH, expand=True)

        column_frame = ctk.CTkFrame(fourth_segment)
        column_frame.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)  # Stretch the columns to the second segment

        app_label = ctk.CTkLabel(column_frame, text="APP")
        app_label.pack()

        app_textbox = ctk.CTkTextbox(column_frame, state=ctk.DISABLED)
        app_textbox.pack(fill=ctk.BOTH, expand=True)

        column_frame = ctk.CTkFrame(fourth_segment)
        column_frame.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)  # Stretch the columns to the second segment

        mot1_label = ctk.CTkLabel(column_frame, text="MOT1")
        mot1_label.pack()

        mot1_textbox = ctk.CTkTextbox(column_frame, state=ctk.DISABLED)
        mot1_textbox.pack(fill=ctk.BOTH, expand=True)

        column_frame = ctk.CTkFrame(fourth_segment)
        column_frame.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)  # Stretch the columns to the second segment

        mot2_label = ctk.CTkLabel(column_frame, text="MOT2")
        mot2_label.pack()

        mot2_textbox = ctk.CTkTextbox(column_frame, state=ctk.DISABLED)
        mot2_textbox.pack(fill=ctk.BOTH, expand=True)


class FELDConnection(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("FELDConnection")
        self.COM = tk.StringVar(value="can0")
        self.BAUD = tk.StringVar(value="500000")
        self.nodes_to_add = []

        self.connect_button = ctk.CTkButton(self, text="CONNECT CAN", command=self.connect_can)
        self.connect_button.grid(row=2, columnspan=2)

        ctk.CTkLabel(self, text="select COM port").grid(row=0, column=0)
        com_options = [port.device for port in serial.tools.list_ports.comports()]
        self.com_option_menu = ctk.CTkOptionMenu(self, dynamic_resizing=False, values=com_options)
        self.com_option_menu.grid(row=0, column=1)
        if not com_options:
            self.com_option_menu.set("NO COM PORT")
            self.com_option_menu.configure(state=ctk.DISABLED)
            self.connect_button.configure(state=ctk.DISABLED)
        self.com_option_menu.configure(variable=self.COM)

        ctk.CTkLabel(self, text="SET BAUD").grid(row=1, column=0)
        baud_options = [str(x) for x in [10000, 20000, 50000, 100000, 125000, 250000, 500000, 750000, 1000000, 8330]]
        self.baud_option_menu = ctk.CTkOptionMenu(self, dynamic_resizing=False, values=baud_options)
        self.baud_option_menu.grid(row=1, column=1)
        self.baud_option_menu.set("500000")
        self.baud_option_menu.configure(variable=self.BAUD)

        ctk.CTkLabel(self, text="NODES").grid(row=3, columnspan=2)
        self.found_nodes_text = ctk.CTkTextbox(self, height=80)
        self.found_nodes_text.grid(row=4, columnspan=2, sticky="nsew")

        self.add_node_button = ctk.CTkButton(self, text="ADD", command=self.add_node)
        self.add_node_button.grid(row=5, column=0)
        self.add_node_button.configure(state=ctk.DISABLED)
        self.node_entry = ctk.CTkEntry(self)
        self.node_entry.grid(row=5, column=1)

        self.new_button = ctk.CTkButton(self, text="DELETE ALL NODES", command=self.delete_nodes)
        self.new_button.grid(row=5, column=2)

        self.continue_button = ctk.CTkButton(self, text="CONTINUE", command=self.continue_btn)
        self.continue_button.grid(row=6, columnspan=3)
        self.continue_button.configure(state=ctk.DISABLED)

        # DEFAULT VALUES
        self.found_nodes_text.insert("end", "66" + "\n")
        self.nodes_to_add.append(66)
        self.found_nodes_text.insert("end", "126" + "\n")
        self.nodes_to_add.append(126)

    def continue_btn(self):
        try:
            for node_num in self.nodes_to_add:
                new_node = MCP_Node(node_num)
                controllers.append(new_node)
                print(f"node {node_num} added")
                print(new_node.GetNodeState())
            self.destroy()
        except Exception as e:
            self.destroy()
            NetworkDisconnect()
            print(f"One or more nodes not valid: {e}")
            # handle the exception here by displaying a pop-up with the error message
            messagebox.showerror("Error", f"One or more nodes not valid: {e}")

    def connect_can(self):
        result = ConnectToCan("can0", 500000)
        if result == 0:
            self.connect_button.configure(text="CONNECTION OK")
            self.connect_button.configure(state=ctk.DISABLED)
            self.add_node_button.configure(state=ctk.NORMAL)
        elif result == -1:
            tkinter.messagebox.showerror("Error", "CONNECTION ERROR. COULD NOT CONNECT TO CAN")
        if len(self.nodes_to_add) >= 1:
            self.continue_button.configure(state="enabled")

    def add_node(self):
        node_num = int(self.node_entry.get())
        self.nodes_to_add.append(node_num)
        found_nodes_str = str(node_num)
        self.found_nodes_text.insert("end", found_nodes_str + "\n")
        self.node_entry.delete(0, tk.END)
        self.continue_button.configure(state="enabled")

    def delete_nodes(self):
        self.nodes_to_add.clear()
        self.found_nodes_text.delete("1.0", "end")
        self.continue_button.configure(state=ctk.DISABLED)


# END ########################################################


# HERE
class FELDParameter(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("FELDParameter")
        self.geometry("1366x768")
        self.column_weights = [1, 1, 2, 1, 1, 1, 1]
        self.tabs = ["Function", "Communication", "Motor Parameter", "Motor Tune", "Brake"]
        self.entry_widgets = {}

        self.current_controller = None

        # Create a frame to hold the label and drop-down menu
        top_frame = ctk.CTkFrame(self)
        top_frame.pack(side="top", anchor="ne")

        # Create a label and drop-down menu
        select_node_label = ctk.CTkLabel(top_frame, text="SELECT NODE")
        select_node_label.pack(side="left")

        self.controllers = controllers
        controller_ids = [str(controller.GetCanID()) for controller in controllers]
        self.controller_var = ctk.StringVar(value=controller_ids[0])
        self.controller_dropdown = ctk.CTkOptionMenu(top_frame, variable=self.controller_var,
                                                     values=controller_ids,
                                                     command=self.update_controller)
        self.controller_dropdown.pack(side="left")

        # Call the update_controller function manually DEBUG
        self.update_controller(self.controller_var.get())

        # Create tabview
        self.tabframe = ctk.CTkScrollableFrame(self)  # To get the lil fugg to scroll
        self.tabframe.pack(fill="both", expand=True)

        self.tabview = ctk.CTkTabview(self.tabframe)
        self.tabview.pack(fill="both", expand=True)
        for tab in self.tabs:
            self.tabview.add(tab)

        # Configure grid of individual tabs
        for tab in self.tabs:
            for i in range(7):
                weight = self.column_weights[i]
                self.tabview.tab(tab).grid_columnconfigure(i, weight=weight)

            # Create column headers
            headers = ["ID", "SUB", "NAME", "DEFAULT", "RWC_DEFAULT", "CURRENT VALUE", "NEW VALUE"]
            for i, header in enumerate(headers):
                label = ctk.CTkLabel(self.tabview.tab(tab), text=header)
                label.grid(row=0, column=i)
                label.configure(anchor="center")

        # Add content to columns 1-5 from ParameterRegisterData list
        for item in ParameterRegisterData:
            can_id = item[0]
            sub = item[1]
            name = item[2]
            tab = item[3]
            default = item[4]
            rwc_default = item[5]

            frame = self.tabview.tab(tab)
            row = frame.grid_size()[1]

            self.id_label = ctk.CTkLabel(frame, text=hex(can_id))
            self.id_label.grid(row=row, column=0)

            self.sub_label = ctk.CTkLabel(frame, text=sub)
            self.sub_label.grid(row=row, column=1)

            self.name_label = ctk.CTkLabel(frame, text=name)
            self.name_label.grid(row=row, column=2)
            self.name_label.configure(anchor="w")

            self.default_entry = ctk.CTkEntry(frame)
            self.default_entry.insert(ctk.END, default)
            self.default_entry.configure(state="readonly")
            self.default_entry.grid(row=row, column=3)
            self.default_entry.configure(width=70)

            self.rwc_default_entry = ctk.CTkEntry(frame)
            self.rwc_default_entry.insert(ctk.END, rwc_default)
            self.rwc_default_entry.configure(state="readonly")
            self.rwc_default_entry.grid(row=row, column=4)
            self.rwc_default_entry.configure(width=70)

            self.current_value_entry = ctk.CTkEntry(frame)
            self.current_value_entry.insert(0, "READ")
            self.current_value_entry.configure(state='readonly')
            self.current_value_entry.configure(width=100)
            self.current_value_entry.grid(row=row, column=5)

            self.new_entry = ctk.CTkEntry(frame)
            self.new_entry.grid(row=row, column=6)

            self.set_button = ctk.CTkButton(frame, text="SET",
                                            command=lambda widget_row=row, widget_tab=tab: self.set_value(widget_row,
                                                                                                          widget_tab))
            self.set_button.grid(row=row, column=7)

        self.read_config_button = ctk.CTkButton(self, text="READ CONFIGURATION", command=self.read_config)
        self.read_config_button.pack(side="right")

        self.restore_defaults_button = ctk.CTkButton(self, text="Restore factory defaults")
        self.restore_defaults_button.configure(state=ctk.DISABLED)
        self.restore_defaults_button.pack(side="left")

        self.save_config_button = ctk.CTkButton(self, text="Save configuration to memory",
                                                command=self.save_config_button)
        self.save_config_button.pack(side="left")

    def read_config(self):
        self.read_config_button.configure(state=ctk.DISABLED, text='READING...')
        self.read_config_button.update_idletasks()
        for tab in self.tabs:
            frame = self.tabview.tab(tab)
            rows = frame.grid_size()[1]

            for row in range(1, rows):
                id_label = frame.grid_slaves(row=row, column=0)[0]
                can_id = int(id_label.cget("text"), 16)

                sub_label = frame.grid_slaves(row=row, column=1)[0]
                sub = int(sub_label.cget("text"))

                current_value = self.current_controller.GetValue(can_id, sub)

                current_value_entry = frame.grid_slaves(row=row, column=5)[0]
                current_value_entry.configure(state='normal')
                current_value_entry.delete(0, 'end')
                current_value_entry.insert(0, current_value)
                current_value_entry.configure(state='readonly')

        self.read_config_button.configure(state='normal', text='READ CONFIGURATION')

    def update_controller(self, selected_id):
        # Find the selected controller object based on the selected ID
        self.current_controller = next(
            (controller for controller in self.controllers if str(controller.GetCanID()) == selected_id), None)

    def set_value(self, row, tab):
        frame = self.tabview.tab(tab)

        id_label = frame.grid_slaves(row=row, column=0)[0]
        can_id = int(id_label.cget("text"), 16)

        sub_label = frame.grid_slaves(row=row, column=1)[0]
        sub = int(sub_label.cget("text"))

        value_entry = frame.grid_slaves(row=row, column=6)[0]
        try:
            value = float(value_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid input. Please enter a valid number.")
            return

        self.current_controller.SetValue(can_id, sub, value)
        value_entry.delete(0, 'end')

        current_value = self.current_controller.GetValue(can_id, sub)

        current_value_entry = frame.grid_slaves(row=row, column=5)[0]
        current_value_entry.configure(state='normal')
        current_value_entry.delete(0, 'end')
        current_value_entry.insert(0, current_value)
        current_value_entry.configure(state='readonly')

    def save_config_button(self):
        result = messagebox.askokcancel("Save Parameters",
                                        "Are you sure you want to save the parameters to memory? This change cannot be undone.")
        if result:
            self.current_controller.SaveToMemory()

    def _reset_scrollregion(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _resize_inner_frame(self, event):
        self.canvas.itemconfig("inner", width=event.width)


# class FELDLiveView(ctk.CTkToplevel):
#     def __init__(self, parent):
#         super().__init__(parent)
#         self.title("FELDLiveView")
#         self.geometry("1200x1000")
#
#         self.current_controller = None
#         # Create ALL NODES segment
#         all_nodes_frame = ctk.CTkFrame(self)
#         all_nodes_frame.pack(fill="x")
#         all_nodes_label = ctk.CTkLabel(all_nodes_frame, text="ALL NODES")
#         all_nodes_label.pack()
#
#         # Create four identical segments
#         for i in range(4):
#             segment_frame = ctk.CTkFrame(self)
#             segment_frame.pack(fill="x")
#
#             # Create drop-down menu
#             controller_ids = [str(controller.GetCanID()) for controller in controllers]
#             self.controller_var = ctk.StringVar(value=controller_ids[0])
#             self.controller_dropdown = ctk.CTkOptionMenu(segment_frame, variable=self.controller_var,
#                                                          values=controller_ids,
#                                                          command=self.update_controller)
#             self.controller_dropdown.pack(side="left")
#
#     def update_controller(self,selected_id):
#         # Find the selected controller object based on the selected ID
#         self.current_controller = next((controller for controller in self.controllers if str(controller.GetCanID()) == selected_id), None)

class FELDLiveView(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("FELDLiveView")
        self.geometry("1200x1000")

        self.current_controller = None
        self.controllers = controllers
        # Create ALL NODES segment
        all_nodes_frame = ctk.CTkFrame(self)
        all_nodes_frame.pack(fill="x")
        all_nodes_label = ctk.CTkLabel(all_nodes_frame, text="ALL NODES")
        all_nodes_label.pack(side="left")

        # Add dummy text to ALL NODES segment
        all_nodes_dummy_text = ctk.CTkLabel(all_nodes_frame, text="Dummy Text")
        all_nodes_dummy_text.pack(side="left")

        # Create four identical segments
        for i in range(4):
            segment_frame = ctk.CTkFrame(self)
            segment_frame.pack(fill="x")

            # Create drop-down menu with no default value
            controller_ids = [str(controller.GetCanID()) for controller in controllers]
            self.controller_var = ctk.StringVar()
            self.controller_dropdown = ctk.CTkOptionMenu(segment_frame, variable=self.controller_var,
                                                         values=controller_ids,
                                                         command=self.update_controller)
            self.controller_dropdown.pack(side="left")

            id_label = ctk.CTkLabel(segment_frame, text="ID:")
            id_label.pack(side="left")

            id_textbox = ctk.CTkEntry(segment_frame)
            id_textbox.configure(state=ctk.DISABLED)
            id_textbox.pack(side="left")

            state_label = ctk.CTkLabel(segment_frame, text="STATE:")
            state_label.pack(side="left")

            state_textbox = ctk.CTkEntry(segment_frame)
            state_textbox.configure(state=ctk.DISABLED)
            state_textbox.pack(side="left")

            column1 = ctk.CTkFrame(segment_frame)
            column1.pack(side="left")

            column2 = ctk.CTkFrame(segment_frame)
            column2.pack(side="left")

            motor1_label = ctk.CTkLabel(column1, text="Motor 1")
            motor1_label.pack()

            current_limit_label = ctk.CTkLabel(column1, text="Current Limit")
            current_limit_label.pack()

            current_limit_slider = ctk.CTkSlider(column1)
            current_limit_slider.pack()

            motor_temperature_label = ctk.CTkLabel(column1, text="MOTOR TEMPERATURE")
            motor_temperature_label.pack()

            motor_temperature_textbox = ctk.CTkEntry(column1)
            motor_temperature_textbox.configure(state=ctk.DISABLED)
            motor_temperature_textbox.pack()

            textbox1 = ctk.CTkEntry(column1)
            textbox1.configure(state=ctk.DISABLED)
            textbox1.pack()

            textbox2 = ctk.CTkEntry(column1)
            textbox2.configure(state=ctk.DISABLED)
            textbox2.pack()

            force_control_label = ctk.CTkLabel(column1, text="FORCE & CONTROL")
            force_control_label.pack()

            brake_status_label = ctk.CTkLabel(column1, text="Brake Status")
            brake_status_label.pack()

            brake_status_textbox = ctk.CTkEntry(column1)
            brake_status_textbox.pack()

            release_brake_button = ctk.CTkButton(column1, text="RELEASE BRAKE")
            release_brake_button.pack()

            close_brake_button = ctk.CTkButton(column1, text="CLOSE BRAKE")
            close_brake_button.pack()

            target_speed_label = ctk.CTkLabel(column1, text="TARGET SPEED")
            target_speed_label.pack()

            target_speed_textbox = ctk.CTkEntry(column1)
            target_speed_textbox.pack()

            set_speed_button = ctk.CTkButton(column1, text="SET")
            set_speed_button.pack()

            target_torque_label = ctk.CTkLabel(column1, text="TARGET TORQUE")
            target_torque_label.pack()

            target_torque_textbox = ctk.CTkEntry(column1)
            target_torque_textbox.pack()

            set_torque_button = ctk.CTkButton(column1, text="SET")
            set_torque_button.pack()

            enable_button = ctk.CTkButton(column1, text="ENABLE")
            enable_button.pack()

            disable_button = ctk.CTkButton(column1, text="DISABLE")
            disable_button.pack()

            application_label = ctk.CTkLabel(segment_frame, text="APPLICATION")
            application_label.pack()

            temperatures_label = ctk.CTkLabel(segment_frame, text="TEMPERATURES")
            temperatures_label.pack(side="left")

            mot1_label = ctk.CTkLabel(segment_frame, text="MOT1")
            mot1_label.pack(side="left")

            mot1_textbox = ctk.CTkEntry(segment_frame)
            mot1_textbox.pack(side="left")

            mot2_label = ctk.CTkLabel(segment_frame, text="MOT2")
            mot2_label.pack(side="left")

            mot2_textbox = ctk.CTkEntry(segment_frame)
            mot2_textbox.pack(side="left")

            app_label = ctk.CTkLabel(segment_frame, text="APP")
            app_label.pack(side="left")

            app_textbox = ctk.CTkEntry(segment_frame)
            app_textbox.pack(side="left")

            status_application_label = ctk.CTkLabel(segment_frame, text="STATUS APPLICATION")
            status_application_label.pack()

            status_application_textbox = ctk.CTkEntry(segment_frame)
            status_application_textbox.pack()

            digital_i_label = ctk.CTkLabel(segment_frame, text="DIGITAL I")
            digital_i_label.pack()

            # Add dummy text and button
            dummy_text = ctk.CTkLabel(segment_frame, text="Dummy Text")
            dummy_text.pack(side="left")
            dummy_button = ctk.CTkButton(segment_frame, text="Dummy Button")
            dummy_button.pack(side="left")

    def update_controller(self, selected_id):
        # Find the selected controller object based on the selected ID
        self.current_controller = next(
            (controller for controller in self.controllers if str(controller.GetCanID()) == selected_id), None)


# MAIN APP ##### MAIN APP ##### MAIN APP ##### MAIN APP ##### MAIN APP
# class FELDTool_main_app(ctk.CTk):
#     def __init__(self):
#         super().__init__()
#
#         self.geometry('800x600')
#         self.title('FELDTool')
#
#         # place a button on the root window
#         ctk.CTkButton(self, text='Faults View', command=self.open_FaultsView).pack(expand=True)
#         ctk.CTkButton(self, text="FELDConnect", command=self.open_feld_connection).pack(expand=True)
#         ctk.CTkButton(self, text="Activate", command=self.activate_motors).pack(expand=True)
#         ctk.CTkButton(self, text="Deactivate", command=self.deactivate_motors).pack(expand=True)
#
#         ctk.CTkButton(self, text="Parameter", command=self.open_parameters).pack(expand=True)
#
#         ctk.CTkButton(self, text="Live", command=self.open_LiveView).pack(expand=True)
#
#     def open_FaultsView(self):
#         fault_window = FELDFaults(self)
#         fault_window.grab_set()
#
#     def open_parameters(self):
#         parameter_window = FELDParameter(self)
#         parameter_window.grab_set()
#
#     def open_feld_connection(self):
#         connection_window = FELDConnection(self)
#         connection_window.grab_set()
#
#     def open_LiveView(self):
#         LiveView_window = FELDLiveView(self)
#         LiveView_window.grab_set()
#
#     def activate_motors(self):
#         activate_motors_tmp()
#
#     def deactivate_motors(self):
#         deactivate_motors_tmp()


class FELDTool_main_app(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.geometry('800x1200')
        self.title('FELDTool')

        # First line
        first_line = ctk.CTkFrame(self)
        first_line.pack(fill="x")

        connect_button = ctk.CTkButton(first_line, text="CONNECT", command=self.open_feld_connection)
        connect_button.pack(side=LEFT)

        info_frame = ctk.CTkFrame(self)
        info_frame.pack(side=LEFT, fill="both", expand=True)

        self.info_text = ctk.CTkLabel(info_frame, text="")
        self.info_text.pack(fill="both", expand=True)

        # Second line
        second_line = ctk.CTkFrame(self)
        second_line.pack(fill="x", pady=10)

        self.faults_button = ctk.CTkButton(second_line, text="FAULTS", command=self.open_FaultsView)
        self.faults_button.configure(state=ctk.DISABLED)
        self.faults_button.pack(side=LEFT, padx=5)

        self.parameter_button = ctk.CTkButton(second_line, text="PARAMETER", command=self.open_parameters)
        self.parameter_button.configure(state=ctk.DISABLED)
        self.parameter_button.pack(side=LEFT, padx=5)

        self.live_view_button = ctk.CTkButton(second_line, text="LIVE VIEW", command=self.open_LiveView)
        self.live_view_button.configure(state=ctk.DISABLED)
        self.live_view_button.pack(side=LEFT, padx=5)

        # Third line
        third_line = ctk.CTkFrame(self)
        third_line.pack(fill="x", pady=10)

        self.activate_all_button = ctk.CTkButton(third_line, text="ACTIVATE ALL", command=self.activate_all)
        self.activate_all_button.configure(state=ctk.DISABLED)
        self.activate_all_button.pack(side=LEFT, padx=5)

        self.release_brakes_button = ctk.CTkButton(third_line, text="RELEASE BRAKES", command=self.release_all)
        self.release_brakes_button.configure(state=ctk.DISABLED)
        self.release_brakes_button.pack(side=LEFT, padx=5)

        self.apply_brakes_button = ctk.CTkButton(third_line, text="APPLY BRAKES", command=self.apply_all)
        self.apply_brakes_button.configure(state=ctk.DISABLED)
        self.apply_brakes_button.pack(side=LEFT, padx=5)

        self.deactivate_all_button = ctk.CTkButton(third_line, text="DEACTIVATE ALL", command=self.deactivate_all)
        self.deactivate_all_button.configure(state=ctk.DISABLED)
        self.deactivate_all_button.pack(side=LEFT, padx=5)

        # Fourth line
        fourth_line = ctk.CTkFrame(self)
        fourth_line.pack(fill="x")

        rpm_label = ctk.CTkLabel(fourth_line, text="RPM-SET")
        rpm_label.grid(row=0, column=0)

        self.rpm_entry = ctk.CTkEntry(fourth_line)
        self.rpm_entry.grid(row=0, column=1)

        self.set_rpm_button = ctk.CTkButton(fourth_line, text="SET", command=self.set_rpm)
        self.set_rpm_button.configure(state=ctk.DISABLED)
        self.set_rpm_button.grid(row=0, column=2)

        torque_label = ctk.CTkLabel(fourth_line, text="TORQUE-SET")
        torque_label.grid(row=1, column=0)

        self.torque_entry = ctk.CTkEntry(fourth_line)
        self.torque_entry.grid(row=1, column=1)

        self.set_torque_button = ctk.CTkButton(fourth_line, text="SET", command=self.set_torque)
        self.set_torque_button.configure(state=ctk.DISABLED)
        self.set_torque_button.grid(row=1, column=2)

        # Sixth line
        sixth_line = ctk.CTkFrame(self)
        sixth_line.pack(fill="x")

        current_limit_label = ctk.CTkLabel(sixth_line, text="CURRENT LIMIT")
        current_limit_label.grid(row=0, column=0)

        self.current_limit_entry = ctk.CTkEntry(sixth_line)
        self.current_limit_entry.grid(row=0, column=1)

        self.set_current_limit_button = ctk.CTkButton(sixth_line, text="SET", command=self.set_current_limit)
        self.set_current_limit_button.configure(state=ctk.DISABLED)
        self.set_current_limit_button.grid(row=0, column=2)

        # Seventh line
        seventh_line = ctk.CTkFrame(self)
        seventh_line.pack(fill="x")

        rpm_accel_ramp_label = ctk.CTkLabel(seventh_line, text="RPM accel ramp")
        rpm_accel_ramp_label.grid(row=0, column=0)

        self.rpm_accel_ramp_entry = ctk.CTkEntry(seventh_line)
        self.rpm_accel_ramp_entry.grid(row=0, column=1)

        self.set_rpm_accel_ramp_button = ctk.CTkButton(seventh_line, text="SET", command=self.set_rpm_accel_ramp)
        self.set_rpm_accel_ramp_button.configure(state=ctk.DISABLED)
        self.set_rpm_accel_ramp_button.grid(row=0, column=2)

        # Eighth line
        eighth_line = ctk.CTkFrame(self)
        eighth_line.pack(fill="x")

        rpm_decel_ramp_label = ctk.CTkLabel(eighth_line, text="RPM decel ramp")
        rpm_decel_ramp_label.grid(row=0, column=0)

        self.rpm_decel_ramp_entry = ctk.CTkEntry(eighth_line)
        self.rpm_decel_ramp_entry.grid(row=0, column=1)

        self.set_rpm_decel_ramp_button = ctk.CTkButton(eighth_line, text="SET", command=self.set_rpm_decel_ramp)
        self.set_rpm_decel_ramp_button.configure(state=ctk.DISABLED)
        self.set_rpm_decel_ramp_button.grid(row=0, column=2)

        # Ninth line
        ninth_line = ctk.CTkFrame(self)
        ninth_line.pack(fill="x")

        p_val_label = ctk.CTkLabel(ninth_line, text="P-Val")
        p_val_label.grid(row=0, column=0)

        self.p_val_entry = ctk.CTkEntry(ninth_line)
        self.p_val_entry.grid(row=0, column=1)

        self.set_p_val_button = ctk.CTkButton(ninth_line, text="SET", command=self.set_p_val)
        self.set_p_val_button.configure(state=ctk.DISABLED)
        self.set_p_val_button.grid(row=0, column=2)

        # tenth line
        tenth_line = ctk.CTkFrame(self)
        tenth_line.pack(fill="x")

        i_val_label = ctk.CTkLabel(tenth_line, text="I-Val")
        i_val_label.grid(row=0, column=0)

        self.i_val_entry = ctk.CTkEntry(tenth_line)
        self.i_val_entry.grid(row=0, column=1)

        self.set_i_val_button = ctk.CTkButton(tenth_line, text="SET", command=self.set_i_val)
        self.set_i_val_button.configure(state=ctk.DISABLED)
        self.set_i_val_button.grid(row=0, column=2)

        # eleventh line
        eleventh_line = ctk.CTkFrame(self)
        eleventh_line.pack(fill="x")

        d_val_label = ctk.CTkLabel(eleventh_line, text="D-Val")
        d_val_label.grid(row=0, column=0)

        self.d_val_entry = ctk.CTkEntry(eleventh_line)
        self.d_val_entry.grid(row=0, column=1)

        self.set_d_val_button = ctk.CTkButton(eleventh_line, text="SET", command=self.set_d_val)
        self.set_d_val_button.configure(state=ctk.DISABLED)
        self.set_d_val_button.grid(row=0, column=2)

        # Twelfth line
        twelfth_line = ctk.CTkFrame(self)
        twelfth_line.pack(fill="x")

        self.set_current_control_button = ctk.CTkButton(twelfth_line, text="SET CURRENT CONTROL",
                                                        command=self.set_current_control)
        self.set_current_control_button.configure(state=ctk.DISABLED)
        self.set_current_control_button.grid(row=0, column=0)

        self.set_rpm_control_button = ctk.CTkButton(twelfth_line, text="SET RPM CONTROL", command=self.set_rpm_control)
        self.set_rpm_control_button.configure(state=ctk.DISABLED)
        self.set_rpm_control_button.grid(row=0, column=1)

        self.update_info_text()
        # self.geometry('800x800')

    def set_rpm(self):
        rpm = self.rpm_entry.get()
        self.rpm_entry.delete(0, "end")
        for controller in controllers:
            controller.SetValue(0x6042, 1, rpm)
            controller.SetValue(0x6042, 2, rpm)
        print(f"RPM set to: {rpm}")

    def set_torque(self):
        torque = float(self.torque_entry.get())
        self.torque_entry.delete(0, "end")
        for controller in controllers:
            controller.SetValue(0x6071, 1, torque)
            controller.SetValue(0x6071, 2, torque)
        print(f"Torque set to: {torque}")

    def set_current_limit(self):
        current_limit = float(self.current_limit_entry.get())
        self.current_limit_entry.delete(0, "end")
        for controller in controllers:
            controller.SetValue(0x3009, 1, current_limit)
            controller.SetValue(0x3009, 2, current_limit)
        print(f"Current limit set to: {current_limit}")

    def set_rpm_accel_ramp(self):
        self.deactivate_all()
        rpm_ramp = float(self.rpm_accel_ramp_entry.get())
        self.rpm_accel_ramp_entry.delete(0, "end")
        for controller in controllers:
            controller.SetValue(0x3011, 1, rpm_ramp)
            controller.SetValue(0x3011, 2, rpm_ramp)
        print(f"RPM acel ramp set to: {rpm_ramp}")

    def set_rpm_decel_ramp(self):
        self.deactivate_all()
        rpm_ramp = float(self.rpm_decel_ramp_entry.get())
        self.rpm_decel_ramp_entry.delete(0, "end")
        for controller in controllers:
            controller.SetValue(0x3012, 1, rpm_ramp)
            controller.SetValue(0x3012, 2, rpm_ramp)
        print(f"RPM decel ramp set to: {rpm_ramp}")

    def set_p_val(self):
        self.deactivate_all()
        p_val = float(self.p_val_entry.get())
        self.p_val_entry.delete(0, "end")
        for controller in controllers:
            controller.SetValue(0x60F9, 1, p_val)
            controller.SetValue(0x60F9, 5, p_val)
        print(f"P-Val set to: {p_val}")

    def set_i_val(self):
        self.deactivate_all()
        i_val = float(self.i_val_entry.get())
        self.i_val_entry.delete(0, "end")
        for controller in controllers:
            controller.SetValue(0x60F9, 2, i_val)
            controller.SetValue(0x60F9, 6, i_val)
        print(f"I-Val set to: {i_val}")

    def set_d_val(self):
        self.deactivate_all()
        d_val = float(self.d_val_entry.get())
        self.d_val_entry.delete(0, "end")
        for controller in controllers:
            controller.SetValue(0x60F9, 3, d_val)
            controller.SetValue(0x60F9, 7, d_val)
        print(f"D-Val set to: {d_val}")

    def set_current_control(self):
        self.deactivate_all()
        for controller in controllers:
            controller.SetValue(0x6060, 1, 0x03)
            controller.SetValue(0x6060, 2, 0x03)
        self.release_all()
        print(f"Current control mode")

    def set_rpm_control(self):
        self.deactivate_all()
        for controller in controllers:
            controller.SetValue(0x6060, 1, 0x06)
            controller.SetValue(0x6060, 2, 0x06)
        print(f"RPM control mode")

    def open_FaultsView(self):
        fault_window = FELDFaults(self)
        fault_window.grab_set()

    def open_parameters(self):
        parameter_window = FELDParameter(self)
        parameter_window.grab_set()

    def open_feld_connection(self):
        connection_window = FELDConnection(self)
        connection_window.grab_set()
        connection_window.bind("<Destroy>", lambda event: self.on_connection_window_closed())

    def on_connection_window_closed(self):
        if len(controllers) >= 1:
            self.faults_button.configure(state=ctk.NORMAL)
            self.parameter_button.configure(state=ctk.NORMAL)
            self.live_view_button.configure(state=ctk.NORMAL)
            self.activate_all_button.configure(state=ctk.NORMAL)
            self.release_brakes_button.configure(state=ctk.NORMAL)
            self.apply_brakes_button.configure(state=ctk.NORMAL)
            self.deactivate_all_button.configure(state=ctk.NORMAL)
            self.set_rpm_button.configure(state=ctk.NORMAL)
            self.set_torque_button.configure(state=ctk.NORMAL)
            self.set_current_limit_button.configure(state=ctk.NORMAL)
            self.set_rpm_control_button.configure(state=ctk.NORMAL)
            self.set_rpm_accel_ramp_button.configure(state=ctk.NORMAL)
            self.set_rpm_decel_ramp_button.configure(state=ctk.NORMAL)
            self.set_p_val_button.configure(state=ctk.NORMAL)
            self.set_i_val_button.configure(state=ctk.NORMAL)
            self.set_d_val_button.configure(state=ctk.NORMAL)
            self.set_current_control_button.configure(state=ctk.NORMAL)
            self.set_rpm_control_button.configure(state=ctk.NORMAL)
            self.geometry('800x1200')
        pass

    def open_LiveView(self):
        LiveView_window = FELDLiveView(self)
        LiveView_window.grab_set()

    def activate_all(self):
        for controller in controllers:
            controller.EnableMotor("Motor1")
            controller.EnableMotor("Motor2")
        print("activate_all")

    def deactivate_all(self):
        for controller in controllers:
            controller.DisableMotor("Motor1")
            controller.DisableMotor("Motor2")
        print("deactivate_all")

    def release_all(self):
        for controller in controllers:
            controller.ForceBrakeRelease("Motor1")
            controller.ForceBrakeRelease("Motor2")
        print("release_all")

    def apply_all(self):
        for controller in controllers:
            controller.ForceBrakeApply("Motor1")
            controller.ForceBrakeApply("Motor2")
        print("apply_all")

    def update_info_text(self):
        global amp_hours
        node_states_text = []
        for controller in controllers:
            node_states_text.append("Node: ")
            node_states_text.append(controller.GetCanID())
            node_states_text.append(controller.GetNodeState())
            node_states_text.append("\n")

            # for controller in controllers:
            #     node_states_text.append("Controller: ")
            #     node_states_text.append(controller.GetCanID)
            #     node_states_text.append(" M1[")
            #     node_states_text.append(controller.GetValue(0x6041, 1))
            #     node_states_text.append("];")
            #     node_states_text.append(" M2[")
            #     node_states_text.append(controller.GetValue(0x6041, 2))
            #     node_states_text.append("];")
            #     node_states_text.append("\n")

        amps = 0
        for controller in controllers:
            amps += controller.GetValue(0x6078, 1)
            amps += controller.GetValue(0x6078, 2)
        amp_hours += amps * 0.1 / 3600.0

        node_states_text.append("Mot Amps: ")
        node_states_text.append(round(amps / 4.0, 2))
        node_states_text.append("\n")

        node_states_text.append("Amp Hours: ")
        node_states_text.append(round(amp_hours, 5))
        node_states_text.append("\n")

        self.info_text.configure(text=node_states_text, anchor="nw")
        self.after(100, self.update_info_text)


app = FELDTool_main_app()

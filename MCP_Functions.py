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
import time
import os
import canopen
import MCPRegisters as mcp_reg

# CAN-BusConfiguration
network = canopen.Network()
pathEDS1 = 'MCP-48-20-02.eds'  # path to .eds file


def ConnectToCan(COM, Baud):
    try:
        # Bring down the CAN interface
        os.system('sudo ifconfig can0 down')
        time.sleep(1)  # Allow some time for the interface to go down

        # Set up the CAN interface
        os.system('sudo ip link set can0 type can bitrate 500000') #100000
        os.system('sudo ifconfig can0 up')

        network.connect(bustype='socketcan', channel=COM, bitrate=Baud)  # connect to network
        network.send_message(0x0, [0x1, 0])  # operational
        print("Operational Sent")
        return (0)
    except Exception as e:
        print(f"Error connecting to CAN bus: {e}")
        return (-1)



def NetworkDisconnect():
    network.disconnect()
    print("Disconnected")


class MCP_Node:
    node = None

    def __init__(self, id):
        try:
            self.node = network.add_node(id, pathEDS1)  # add node to network
        except Exception as e:
            raise Exception(f"Failed to add node: {e}")

    # node1_Controlword_1 = node1.sdo[0x6040][1]
    # node1_Controlword_1.raw = 15
    # print("Enable Mot 1")

    def GetNodeState(self):
        note_state = (self.node.sdo[0x2001]).raw
        if (note_state in mcp_reg.NodeStates):
            return [hex(note_state), mcp_reg.NodeStates[note_state]]
        else:
            return hex(note_state)

    def GetCanID(self):
        return (self.node.sdo[0x2000][1]).raw

    def GetValue(self, ID, SUB):
        if SUB == -1:
            print("base sub")
            return (self.node.sdo[ID]).raw
        else:
            return (self.node.sdo[ID][SUB]).raw

    def SetValue(self, ID, SUB, VAL):
        if SUB == -1:
            (self.node.sdo[ID]).raw = VAL
        else:
            (self.node.sdo[ID][SUB]).raw = VAL

    def SaveToMemory(self):
        self.DisableMotor("Motor1")
        self.DisableMotor("Motor2")
        print("disable")
        time.sleep(2.5)
        (self.node.sdo[0x1010][1]).raw = 0x65766173
        print("saved to memory!")


    def EnableMotor(self, Motor):
        if Motor == "Motor1":
            (self.node.sdo[0x6040][1]).raw = 0xF
            (self.node.sdo[0x3025][1]).raw = 0x00
            (self.node.sdo[0x3024][1]).raw = 0x00
        elif Motor == "Motor2":
            (self.node.sdo[0x6040][2]).raw = 0xF
            (self.node.sdo[0x3025][2]).raw = 0x00
            (self.node.sdo[0x3024][2]).raw = 0x00
        else:
            raise ValueError("Invalid motor specified")

    def DisableMotor(self, Motor):
        if Motor == "Motor1":
            (self.node.sdo[0x6040][1]).raw = 0x0
            (self.node.sdo[0x3025][1]).raw = 0x00
            (self.node.sdo[0x3024][1]).raw = 0x00
        elif Motor == "Motor2":
            (self.node.sdo[0x6040][2]).raw = 0x0
            (self.node.sdo[0x3025][1]).raw = 0x00
            (self.node.sdo[0x3024][1]).raw = 0x00
        else:
            raise ValueError("Invalid motor specified")

    def ForceBrakeRelease(self, Motor):
        if Motor == "Motor1":
            (self.node.sdo[0x3025][1]).raw = 0x00
            (self.node.sdo[0x3024][1]).raw = 0x01
            print("release_M1")
        elif Motor == "Motor2":
            (self.node.sdo[0x3025][2]).raw = 0x00
            (self.node.sdo[0x3024][2]).raw = 0x01
            print("release_M2")
        else:
            raise ValueError("Invalid motor specified")

    def ForceBrakeApply(self, Motor):
        if Motor == "Motor1":
            (self.node.sdo[0x3024][1]).raw = 0x00
            (self.node.sdo[0x3025][1]).raw = 0x01
        elif Motor == "Motor2":
            (self.node.sdo[0x3024][2]).raw = 0x00
            (self.node.sdo[0x3025][2]).raw = 0x01
        else:
            raise ValueError("Invalid motor specified")

    def FaultResetMotor(self, Motor):
        if Motor == "Motor1":
            (self.node.sdo[0x6040][1]).raw = 0x80
        elif Motor == "Motor2":
            (self.node.sdo[0x6040][2]).raw = 0x80
        else:
            raise ValueError("Invalid motor specified")

    def ReadFaults(self, fault):
        if fault == "ErrorRegister":
            return self.Read_ErrorRegister()
        elif fault == "ErrorRegisterNumber":
            return self.Read_ErrorRegisterNumber()
        elif fault == "PreDefinedErrorField":
            return self.Read_PreDefinedErrorField()
        elif fault in ["Motor1", "Motor2", "Application"]:
            return self.Read_FaultRegister(fault)

    # def ReadFaults(self):
    #     print(self.Read_ErrorRegister())
    #     print(self.Read_PreDefinedErrorField())
    #     print(self.Read_FaultRegister("Motor1"))
    #     print(self.Read_FaultRegister("Motor2"))
    #     print(self.Read_FaultRegister("Application"))

    #    for obj in node1.object_dictionary.values():
    #        print('0x%X: %s' % (obj.index, obj.name))
    #        if isinstance(obj, canopen.objectdictionary.Record):
    #            for subobj in obj.values():
    #                print('  %d: %s' % (subobj.subindex, subobj.name))

    #   print("NumErrors")
    #  print(node1_RampAcceleration_1.raw)
    #   print((node1.sdo[0x1003][0]).raw)
    #   print("Error_1")
    #    print(hex((node1.sdo[0x1003][1]).raw))

    def Read_ErrorRegister(self):
        error_num = (self.node.sdo[0x1001]).raw
        if (error_num != 0):
            return [hex(error_num), mcp_reg.ErrorRegisterStates[error_num]]

    def Read_ErrorRegisterNumber(self):
        error_num = (self.node.sdo[0x1001]).raw
        if (error_num != 0):
            return error_num

    def Read_PreDefinedErrorField(self):
        pending_error = (self.node.sdo[0x1003][0]).raw
        error_list = []

        # print(pending_error)

        for i in range(1, pending_error + 1):
            error_num = (self.node.sdo[0x1003][i]).raw
            app_code = (error_num >> (4 * 4)) & 0xF
            error_code = error_num & 0x0FFFF
            appStates = []

            for code, message in mcp_reg.PreDefinedErrorFieldAppStates.items():
                if app_code & code:
                    appStates.append([message])

            error_list.append(
                [hex(error_num), appStates,
                 mcp_reg.PreDefinedErrorFieldStates[error_code]])
        return error_list

    def Read_FaultRegister(self, register):
        if register == "Motor1":
            fault = (self.node.sdo[0x3002][1]).raw
            fault_register = mcp_reg.FaultRegisterMotor
        elif register == "Motor2":
            fault = (self.node.sdo[0x3002][2]).raw
            fault_register = mcp_reg.FaultRegisterMotor
        elif register == "Application":
            fault = (self.node.sdo[0x3002][3]).raw
            fault_register = mcp_reg.FaultRegisterApplication
        else:
            raise ValueError("Invalid register specified")

        if fault == 0x0:
            return

        error_list = [hex(fault)]

        for code, message in mcp_reg.FaultRegisterAllSubs.items():
            if fault & code:
                error_list.append([message])

        for code, message in fault_register.items():
            if fault & code:
                error_list.append([message])

        return error_list

    def Clear_Errors(self):
        (self.node.sdo[0x1003][0]).raw = 0

    def MCP_Stuff_tmp(self):
        node1_TargetVelocity_1 = self.node.sdo[0x6042][1]
        node1_Controlword_1 = self.node.sdo[0x6040][1]
        node1_CurrentLimit_1 = self.node.sdo[0x3009][1]

        #    for obj in node1.object_dictionary.values():
        #        print('0x%X: %s' % (obj.index, obj.name))
        #        if isinstance(obj, canopen.objectdictionary.Record):
        #            for subobj in obj.values():
        #                print('  %d: %s' % (subobj.subindex, subobj.name))

        # time.sleep(3.05)

        # time.sleep(3.05)

        node1_TargetVelocity_1.raw = 0  # rpm
        print("Target vel set")

        node1_Controlword_1.raw = 15
        print("Controlword")

        print("VoltageConstant_1")
        print((self.node.sdo[0x3005][1]).raw)
        print("VoltageConstant_2")
        print((self.node.sdo[0x3005][2]).raw)
        print("TorqueConstant_1")
        print((self.node.sdo[0x3006][1]).raw)
        print("TorqueConstant_2")
        print((self.node.sdo[0x3006][2]).raw)

        print("Old CurrentLimit_1")
        print((self.node.sdo[0x3009][1]).raw)
        print("CurrentLimit_2")
        print((self.node.sdo[0x3009][2]).raw)

        print("CurrentLimit_i2t_1")
        print((self.node.sdo[0x300A][1]).raw)
        print("CurrentLimit_i2t_2")
        print((self.node.sdo[0x300A][2]).raw)

        print("NumErrors")
        print((self.node.sdo[0x1003][0]).raw)
        print("Error_1")
        print(hex((self.node.sdo[0x1003][1]).raw))

        print("Set CurrentLimit_1")
        node1_CurrentLimit_1.raw = 5  # A
        print("New CurrentLimit_1")
        print((self.node.sdo[0x3009][1]).raw)

        node1_Controlword_1.raw = 0
        print("Controlword")

        # network.send_message(0x0, [0x1, 1])  # operational
        # print("Something sent")

        #  node1_RampAcceleration_1 = node1.sdo[0x3011][1]

        #   print("NumErrors")
        #  print(node1_RampAcceleration_1.raw)
        #   print((node1.sdo[0x1003][0]).raw)
        #   print("Error_1")
        #    print(hex((node1.sdo[0x1003][1]).raw))

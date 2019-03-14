import Adafruit_BBIO.GPIO as GPIO

class MITM():
    def __init__(self):
        GPIO.setup("P8_38",GPIO.OUT)
        GPIO.setup("P8_39",GPIO.OUT)
        GPIO.setup("P8_40",GPIO.OUT)
        GPIO.setup("P8_37",GPIO.OUT)
        GPIO.setup("P8_45",GPIO.OUT)
        GPIO.setup("P8_42",GPIO.OUT)
        GPIO.setup("P8_46",GPIO.OUT)
    
    def LED(self,state):
        if state:
            GPIO.output("P8_38",GPIO.HIGH)
        else:
            GPIO.output("P8_38",GPIO.LOW)
    
    def switch_1(self,state):
        if state:
            GPIO.output("P8_39",GPIO.HIGH)
        else:
            GPIO.output("P8_39",GPIO.LOW)
    
    def switch_2(self,state):
        if state:
            GPIO.output("P8_40",GPIO.HIGH)
        else:
            GPIO.output("P8_40",GPIO.LOW)
    
    def switch_3(self,state):
        if state:
            GPIO.output("P8_37",GPIO.HIGH)
        else:
            GPIO.output("P8_37",GPIO.LOW)
    
    def switch_4(self,state):
        if state:
            GPIO.output("P8_42",GPIO.HIGH)
        else:
            GPIO.output("P8_42",GPIO.LOW)
    
    def switch_5(self,state):
        if state:
            GPIO.output("P8_45",GPIO.HIGH)
        else:
            GPIO.output("P8_45",GPIO.LOW)
    
    def switch_6(self,state):
        if state:
            GPIO.output("P8_46",GPIO.HIGH)
        else:
            GPIO.output("P8_46",GPIO.LOW)

    def passthrough_all_with_resistors(self):
        """
        Terminating resistors are introduced.
        """
        self.switch_1(True) #Connect J1939
        self.switch_2(False) #Connect CAN2
        self.switch_3(False) #DCAN1 reads J1939
        self.switch_4(False) #Connect J1708
        self.switch_5(True) #DCAN0 reads CAN2
        self.switch_6(False) #Terminating Resitors connected

    def passthrough_all_monitor_j1939(self):
        """
        No Terminating resistors are introduced.
        """
        self.switch_1(False) #Disconnect J1939
        self.switch_2(False) #Connect CAN2
        self.switch_3(False) #DCAN1 reads J1939
        self.switch_4(False) #Connect J1708
        self.switch_5(False) #DCAN0 reads J1939
        self.switch_6(True) #DCAN0 connects to DCAN1
    
    def passthrough_all_monitor_can2(self):
        """
        No Terminating resistors are introduced.
        """
        self.switch_1(True) #connect J1939
        self.switch_2(True) #disconnect CAN2
        self.switch_3(True) #DCAN1 reads CAN2
        self.switch_4(False) #Connect J1708
        self.switch_5(True) #DCAN0 reads CAN2
        self.switch_6(True) #DCAN0 connects to DCAN1

    def mitm_can2(self):
        """
        Terminating resistors are introduced.
        """
        self.switch_1(True) #connect J1939
        self.switch_2(True) #disconnect CAN2
        self.switch_3(True) #DCAN1 reads CAN2A
        self.switch_4(False) #Connect J1708
        self.switch_5(True) #DCAN0 reads CAN2B
        self.switch_6(False) #Adds terminating resistors

    def mitm_J1939(self):
        """
        Terminating resistors are introduced.
        """
        self.switch_1(False) #disconnect J1939
        self.switch_2(False) #connect CAN2
        self.switch_3(False) #DCAN1 reads J1939A
        self.switch_4(False) #Connect J1708
        self.switch_5(False) #DCAN0 reads J1939B
        self.switch_6(False) #Adds terminating resistors
    


if __name__ == '__main__':
    import time
    mitm = MITM()
    mitm.LED(False)
    time.sleep(1)
    mitm.LED(True)

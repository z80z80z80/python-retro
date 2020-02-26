#!/usr/bin/env python3

import socket

class Joycon:

    def __init__(self):
        self.joy_but = [False] * self.get_numbuttons()
        self.joy_ax = [0] * self.get_numaxes()
        self.joy_hat = [[0,0]] * self.get_numhats()
        self.data = False
                
        # Create an UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(0.001) # don't wait for replys
        
        # Bind the socket to the port
        server_address = ('localhost', 1312)
        self.sock.bind(server_address)

    def get_input(self):
        # Gets player input
        
        try:
            self.data, address = self.sock.recvfrom(4096)
            self.data = self.data.decode()
        except socket.timeout:
            pass
    
        if self.data:
            for i in range(self.get_numbuttons()): # all buttons except d-pad
                #if i == 0:
                    #print(self.data == str(i)+"_down")
                if self.data == str(i)+"_down":                
                    self.joy_but[i] = True

                elif self.data == str(i)+"_up":
                    self.joy_but[i] = False
    
            if self.data[0:7] == "Stick;1": # left analog stick
                ax0 = float(self.data.split(";")[2])
                ax1 = -float(self.data.split(";")[3])
                if (ax0>0.2 or ax0<-0.2 or ax1>0.2 or ax1<-0.2):
                    self.joy_ax[0]=ax0
                    self.joy_ax[1]=ax1
           
            if self.data[0:7] == "Stick;2": # right analog stick
                ax2 = float(self.data.split(";")[2])
                ax3 = -float(self.data.split(";")[3])
                if (ax2>0.2 or ax2<-0.2 or ax3>0.2 or ax3<-0.2):
                    self.joy_ax[2]=ax2
                    self.joy_ax[3]=ax3
    
            if self.data == "s0_up":
                    self.joy_ax[0]=0
                    self.joy_ax[1]=0
    
            if self.data == "s1_up":
                    self.joy_ax[2]=0
                    self.joy_ax[3]=0
                  
            hat_ids = [ # button (d0..d3): (tuple index, value) -> see get_hat
                    (1, 1), #d0 - u 
                    (1, -1), #d1 - d
                    (0, -1), #d2 - l
                    (0, 1) #d3 - r
                    ]
            for i in range(4): # d-pad, 4 values, there is only one dpad for the switch
                if self.data == "d"+str(i)+"_down":
                    self.joy_hat[0][hat_ids[i][0]] = hat_ids[i][1]
                elif self.data == "d"+str(i)+"_up":
                    self.joy_hat[0][hat_ids[i][0]] = 0

        #print(self.joy_but, self.joy_ax, self.joy_hat)
        return self.joy_but, self.joy_ax, self.joy_hat
    
    def get_button(self, idx):
        self.joy_but, _, _ = self.get_input() # returns bool list of len 8 for joy_but
    
        return self.joy_but[idx]
    
    def get_axis(self, idx):
        _, self.joy_ax, _ = self.get_input() # returns float list of len 4 for joy_ax
        
        return self.joy_ax[idx]
    
    def get_hat(self, idx):
        '''
        'u': (0, 1)  - 0
        'd': (0, -1) - 1
        'l': (-1, 0) - 2 
        'r': (1, 0)  - 3
        
        'c': (0, 0),
        'u': (0, 1),
        'r': (1, 0),
        'd': (0, -1),
        'l': (-1, 0),
        'ur': (1, 1),
        'dr': (1, -1),
        'ul': (-1, 1),
        'dl': (-1, -1),

        '''
        _, _, joy_hat = self.get_input() # returns bool list of len 4 for joy_hat
    
        return tuple(joy_hat[idx])
    
    def get_numaxes(self):
        return 4
    
    def get_numbuttons(self):
        return 8
    
    def get_numhats(self):
        return 1

####


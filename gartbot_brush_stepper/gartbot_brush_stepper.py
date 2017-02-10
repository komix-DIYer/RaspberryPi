#!/usr/bin/python3

import serial
import binascii

import gertbot as gb

btn = [0, 0, 0, 0, 0, 0]
ser = serial.Serial('/dev/rfcomm0', 9600)
dxax = 0
dyax = 0
dxax_old = 0
dyax_old = 0

BOARD = 3
BRS_A = 0
RAMP  = gb.RAMP_050 # ramp speed=0.5 seconds
FORWD = gb.MOVE_A
BACKW = gb.MOVE_B
STOP  = gb.MOVE_STOP
STEPPER_B = 2
MODE  = 24
FREQ  = 400.0

gb.open_uart(0)

gb.set_mode(BOARD, BRS_A, gb.MODE_BRUSH)
gb.set_brush_ramps(BOARD, BRS_A, RAMP, RAMP, 0)

gb.set_mode(BOARD, STEPPER_B, MODE)
gb.freq_stepper(BOARD, STEPPER_B, FREQ)

while True:
    dlen = binascii.b2a_hex(ser.read()).decode('utf-8')
    if dlen=='08' or  dlen=='05' or  dlen=='04':
        dsep = binascii.b2a_hex(ser.read()).decode('utf-8')
        if dsep=='a1':
            dtyp = binascii.b2a_hex(ser.read()).decode('utf-8')
            if   dtyp=='07':
                for i in range(len(btn)):
                    btn[i] = 0
                for i in range(len(btn)):
                    dbtn = int(binascii.b2a_hex(ser.read()).decode('utf-8'),16)
                    if dbtn==0 or dbtn==1 or dbtn==2 or dbtn==3:
                        btn[dbtn] = 1
                # Stop/Up/Down
                if   btn[0]==0 and btn[1]==0:
                    print('Stop')
                    gb.move_brushed(BOARD,BRS_A,STOP)
                elif btn[0]==0 and btn[1]==1:
                    print('Up')
                    gb.move_brushed(BOARD,BRS_A,FORWD)
                elif btn[0]==1 and btn[1]==0:
                    print('Down')
                    gb.move_brushed(BOARD,BRS_A,BACKW)
                #print('[A B C D : X Y] = [' + str(btn[0]) + ' ' + str(btn[1]) + ' ' + str(btn[2]) + ' ' + str(btn[3]) + ' : ' + str(dxax) + ' ' + str(dyax)+ ']')
            elif dtyp=='08':
                dyax_old = dyax
                dxax_old = dxax
                val  = ser.read()
                dyax = -int(binascii.b2a_hex(ser.read()).decode('utf-8'),16)
                if dyax<=-128:
                    dyax = dyax + 256
                dxax = -int(binascii.b2a_hex(ser.read()).decode('utf-8'),16)
                if dxax<=-128:
                    dxax = dxax + 256
                #print('[A B C D : X Y] = [' + str(btn[0]) + ' ' + str(btn[1]) + ' ' + str(btn[2]) + ' ' + str(btn[3]) + ' : ' + str(dxax) + ' ' + str(dyax)+ ']')
            elif dtyp=='11':
                #print('Idle')
                val  = ser.read()
                val  = ser.read()
    if dxax>8 and dxax_old<=8:
        gb.move_stepper(BOARD,STEPPER_B,-20000)
        print('Forward')
    elif dxax<-8 and dxax_old>=-8:
        gb.move_stepper(BOARD,STEPPER_B,20000)
        print('Backword')
    elif abs(dxax)<=8 and abs(dxax_old)>8 :
        gb.stop_stepper(BOARD,STEPPER_B,1)
        print('Stop')
    dxax_old = dxax
    dyax_old = dyax

gb.emergency_stop()

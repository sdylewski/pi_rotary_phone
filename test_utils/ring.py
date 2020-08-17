# need to copy /etc/asound.conf also
# by Scott Dylewski 7/2020
#
import RPi.GPIO as GPIO
import numpy
import signal
import subprocess
import time
import pyaudio  # for recording audio from microphone input
import wave  # saving wav files
import os

# check/define audio in/out ports:?

# GPIO definitions:
FRpin3_1=14
RMpin4_1=15
SHKpin5_1=18

# 2nd phone system:
FRpin3_2=3
RMpin4_2=2
SHKpin5_2=4

debounceDelay=5  # ms
maxPulseInterval=250 # ms  Max separation between digits being dialed
hookDelay = 250 # ms. 

#SHK_state_1 = 0
shkReading1 = 0
previousshkReading1 = 1
state1="ON_HOOK"

#SHK_state_2 = 0
shkReading_2 = 0
previousshkReading_2 = 1
state2="ON_HOOK"

ItalianMode=0
playRecording1 = 0
playRecording2 = 0

# char array for number dialed?

# files:
tmpdir='/home/pi/Telephone/Audio/tmp/'
# filename='/home/pi/Telephone/Audio/hithere.wav'
#filename='/home/pi/Telephone/Audio/applause.wav'
outfile=tmpdir + 'out.wav'

##### Setup:
# audio:
sampleRate=44100 # 44100,  22050, 11025
bitsize= -16
channels = 2
buf = 2048  # experiment to get decent sound?

# GPIO.cleanup()
GPIO.setwarnings(True)  # can set to False by default later
GPIO.setmode(GPIO.BCM) # use GPIO pin numbering 
# phone #1
GPIO.setup(FRpin3_1, GPIO.OUT)
GPIO.setup(RMpin4_1, GPIO.OUT)
GPIO.setup(SHKpin5_1, GPIO.IN)
# phone #2:
GPIO.setup(FRpin3_2, GPIO.OUT)
GPIO.setup(RMpin4_2, GPIO.OUT)
GPIO.setup(SHKpin5_2, GPIO.IN)


def ringPhone(phoneID):
	print("ringing phone" + str(phoneID))
	# getShkReading(device)
	if phoneID == 1:
		FRpin3=FRpin3_1
		RMpin4=RMpin4_1
		SHKpin5=SHKpin5_1
	elif phoneID == 2:
		FRpin3=FRpin3_2
		RMpin4=RMpin4_2
		SHKpin5=SHKpin5_2
	while ( GPIO.input(SHKpin5) == 0 ): # while on hook (SHK=0)
		GPIO.output(RMpin4, GPIO.HIGH)  # set RM high
		time.sleep(0.01)
		for freq in [20,25,30]:
			# ringDelay = 0.04   # 40ms
			ringDelay=(1/freq)
			rings=round(1/ringDelay)+1
			print("freq="+str(freq) + " ringDelay="+str(ringDelay)+ " rings="+str(rings) )
			for i in range(1,rings):
				GPIO.output(FRpin3, GPIO.LOW)  # alternate the FR to ring
				time.sleep(ringDelay)
				GPIO.output(FRpin3, GPIO.HIGH)  # alternate the FR to ring
				time.sleep(ringDelay)
				if ( GPIO.input(SHKpin5) == 1 ):  # check if we lifted handset
					GPIO.output(RMpin4, GPIO.LOW)  # set RM back to low before stopping
					return  # exit function
			GPIO.output(RMpin4, GPIO.LOW)  # set RM low between rings
			time.sleep(1)


try:

	ringPhone(2)

	# phoneID=2
	# if phoneID == 1:
	# 	FRpin3=FRpin3_1
	# 	RMpin4=RMpin4_1
	# 	SHKpin5=SHKpin5_1
	# elif phoneID == 2:
	# 	FRpin3=FRpin3_2
	# 	RMpin4=RMpin4_2
	# 	SHKpin5=SHKpin5_2

	# GPIO.output(RMpin4, GPIO.LOW)  # set RM high
	# GPIO.output(FRpin3, GPIO.LOW)
	# while True:
	# 	GPIO.output(RMpin4, GPIO.LOW)  # set RM high
	# 	GPIO.output(FRpin3, GPIO.HIGH)

	# GPIO.output(FRpin3, GPIO.LOW)  # alternate the FR to ring



finally:
	GPIO.cleanup()
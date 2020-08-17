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
# from scipy import signal # sudo apt-get install python3-scipy

# check/define audio in/out ports:?

# define devices in an array:
# [device0, device1] as deviceIndex

# GPIO definitions: 
FRpin3=[14,3]
RMpin4=[15,2]
SHKpin5=[18,4]

# FRpin3_1=14
# RMpin4_1=15
# SHKpin5_1=18

# # 2nd phone system:
# FRpin3_2=3
# RMpin4_2=2
# SHKpin5_2=4

# set volume and mic gain for devices:
# use "aplay -l" to list audio cards
# config sound cards using py
print('setting default amixer controls')
amixerDevice1=2  # this is the hw device number from hw:2,0 or hw:3,0
amixerDevice2=3
os.system("amixer -c "+str(amixerDevice1)+" set 'Auto Gain Control' off")
os.system("amixer -c "+str(amixerDevice1)+" set 'Speaker' 100%")
os.system("amixer -c "+str(amixerDevice1)+" set 'Mic' 30%")
# os.system("amixer -c "+str(amixerDevice1))

os.system("amixer -c "+str(amixerDevice2)+" set 'Auto Gain Control' off")
os.system("amixer -c "+str(amixerDevice2)+" set 'Speaker' 100%")
os.system("amixer -c "+str(amixerDevice2)+" set 'Mic' 25%")
# os.system("amixer -c "+str(amixerDevice2))



debounceDelay=5  # ms
maxPulseInterval=250 # ms  Max separation between digits being dialed
hookDelay = 250 # ms. 

#SHK_state_1 = 0
shkReading = [0,0]
previousshkReading = [1,1]
state=["ON_HOOK","ON_HOOK"]

#SHK_state_2 = 0
# shkReading2 = 0
# previousshkReading2 = 1
# state2="ON_HOOK"

ItalianMode=[0,0]
playRecording = [0,0]
# playRecording2 = 0

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

# offsets for tone callbacks:
offset1 = 0.0
offset2 = 0.0

# GPIO.cleanup()
GPIO.setwarnings(True)  # can set to False by default later
GPIO.setmode(GPIO.BCM) # use GPIO pin numbering 
# phone #1
GPIO.setup(FRpin3[0], GPIO.OUT)
GPIO.setup(RMpin4[0], GPIO.OUT)
GPIO.setup(SHKpin5[0], GPIO.IN)
# phone #2:
GPIO.setup(FRpin3[1], GPIO.OUT)
GPIO.setup(RMpin4[1], GPIO.OUT)
GPIO.setup(SHKpin5[1], GPIO.IN)

# initialize pyaudio:
p=pyaudio.PyAudio()
# p2=pyaudio.PyAudio()

# ring once so we know when we're ready:
# print("ringing phone once")
# ringDelay = 0.04   # 40ms
# GPIO.output(RMpin4[0], GPIO.HIGH)  # set RM high
# time.sleep(0.01)
# GPIO.output(FRpin3[0], GPIO.LOW)  # alternate the FR to ring
# time.sleep(ringDelay)
# GPIO.output(FRpin3[0], GPIO.HIGH)  # alternate the FR to ring
# time.sleep(ringDelay)
# GPIO.output(RMpin4[0], GPIO.LOW)  # set RM low between rings


# current time in ms:
def now_ms():
	now = int(round(time.time() *1000))  # time in ms
	return now

def dialToneCallback1(in_data, frames, time_info, status):
	# add reference to web site that helped explain this:
	# https://markhedleyjones.com/projects/python-tone-generator
	# equation: sin( 2*pi*f * (t + to) ). # t is in samples, so t/sampleRate = time
	global offset1
	tones=[350,450]
	out = numpy.zeros(frames, dtype=numpy.float32)
	t=(numpy.arange(frames,dtype=numpy.float32)+offset1)/sampleRate
	out += numpy.sin(2*numpy.pi * float(tones[0]) *  t)
	out += numpy.sin(2*numpy.pi * float(tones[1]) *  t)
	out /= len(tones) # keep maximum constant
	offset1 += frames
	return(out, pyaudio.paContinue)

def dialToneCallback2(in_data, frames, time_info, status):
	global offset2
	tones=[350,450]
	out = numpy.zeros(frames, dtype=numpy.float32)
	t=(numpy.arange(frames,dtype=numpy.float32)+offset2)/sampleRate
	out += numpy.sin(2*numpy.pi * float(tones[0]) *  t)
	out += numpy.sin(2*numpy.pi * float(tones[1]) *  t)
	out /= len(tones) # keep maximum constant
	offset2 += frames
	return(out, pyaudio.paContinue)

def ringToneCallback1(in_data, frames, time_info, status):
	global offset1
	tones=[440,480]
	toneDuration=2
	toneDelay=4
	maskPeriod=(toneDuration + toneDelay)
	# maskFreq=1/maskPeriod
	dutyCycle=toneDuration/(toneDuration+toneDelay)

	out = numpy.zeros(frames, dtype=numpy.float32)
	t=(numpy.arange(frames,dtype=numpy.float32)+offset1)/sampleRate
	# for this frame, determine the overall square wave mask:
	rem = numpy.mod(t,maskPeriod)
	mask= rem < (dutyCycle * maskPeriod)
	out += numpy.sin(2*numpy.pi * float(tones[0]) *  t)
	out += numpy.sin(2*numpy.pi * float(tones[1]) *  t)
	out /= len(tones)
	out *= mask
	offset1 += frames
	return(out, pyaudio.paContinue)

def ringToneCallback2(in_data, frames, time_info, status):
	global offset2
	tones=[440,480]
	toneDuration=2
	toneDelay=4
	maskPeriod=(toneDuration + toneDelay)
	# maskFreq=1/maskPeriod
	dutyCycle=toneDuration/(toneDuration+toneDelay)

	out = numpy.zeros(frames, dtype=numpy.float32)
	t=(numpy.arange(frames,dtype=numpy.float32)+offset2)/sampleRate
	# for this frame, determine the overall square wave mask:
	rem = numpy.mod(t,maskPeriod)
	mask= rem < (dutyCycle * maskPeriod)
	out += numpy.sin(2*numpy.pi * float(tones[0]) *  t)
	out += numpy.sin(2*numpy.pi * float(tones[1]) *  t)
	out /= len(tones)
	out *= mask
	offset2 += frames
	return(out, pyaudio.paContinue)

def busyToneCallback1(in_data, frames, time_info, status):
	global offset1
	tones=[480,620]
	toneDuration=0.5
	toneDelay=0.5
	maskPeriod=(toneDuration + toneDelay)
	# maskFreq=1/maskPeriod
	dutyCycle=toneDuration/(toneDuration+toneDelay)
	out = numpy.zeros(frames, dtype=numpy.float32)
	t=(numpy.arange(frames,dtype=numpy.float32)+offset1)/sampleRate
	# for this frame, determine the overall square wave mask:
	rem = numpy.mod(t,maskPeriod)
	mask= rem < (dutyCycle * maskPeriod)
	out += numpy.sin(2*numpy.pi * float(tones[0]) *  t)
	out += numpy.sin(2*numpy.pi * float(tones[1]) *  t)
	out /= len(tones)
	out *= mask
	offset1 += frames
	return(out, pyaudio.paContinue)

def busyToneCallback2(in_data, frames, time_info, status):
	global offset2
	tones=[480,620]
	toneDuration=0.5
	toneDelay=0.5
	maskPeriod=(toneDuration + toneDelay)
	# maskFreq=1/maskPeriod
	dutyCycle=toneDuration/(toneDuration+toneDelay)
	out = numpy.zeros(frames, dtype=numpy.float32)
	t=(numpy.arange(frames,dtype=numpy.float32)+offset2)/sampleRate
	# for this frame, determine the overall square wave mask:
	rem = numpy.mod(t,maskPeriod)
	mask= rem < (dutyCycle * maskPeriod)
	out += numpy.sin(2*numpy.pi * float(tones[0]) *  t)
	out += numpy.sin(2*numpy.pi * float(tones[1]) *  t)
	out /= len(tones)
	out *= mask
	offset2 += frames
	return(out, pyaudio.paContinue)

def tone(toneName,p,deviceIndex):
	print("tone " + toneName + " " + "device="+ str(deviceIndex))
	if deviceIndex == 0:
		toneCallback=eval(toneName+"Callback1")
	elif deviceIndex == 1:
		toneCallback=eval(toneName+"Callback2")

	s = p.open(output_device_index=pyaudioDevID(deviceIndex), frames_per_buffer=2048, 
			format=pyaudio.paFloat32, channels=1, 
			rate=sampleRate, output=True, stream_callback=toneCallback)
	s.start_stream()
	return s

def stopSound(stream=None,wf=None,processID=None):
	# print('StopSound')
	# print(stream)
	if stream:
		print('stop stream')
		stream.stop_stream()
		stream.close()
	if wf:
		print('close wf')
		# print(wf)
		wf.close()
	if processID:
		print('stopping process')
		os.killpg(processID.pid, signal.SIGTERM)
		processID.terminate()
		print("sox 1-2 stopped")
		# return processID
	stream=None
	wf=None
	processID=None
	return stream,wf,processID

def pyaudioListDevices(p):
	print("Listing pyAudio devices:")
	# p = pyaudio.PyAudio()
	info = p.get_host_api_info_by_index(0)
	numdevices = info.get('deviceCount')
	print('Number of devices is '+str(numdevices))
	#for each audio device, determine if is an input or an output and add it to the appropriate list and dictionary
	for i in range (0,numdevices):
	        if p.get_device_info_by_host_api_device_index(0,i).get('maxInputChannels')>0:
	                print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0,i).get('name'))

	        if p.get_device_info_by_host_api_device_index(0,i).get('maxOutputChannels')>0:
	                print("Output Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0,i).get('name'))

	devinfo = p.get_device_info_by_index(1)
	print("Default device is ",devinfo.get('name'))
	# if p.is_format_supported(44100.0,  # Sample rate
 #         input_device=devinfo["index"],
 #         input_channels=devinfo['maxInputChannels'],
 #         input_format=pyaudio.paInt16):
	print('Done')
	# p.terminate()

def streamSound(hw1,hw2,callMode):
	# hw1='hw:2'
	# hw2='hw:3'
	soxbuffer='512'  # 256 gives lots of errors and won't quit
	rate='44100'
	if (callMode == 'call'):
		proc_args = ['sox', '--buffer', soxbuffer, '-c1' , '-r' , 
		rate , '-t', 'alsa', hw1, '-t', 'alsa', hw2]
	elif (callMode == 'high'):
		proc_args = ['sox', '--buffer', soxbuffer, '-c1' , '-r' , 
		rate , '-t', 'alsa', hw1, '-t', 'alsa', hw2, 'pitch', '600']
	elif (callMode == 'low'):
		proc_args = ['sox', '--buffer', soxbuffer, '-c1' , '-r' , 
		rate , '-t', 'alsa', hw1, '-t', 'alsa', hw2, 'pitch', '-400']
	elif (callMode == 'dalek'):
		proc_args = ['sox', '--buffer', soxbuffer, '-c1' , '-r' , 
		rate , '-t', 'alsa', hw1, '-t', 'alsa', hw2, "synth", "0", "sine", "amod", "30", "pitch", "400", "gain", "4"]

	print(proc_args)
	# notes:
	# shell=False works.  
	# preexec_fn=os.setsid is to make the process continue even if the calling function quits
	# adding stderr=subprocess.DEVNULL will redirect stderr to /dev/null
	rec_proc = subprocess.Popen(proc_args, shell=False, 
		preexec_fn=os.setsid, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
	print("sox " + hw1 + ' --> ' + hw2 + " pid= " + str(rec_proc.pid) + ' started')
	return rec_proc

# def stopStreamSound(processID):
# 	os.killpg(processID.pid, signal.SIGTERM)
# 	processID.terminate()
# 	processID = None
# 	print("sox 1-2 stopped")
# 	return processID

# pyaudio examples:
# https://people.csail.mit.edu/hubert/pyaudio/docs/
def recordSound(deviceIndex):
	# record something
	outfile = tmpdir+'recording.wav'
	print('recording to '+ outfile)
	# micAudio = pyaudio.PyAudio(). # using p now
	chunk=4096
	record_secs=10  # Maximum recording time
	# input device needs to be the correct number, but it's not the HW number from "aplay -l"
	# to get the correct device, use this function:
	# pyaudioListDevices()
	s = p.open(format = pyaudio.paInt16, rate=sampleRate, 
		channels=1, input_device_index=pyaudioDevID(deviceIndex), input=True, 
		frames_per_buffer=4096)
	frames=[]
	# loop through stream and append audio chunks to frame array
	for ii in range(0,int((sampleRate/chunk)*record_secs)):
	    data = s.read(chunk)
	    frames.append(data)
	    # check for hangup condition
	    if ( GPIO.input(SHKpin5[deviceIndex]) == 0 ):  # if on hook, stop
	    	break
	print("finished recording")
	# stop the stream, close it
	s.stop_stream()
	s.close()

	# save the audio frames as .wav file
	wavefile = wave.open(outfile,'wb')
	wavefile.setnchannels(1)
	wavefile.setsampwidth(p.get_sample_size(pyaudio.paInt16))
	wavefile.setframerate(sampleRate)
	wavefile.writeframes(b''.join(frames))
	wavefile.close()
	return outfile

# see http://people.csail.mit.edu/hubert/pyaudio/ for playing wav files using callback
def playCallback1(in_data, frame_count, time_info, status):
	global wf
	data = wf[0].readframes(frame_count)
	return(data, pyaudio.paContinue)

def playCallback2(in_data, frame_count, time_info, status):
	global wf
	data = wf[1].readframes(frame_count)
	return(data, pyaudio.paContinue)

def playFile(filename,p, deviceIndex):
	print('PlayFile')
	CHUNK=4096
	global wf
	wf[deviceIndex] = wave.open(filename, 'rb')
	if deviceIndex == 0:
		stream[deviceIndex] = p.open(format=p.get_format_from_width(wf[deviceIndex].getsampwidth()),
	        channels=wf[deviceIndex].getnchannels(), 
	        output_device_index=pyaudioDevID(deviceIndex),
	        rate=wf[deviceIndex].getframerate(), frames_per_buffer=CHUNK,
	        output=True, stream_callback=playCallback1)
	elif deviceIndex == 1:
		stream[deviceIndex] = p.open(format=p.get_format_from_width(wf[deviceIndex].getsampwidth()),
	        channels=wf[deviceIndex].getnchannels(), 
	        output_device_index=pyaudioDevID(deviceIndex),
	        rate=wf[deviceIndex].getframerate(), frames_per_buffer=CHUNK,
	        output=True, stream_callback=playCallback2)
	return(stream[deviceIndex],wf[deviceIndex])

def playComplete(filename,p,deviceIndex):
	print('PlayComplete')
	CHUNK=4096
	wf3 = wave.open(filename, 'rb')
	# print('format='+str(p.get_format_from_width(wf3.getsampwidth())) + 
		# ' channels='+str(wf3.getnchannels())+ ' rate='+str(wf3.getframerate()))
	stream3 = p.open(format=p.get_format_from_width(wf3.getsampwidth()),
        channels=wf3.getnchannels(),
        rate=wf3.getframerate(), output_device_index=pyaudioDevID(deviceIndex),
        output=True, frames_per_buffer=CHUNK)
	data = wf3.readframes(CHUNK)
	while len(data) > 0:
		stream3.write(data)
		data = wf3.readframes(CHUNK)
		if ( GPIO.input(SHKpin5[deviceIndex]) == 0 ):  # check if we hung up
				GPIO.output(RMpin4[deviceIndex], GPIO.LOW)  # set RM back to low before stopping
				stream3.stop_stream()
				stream3.close()
				wf3.close()
				return  # exit function
	# print("playComplete: stopping stream")
	stream3.stop_stream()
	stream3.close()
	wf3.close()
	# return stream3,wf3	
	print('done with playComplete')

def playNumber(number,p, deviceIndex):
	print('PlayNumber')
	if number == '.':
		numberFile='/home/pi/Telephone/Audio/numbers/p.wav'
	else:
		if ( ItalianMode[deviceIndex] == 1 ):
			numberFile='/home/pi/Telephone/Audio/numbers_IT/'+str(number)+'.wav'
		else:
			numberFile='/home/pi/Telephone/Audio/numbers/'+str(number)+'.wav'
	print(numberFile)
	playComplete(numberFile,p,deviceIndex)

	# sound=pygame.mixer.Sound(numberFile)
	# mysound=sound.play()
	# while mysound.get_busy():
	# 	pygame.time.delay(10)

def ringPhone(deviceIndex):
	print("ringing phone " + str(deviceIndex))
	# getShkReading(device)
	ringDelay=[0.04,0.05]
	# ringDelay = 0.04   # 40ms = 25Hz
	# ringDelay = 0.05   # 50ms = 20Hz
	# print('FR='+str(FRpin3[deviceIndex])+' RM='+str(RMpin4[deviceIndex])+' SHK='+str(SHKpin5[deviceIndex]))
	# print('shkState='+str(GPIO.input(SHKpin5[deviceIndex])))
	while ( GPIO.input(SHKpin5[deviceIndex]) == 0 ): # while on hook (SHK=0)
		print('Ring...')
		GPIO.output(RMpin4[deviceIndex], GPIO.HIGH)  # set RM high
		time.sleep(0.01)
		rings=round(1/ringDelay[deviceIndex])+1
		for i in range(1,rings):
			GPIO.output(FRpin3, GPIO.LOW)  # alternate the FR to ring
			time.sleep(ringDelay[deviceIndex])
			GPIO.output(FRpin3, GPIO.HIGH)  # alternate the FR to ring
			time.sleep(ringDelay[deviceIndex])
			if ( GPIO.input(SHKpin5[deviceIndex]) == 1 ):  # check if we lifted handset
				GPIO.output(RMpin4[deviceIndex], GPIO.LOW)  # set RM back to low before stopping
				return  # exit function
		GPIO.output(RMpin4[deviceIndex], GPIO.LOW)  # set RM low between rings
		time.sleep(3)

## audio modifications:
def highPitch(filename): # high pitch
	# filename=string.lower(filename)
	outfile=filename.replace('.wav','_new.wav')
	print(outfile)
	subprocess.run(["/usr/bin/sox", filename, outfile, "pitch", "600"])
	return outfile

def lowPitch(filename): # low pitch
	outfile=filename.replace('.wav','_new.wav')
	print(outfile)
	subprocess.run(["/usr/bin/sox", filename, outfile, "pitch", "-400"])
	return outfile

def dalek(filename):  # dalek
	outfile=filename.replace('.wav','_new.wav')
	print(outfile)
	# get file duration:
	# duration = subprocess.run(["soxi", "-D", filename])
	# print(duration)
	# create 30Hz sine wave:
	subprocess.run(["/usr/bin/sox", filename, outfile, "synth", "0", "sine", "amod", "30", "pitch", "400", "gain", "4"])
	return outfile

def speedUp(filename): # speed up
	outfile=filename.replace('.wav','_new.wav')
	print(outfile)
	subprocess.run(["/usr/bin/sox", filename, outfile, "speed", "2"])
	return outfile

def pyaudioDevID(deviceIndex):
	# return the pyaudio device ID (depends on audio card location)
	hw1=0  # device ID for phone#1  from pyaudioListDevices
	hw2=1	# device ID for phone#2 from pyaudioListDevices
	it=[hw1,hw2]
	return it[deviceIndex]

################### 
pyaudioListDevices(p)  # uncomment to get device ID numbers

# hw1=1  # device ID for phone#1  from pyaudioListDevices
# hw2=0	# device ID for phone#2 from pyaudioListDevices
# pyaudioDevID=[hw1,hw2]
timeLastOnHook=[now_ms(),now_ms()]
timeLastOffHook=[now_ms(),now_ms()]
timeShkChanged=[now_ms(),now_ms()]
phoneNumber=[[],[]]
pulseCount=[0,0]
ringOnNextHangup=[0,0]
# stream1=None
stream=[None,None]
wf=[None,None]
streamProcess=[None,None]  # stream process for streaming through sox from phone-phone
callingMode=[None,None]

devices=[0,1]
# main loop:
try:
	while True:

		for i in devices:  # loop over each phone
			# listen for offhook condition
			now = now_ms()  # time in ms

			# debounce hook switch
			shkReading[i] = GPIO.input(SHKpin5[i])
			# print('SHK1='+str(shkReading[0])+' SHK2='+str(shkReading[1])+' state='+str(state))
			if shkReading[i] == 1 :  # off hook
				timeLastOffHook[i] = now
			elif shkReading[i] == 0 :  # on hook
				timeLastOnHook[i] = now

			# if off hook now but not before
			if ( shkReading[i] == 1 ) and ( state[i] == 'ON_HOOK') :  # transition to OFF_HOOK
				previousshkReading[i]=shkReading[i]	
				if ( now - timeLastOnHook[i] > hookDelay ) :
					print(str(i)+" Offhook")
					state[i] = "OFF_HOOK"
					timeLastOnHook[i] = now
					if ( playRecording[i] == 1 ):
						# time.sleep(1)
						thisfile=tmpdir+'recording.wav'
						print('playing '+thisfile)
						playComplete(thisfile,p,i)  # wait until finished
						stream[i] = tone('dialTone',p,i)
						playRecording[i]=0
					else:
						print('running dialTone for phone '+str(i))
						stream[i] = tone('dialTone',p,i)
			# else if on hook now, but was off hook previously
			elif ( shkReading[i] == 0 ) and ( state[i] != "ON_HOOK") :  # transition to ON_HOOK
				previousshkReading[i]=shkReading[i]	
				if ( now - timeLastOffHook[i] > hookDelay ) :
					print("1 Onhook")
					state[i] = "ON_HOOK"
					timeLastOffHook[i] = now
					# stop any playing audio:
					stream[i],wf[i],streamProcess1=stopSound(stream[i],wf[i],streamProcess[i])
					pulseCount[i]=0
					phoneNumber[i]=[]
					if ( ringOnNextHangup[i] == 1 ):
						print("ringing in 3s...")
						time.sleep(3)
						ringPhone(i)
						ringOnNextHangup[i]=0

			#################  Phone dialing
			## if off hook, check for dialing:
			if ( state[i] == 'OFF_HOOK' ) or ( state[i] == 'DIALING'):
				# deviceIndex=0
				# check for SHK values changing to indicate a dialed number:
				if ( shkReading[i] != previousshkReading[i] ):
					state[i] = 'DIALING'
					# stop audio if it's playing
					stream[i],wf[i],streamProcess[i]=stopSound(stream[i],wf[i],streamProcess[i])
					if ( now - timeShkChanged[i] < debounceDelay ):  # debounce SHK:
						continue  # go back to top while state[i]
					if ( shkReading[i] == 1 ):  # dial pulse detected
						pulseCount[i]=pulseCount[i] + 1 # number of pulses gives the number dialed
					timeShkChanged[i] = now_ms()
					previousshkReading[i] = shkReading[i]
				if ( now - timeShkChanged[i] >= maxPulseInterval ) and ( pulseCount[i] > 0 ) :
					# wait a certain time before assuming it's the end of the dialed digit
					if (pulseCount[i] == 10 ): 
						pulseCount[i] = 0 # zero is equal to 10 pulses
					print("Digit dialed = "+str(pulseCount[i]))
					# speak the digit on the speaker:
					# append the digit dialed to the number array:
					phoneNumber[i].append(pulseCount[i])
					print("PhoneNumber1=" + str(phoneNumber[i]))
					playNumber(pulseCount[i],p,i)
					print("after PlayNumber")
					playRecording[i]=0
					# Single numbers dialed:
					if (phoneNumber[i] == [6]):
						state[i]='CONNECTED'
						print('Playing Amore')
						if ItalianMode[i] == 1 :
							stream[i],wf[i]=playFile('/home/pi/Telephone/Audio/thats_amore.wav',p,i)
						else:
							stream[i],wf[i]=playFile('/home/pi/Telephone/Audio/ringfire.wav',p,i)
					elif (phoneNumber[i] == [7]):
						state[i]='CONNECTED'
						time.sleep(1)
						stream[i],wf[i]=playFile('/home/pi/Telephone/Audio/burp.wav',p,i)
					elif (phoneNumber[i] == [8]):
						state[i]='CONNECTED'
						if ItalianMode[i] == 1 :
							stream[i],wf[i]=playFile('/home/pi/Telephone/Audio/crocfa.wav',p,i)
						else:
							stream[i],wf[i]=playFile('/home/pi/Telephone/Audio/crocodile_rock.wav',p,i)
					elif (phoneNumber[i] == [9]):
						state[i]='CONNECTED'
						stream[i],wf[i]=playFile('/home/pi/Telephone/Audio/martians.wav',p.i)

					# single phone mode:  repeat things back to same phone
					elif (phoneNumber[i] == [1,2,3]):
						state[i]='CONNECTED'
						if ItalianMode[i] == 1 :
							playComplete('/home/pi/Telephone/Audio/dimmi.wav',p,i)
						else:
							playComplete('/home/pi/Telephone/Audio/speak.wav',p,i)
						recordSound(i)
						ringOnNextHangup[i]=1
						playRecording[i]=1
					elif (phoneNumber[i] == [1,2,4]):  # high voice
						state[i]='CONNECTED'
						if ItalianMode[i] == 1 :
							playComplete('/home/pi/Telephone/Audio/dimmi.wav',p,i)
						else:
							playComplete('/home/pi/Telephone/Audio/speak.wav',p,i)
						outfile = recordSound(i)
						# playFile('/home/pi/Telephone/Audio/plshup.wav')
						highFile = highPitch(outfile)
						os.rename(highFile,outfile)
						ringOnNextHangup[i]=1
						playRecording[i]=1
					elif (phoneNumber[i] == [1,2,5]):  # low voice
						state[i]='CONNECTED'
						if ItalianMode[i] == 1 :
							playComplete('/home/pi/Telephone/Audio/dimmi.wav',p,i)
						else:
							playComplete('/home/pi/Telephone/Audio/speak.wav',p,i)
						outfile = recordSound(i)
						lowFile = lowPitch(outfile)
						os.rename(lowFile,outfile)
						# playFile('/home/pi/Telephone/Audio/plshup.wav')
						ringOnNextHangup[i]=1
						playRecording[i]=1
					elif (phoneNumber[i] == [1,2,8]):  # dalek
						state[i]='CONNECTED'
						if ItalianMode[i] == 1 :
							playComplete('/home/pi/Telephone/Audio/dimmi.wav',p,i)
						else:
							playComplete('/home/pi/Telephone/Audio/speak.wav',p,i)
						outfile = recordSound(i)
						lowFile = dalek(outfile)
						os.rename(lowFile,outfile)
						# playFile('/home/pi/Telephone/Audio/plshup.wav')
						ringOnNextHangup[i]=1
						playRecording[i]=1

					# calling other phone:
					elif (phoneNumber[i] == [2,2,3]): # call other phone
						state[i]='CALLING'
						callingMode[i]='call'
						print('2,3,3: Calling...')
						
					elif (phoneNumber[i] == [2,2,4]):  # high voice
						state[i]='CALLING'
						callingMode[i]='high'
#					elif (phoneNumber[i] == [2,2,5]):  # low voice
#						state[i]='CALLING'
#						callingMode[i]='low'
					elif (phoneNumber[i] == [2,2,8]):  # dalek
						state[i]='CALLING'
						callingMode[i]='dalek'


					# phone "functions"
					elif (phoneNumber[i] == [0,3,9]):  # Italy country code. Switch to Italian
						print("Entering Italian mode. Use '01' to switch back to English")
						playComplete('/home/pi/Telephone/Audio/buongiorno.wav',p,i)
						phoneNumber[i]=[]
						ItalianMode[i]=1
						stream[i] = tone('dialTone',p,i)
					elif (phoneNumber[i] == [0,1]):  # US country code. Switch to English
						print("Returning to English mode.")
						playComplete('/home/pi/Telephone/Audio/hithere.wav',p,i)
						phoneNumber[i]=[]
						ItalianMode[i]=0
						stream[i] = tone('dialTone',p,i)
					# a single dialed digit has been processed, so reset the pulse counter:
					pulseCount[i]=0
			

			if ( state[i] == 'CALLING' ):  # trying to call other phone
				print('Calling mode')
				# call other phone:
				# try to ring other phone:
				# check if other phone is offhook or not
				if ( state[i-1] != 'ON_HOOK'):
					# if other phone is offhook, play busy tone and continue.
					stream[i] = tone('busyTone',p,i) # play on calling phone
					state[i] = 'BUSY'
					# play busy tone until hangup
				elif ( state[i-1] == 'ON_HOOK'):
					# if other phone is onhook, ring other phone
					# play ring tone
					stream[i] = tone('ringTone',p,i) # play on calling phone
					# ring phone:
					ringPhone(i-1)
					# wait for pickup
					while ( GPIO.input(SHKpin5[i-1]) == 0 ): # while other phone is on hook (SHK=0)
						# wait for pickup
						time.delay(0.1)
						# if we get a hangup on calling phone, then exit
						if GPIO.input(SHKpin5[i]) == 0:
							break
					if ( GPIO.input(SHKpin5[i-1]) == 1 ):  # other phone off hook
						# when offhook, stream audio to other phone:
						# stop ring tone to calling phone:
						stream[0],wf[0],streamProcess[0]=stopSound(stream[0],wf[i],streamProcess[0])
						stream[1],wf[1],streamProcess[1]=stopSound(stream[1],wf[1],streamProcess[1])	
						print('streaming sound')
						streamProcess[0] = streamSound('hw:2','hw:3',callingMode[i])
						streamProcess[1] = streamSound('hw:3','hw:2',callingMode[i])
						print('after streamSound')
						# wait for hangup on either end
						while GPIO.input(SHKpin5[i]) == 1 and GPIO.input(SHKpin5[i-1]) == 1:  # wait until a hangup
							time.sleep(0.1)
						# after hangup, kill previous audio streams:
						stream[0],wf[0],streamProcess[0]=stopSound(stream[0],wf[0],streamProcess[0])
						stream[1],wf[1],streamProcess[1]=stopSound(stream[1],wf[1],streamProcess[1])
						state[0] = 'ON_HOOK'
						state[1] = 'ON_HOOK'
						pulseCount[i]=0  # clear dialing counters
						phoneNumber[i]=[]


finally:
	# stop streams
	stream[0],wf[0],streamProcess[0]=stopSound(stream[0],wf[0],streamProcess[0])
	stream[1],wf[1],streamProcess[1]=stopSound(stream[1],wf[1],streamProcess[1])					
	GPIO.cleanup()
	# terminate pyaudio
	p.terminate()


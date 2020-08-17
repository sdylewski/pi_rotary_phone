# check sck status:

import RPi.GPIO as GPIO
import pyaudio
import wave

# GPIO definitions:
FRpin3_1=14
RMpin4_1=15
SHKpin5_1=18

# 2nd phone system:
FRpin3_2=2
RMpin4_2=3
SHKpin5_2=4

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

tmpdir='/home/pi/Telephone/Audio/tmp/'
p=pyaudio.PyAudio()

try:
    sampleRate=44100
    deviceIndex=0
    outfile = tmpdir+'recording.wav'
    print('recording to '+ outfile)
    # micAudio = pyaudio.PyAudio(). # using p now
    chunk=4096
    record_secs=10  # Maximum recording time
    # input device needs to be the correct number, but it's not the HW number from "aplay -l"
    # to get the correct device, use this function:
    # pyaudioListDevices()
    s = p.open(format = pyaudio.paInt16, rate=sampleRate, 
        channels=1, input_device_index=deviceIndex, input=True, frames_per_buffer=4096)
    print('recording')
    frames=[]
    # loop through stream and append audio chunks to frame array
    print(str(int((sampleRate/chunk)*record_secs)))
    for ii in range(0,int((sampleRate/chunk)*record_secs)):
        data = s.read(chunk)
        frames.append(data)
        # check for hangup condition
        if ( GPIO.input(SHKpin5_1) == 0 ):  # if on hook, stop
            print('onhook, stopping!')
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


    filename=outfile
    print('PlayComplete')
    CHUNK=4096
    wf3 = wave.open(filename, 'rb')
    print('format='+str(p.get_format_from_width(wf3.getsampwidth())) + 
        ' channels='+str(wf3.getnchannels())+ ' rate='+str(wf3.getframerate()))
    stream3 = p.open(format=p.get_format_from_width(wf3.getsampwidth()),
        channels=1,
        rate=44100, output_device_index=deviceIndex,
        output=True, frames_per_buffer=CHUNK)
    data = wf3.readframes(CHUNK)
    while len(data) > 0:
        print(len(data))
        stream3.write(data)
        data = wf3.readframes(CHUNK)
    stream3.stop_stream()
    stream3.close()
    wf3.close()
    # return stream3,wf3    
    print('done with playComplete')


    # while True:
    #     frReading_1 = GPIO.input(FRpin3_1)
    #     frReading_2 = GPIO.input(FRpin3_2)

    #     rmReading_1 = GPIO.input(RMpin4_1)
    #     rmReading_2 = GPIO.input(RMpin4_2)

    #     shkReading_1 = GPIO.input(SHKpin5_1)
    #     shkReading_2 = GPIO.input(SHKpin5_2)

    #     print("FR1="+str(frReading_1)+
    #             " FR2="+str(frReading_2)+
    #             " RM1="+str(rmReading_1)+
    #             " RM2="+str(rmReading_2)+
    #             " SHK1="+str(shkReading_1)+
    #             " SHK2="+str(shkReading_2))


finally:
    GPIO.cleanup()

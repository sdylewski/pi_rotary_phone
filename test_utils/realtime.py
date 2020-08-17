# test of running 2-way audio:
# Scott Dylewski
# for raspberry pi
import subprocess
import os
import time
import signal


print('setting default amixer controls')
amixerDevice1=2  # this is the hw device number from hw:2,0 or hw:3,0
amixerDevice2=3
os.system("amixer -c "+str(amixerDevice1)+" set 'Auto Gain Control' off")
os.system("amixer -c "+str(amixerDevice1)+" set 'Speaker' 100%")
os.system("amixer -c "+str(amixerDevice1)+" set 'Mic' 25%")
# os.system("amixer -c "+str(amixerDevice1))

os.system("amixer -c "+str(amixerDevice2)+" set 'Auto Gain Control' off")
os.system("amixer -c "+str(amixerDevice2)+" set 'Speaker' 100%")
os.system("amixer -c "+str(amixerDevice2)+" set 'Mic' 25%")

# while (10 seconds?)
# first start audio stream from 1 --> 2  High pitch
hw1='hw:2'
hw2='hw:3'
soxbuffer='1024'  # 256 gives lots of errors and won't quit
rate='44100'
proc_args1 = ['sox', '--buffer', soxbuffer, '-c1' , '-r' , rate , '-t', 'alsa', hw1, '-t', 'alsa', hw2, 'pitch', '600']
print(proc_args1)
# notes:
# shell=False works.  
# preexec_fn=os.setsid is to make the process continue even if the calling function quits
# adding stderr=subprocess.DEVNULL will redirect stderr to /dev/null
#rec_proc1 = subprocess.Popen(proc_args1, shell=False, preexec_fn=os.setsid, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
rec_proc1 = subprocess.Popen(proc_args1, shell=False, preexec_fn=os.setsid, stdout=None, stderr=None)
print("sox 1-2 pid= " + str(rec_proc1.pid))
print("sox 1-2 started")

# then start audio stream from 2 --> 1  Low pitch
proc_args2 = ['sox', '--buffer', soxbuffer, '-c1' , '-r' , rate , '-t', 'alsa', hw2, '-t', 'alsa', hw1, 'pitch', '600']
print(proc_args2)
rec_proc2 = subprocess.Popen(proc_args2, shell=False, preexec_fn=os.setsid, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print("sox 2-1 pid= " + str(rec_proc2.pid))
print("sox 2-1 started")

print("...")
time.sleep(5)

# kill first stream:
os.killpg(rec_proc1.pid, signal.SIGTERM)
rec_proc1.terminate()
rec_proc1 = None
print("sox 1-2 stopped")

# kill second stream:
os.killpg(rec_proc2.pid, signal.SIGTERM)
rec_proc2.terminate()
rec_proc2 = None
print("sox 2-1 stopped")



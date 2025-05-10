from pijuice import PiJuice
import subprocess

pj = PiJuice(1, 0x14)
pj.power.SetPowerOff(20)
pj.rtcAlarm.SetWakeupEnabled(True)
subprocess.call(["sudo", "poweroff"])

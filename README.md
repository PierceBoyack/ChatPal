This project is a voice controlled AI assistant for Raspberry PI. It uses memory, thinking, and, grounding budgets to maintain a powerful, but cost-effective agent on a small device.

This project was built for use on a 64-bit Raspberry Pi system. In particular, I used a Raspberry Pi 5 with 2GB RAM.

Some important requirements and need-to-knows:
* Importing sounddevice in the voiceCommand files is important. Nobody seems to know why, but there is conjecture that it is due to how sounddevice loads PortAudio libraries. Without importing this, you will receive a variety of ALSA and jack server errors and warnings.
* Raspberry Pi does not have a built-in microphone. If attaching a USB microphone to the Pi, you may have to manually designate it as the default audio device. You may have to edit the ```~/.asoundrc``` file on your device. You can use ```$ arecord -l``` to view your capture devices. An example might return:
  
```
**** List of CAPTURE Hardware Devices ****
card 2: Device [USB PnP Sound Device], device 0: USB Audio [USB Audio]
  Subdevices: 1/1
  Subdevice #0: subdevice #0
```

Using this information, ```nano ~/.asoundrc``` and edit the file config accordingly to set the default audio device. Following this example, we'd input:
```
pcm.!default {
    type plug
    slave.pcm "hw:2,0"
}

ctl.!default {
    type hw
    card 2
}
```

Let's say you move your USB mic to a different port occasionally. In that case, you can try assigning the default mic via device name instead of by card and device number:
```
pcm.!default {
    type plug
    slave.pcm "mic_usb"
}

ctl.!default {
    type hw
    card "USB PnP Sound Device"
}

pcm.mic_usb {
    type hw
    card "USB PnP Sound Device"
    device 0
}
```
You can also purchase a mircophone breakout from Adafruit or another company. This will require a little soldering, but works just as well if you're trying to get a mic hooked up to your Pi. I recommend this one: https://www.adafruit.com/product/3421

I use Picovoice for wake word detection. You can train custom wake words on their website. I use a custom version in main.py.

TTS is done using Piper: https://github.com/OHF-Voice/piper1-gpl/tree/main .
If you want to use TTS, you will have to download a voice model found in this repository and also give your Pi a way to output sound. I am using a USB speaker: https://www.adafruit.com/product/3369

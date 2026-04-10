# Train-Departure-Board
This repository contains the code, and instructions for making your own custom train departure board. 

Materials required (all links to products are for UK suppliers) :
- Raspberry Pi Pico WH (easier if already soldered hence the WH instead of W)
- USB micro cable that supports both data and power transfer (probably already owned, common with console controllers, external storage etc.)
- PC or Mac to load micropython code and to power the device (power can be supplied by any means once micropython is loaded onto the pico)
- Breadboard to form circuit (highly recommend https://tinyurl.com/4tm4zn82 as it is labelled perfectly for the pico)
- Female to male jumper wires (these work fine https://tinyurl.com/5hcm279r)
- OLED Display Module (the one I used https://tinyurl.com/ys6shs5f , the code should work for any display that uses either the ssd1306 or sh1106 drivers - depending on which driver your display uses and what it's resolution is changed may have to be made on lines 9/10 of the main.py file and to size variables DISPLAY_W and DISPLAY_H)

<img width="1440" height="1126" alt="image" src="https://github.com/user-attachments/assets/80bb9efa-c87f-42db-91ab-f49ac9a91c6e" />

The above image shows the required wiring for the 4 display pins (VCC,GND,SDA and SCL) to the respective headers on the pico. The male end of the jumper cable just needs to sit adjacent to the pin. A portion of my setup (showing the male end of the jumper cables in row 16 and 17) is shown below to make it clearer.

<img width="462" height="661" alt="image" src="https://github.com/user-attachments/assets/1051ee8c-e4b0-478f-aaab-90bfe3e72378" />

To begin programming the pico it needs to have micropython installed. I recommend you watch the first 1 min 23 secs of this video to install thonny and subsequently micropython. https://www.youtube.com/watch?v=_ouzuI_ZPLs

Once thonny is installed, firstly create two new files:
- one should be called ssd1306 and contain the relevant code from this repo for the file
- one should be called sh1106 and also contain the relvant code from this repo for the file

Ensure both of those are saved to the pico and then you can simply create one more file "main.py" and paste the code from the repo into that. 

IMPORTANT CHANGES THAT WILL/MAY NEED TO BE MADE TO THE "main.py" file:
- you WILL need to add the ssid and password details for as many networks as you wish to the main.py file so the api can make calls and fetch live data
- you WILL need to sign up for an account with the Rail Data Marketplace (took me about 24 hours for my application be be reviewed and accepted) and once you have an account subscribe to the Staff Version of the Live Departure Board API where you will be given a unique api key which needs to be entered into the main.py code
- you MAY need to change the DISPLAY_W and DISPLAY_H variables if your resolution is different to mine
- you MAY need to comment out of one the drivers and use the other other if your display uses a different driver to mine

Have fun!

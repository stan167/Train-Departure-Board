# 🚆 Pico Train Departure Board

> A live UK train departure board running on a Raspberry Pi Pico W with an OLED display — fetching real-time data from the National Rail Staff Departure Board API.

---

## 📸 Demo

<!-- Add a photo or GIF of your finished build here -->

---

## 🛒 Materials

> All links are to UK suppliers.

| Component | Notes |
|---|---|
| [Raspberry Pi Pico WH](https://tinyurl.com/4tm4zn82) | WH recommended — comes pre-soldered |
| Micro USB cable | Must support data transfer, not charge-only. Common with console controllers, external hard drives etc. |
| PC or Mac | To load MicroPython and code onto the Pico |
| [Breadboard](https://tinyurl.com/4tm4zn82) | This one is labelled perfectly for the Pico |
| [Female to male jumper wires](https://tinyurl.com/5hcm279r) | Standard set works fine |
| [OLED Display Module](https://tinyurl.com/ys6shs5f) | I used a 1.3" SH1106 128x64. See [display compatibility](#-display-compatibility) below |

---

## 🔌 Wiring

Connect the 4 display pins to the Pico as follows:

| Display Pin | Pico Pin |
|---|---|
| VCC | 3V3 — Pin 36 |
| GND | GND — Pin 38 |
| SDA | GP16 — Pin 21 |
| SCL | GP17 — Pin 22 |

> ⚠️ Check the physical labels on your display — some modules have pins in the order `GND VCC SCL SDA` rather than `VCC GND SDA SCL`.

The male end of the jumper cable simply sits in the breadboard row adjacent to the pin. The image below shows the required wiring:

<img width="1440" alt="Wiring diagram" src="https://github.com/user-attachments/assets/80bb9efa-c87f-42db-91ab-f49ac9a91c6e" />

And here is a portion of my own setup showing the male ends of the jumper cables sitting in rows 16 and 17:

<img width="462" alt="My wiring setup" src="https://github.com/user-attachments/assets/1051ee8c-e4b0-478f-aaab-90bfe3e72378" />

---

## 💾 Installing MicroPython

If you haven't used a Pico before, you'll need to install MicroPython first. The first **1 minute 23 seconds** of [this video](https://www.youtube.com/watch?v=_ouzuI_ZPLs) walks you through installing Thonny and flashing MicroPython onto the Pico.

---

## 🚀 Setup

Once Thonny is installed and MicroPython is on your Pico:

**1.** Create a new file in Thonny, paste in the contents of `sh1106.py` from this repo, and save it to the Pico as `sh1106.py`

**2.** Do the same for `ssd1306.py`

**3.** Create one more file, paste in the contents of `main.py`, make the required changes below, and save it to the Pico as `main.py`

> Files saved to the Pico will persist and run automatically on power-up.

---

## ⚙️ Configuration

Open `main.py` and make the following changes at the top of the file:

### ✅ Required

**WiFi credentials** — add the SSID and password for your network(s):
```python
WIFI_NETWORKS = [
    ("YOUR_SSID",    "YOUR_PASSWORD"),
    ("YOUR_SSID_2",  "YOUR_PASSWORD_2"),  # optional extras
]
```

**API key** — sign up for a free account at [Rail Data Marketplace](https://raildata.org.uk) and subscribe to the **Staff Version of the Live Departure Board API**. Once approved (allow ~24 hours), paste your key in:
```python
API_KEY = "YOUR_API_KEY"
```

**Station** — set your 3-letter CRS station code:
```python
CRS = "PLG"  # e.g. VIC for Victoria, LBG for London Bridge
```

**Timezone** — set to `1` during BST (summer) or `0` during GMT (winter):
```python
UTC_OFFSET = 1
```

### 🔧 May Be Required

**Display resolution** — if your display is a different size to the default 128×64:
```python
DISPLAY_W = 128
DISPLAY_H = 64
```

**Display driver** — if your display uses SSD1306 instead of SH1106, comment out line 9 and uncomment line 10 in `main.py`:
```python
import sh1106   # for SH1106 displays (e.g. most 1.3" OLEDs)
# import ssd1306  # for SSD1306 displays (e.g. most 0.96" OLEDs)
```
And update the initialisation line in `main()` accordingly.

---

## 🖥️ Display Compatibility

The code is designed to work with any monochrome I2C OLED that uses the **SH1106** or **SSD1306** driver. Both driver files are included in this repo.

| Display | Driver | Resolution | Changes needed |
|---|---|---|---|
| 1.3" OLED (this build) | SH1106 | 128×64 | None |
| 0.96" OLED | SSD1306 | 128×64 | Swap driver |
| 0.91" OLED | SSD1306 | 128×32 | Swap driver + `DISPLAY_H = 32` |
| 2.42" OLED | SSD1306 | 128×64 | Swap driver |

---

## 🔋 Powering Without a Computer

Once `main.py` is saved to the Pico it will run automatically on boot — no computer needed. Power options include:

- **USB power bank** — plug straight in via Micro USB. Look for one rated for low-current devices
- **3×AA battery holder with Micro USB** — such as [this one from Pi Hut](https://thepihut.com/products/microusb-battery-holder-3xaa) — plugs directly into the Pico, no soldering required. Use alkaline (non-rechargeable) batteries for best results

---

Have fun! 🎉

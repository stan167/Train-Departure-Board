import network
import urequests
import time
import ntptime
import gc

# ── Display driver ────────────────────────────────────────────────────────────
# Uncomment the driver that matches your display:
import sh1106
# import ssd1306
# ─────────────────────────────────────────────────────────────────────────────

from machine import Pin, I2C

# ── WiFi ──────────────────────────────────────────────────────────────────────
# Add as many networks as you like - they are tried in order
WIFI_NETWORKS = [
    ("YOUR_SSID",       "YOUR_PASSWORD"),
    ("YOUR_SSID_2",     "YOUR_PASSWORD_2"),
]

# ── Station ───────────────────────────────────────────────────────────────────
CRS = "PLG"   # 3-letter CRS code for your station (e.g. "PLG", "VIC", "LBG")

# ── API ───────────────────────────────────────────────────────────────────────
# Get a free API key at https://raildata.org.uk
API_KEY     = "YOUR_API_KEY"
API_BASE    = (
    "https://api1.raildata.org.uk"
    "/1010-live-departure-board---staff-version1_0"
    "/LDBSVWS/api/20220120/GetDepartureBoardByCRS"
)
NUM_ROWS    = 7     # max departures to fetch (1-10)
TIME_WINDOW = 120   # how many minutes ahead to look

# ── Time ──────────────────────────────────────────────────────────────────────
UTC_OFFSET  = 1     # BST (summer) = 1, GMT (winter) = 0
REFRESH_SEC = 30    # how often to re-fetch from the API (seconds)

# ── Hardware ──────────────────────────────────────────────────────────────────
# I2C pins - change these to match your wiring
I2C_BUS     = 0
I2C_SDA     = 16
I2C_SCL     = 17
I2C_FREQ    = 400000

# ── Display dimensions ────────────────────────────────────────────────────────
# Change these if you have a different size display
DISPLAY_W   = 128   # pixels wide
DISPLAY_H   = 64    # pixels tall

# ── Layout (auto-calculated from display size) ────────────────────────────────
CHAR_W      = 8     # MicroPython's built-in font is always 8x8px
CHAR_H      = 8
HEADER_H    = 11    # pixels used by header row + separator
ROW_H       = 18    # pixels per train (info line + destination line)
TRAINS_PER_PAGE = max(1, (DISPLAY_H - HEADER_H) // ROW_H)
# Max chars that fit on one line
LINE_CHARS  = DISPLAY_W // CHAR_W   # e.g. 128/8 = 16

# ── Scroll ────────────────────────────────────────────────────────────────────
PAUSE_AFTER_MS  = 2000  # ms to pause once all names are fully visible
TICKER_SPEED_PX = 1     # pixels per frame
TICKER_FRAME_MS = 40    # ms per frame (~25fps)

# ─────────────────────────────────────────────────────────────────────────────

oled = None

# ── Helpers ───────────────────────────────────────────────────────────────────
def show_message(line1, line2="", line3=""):
    oled.fill(0)
    oled.text(line1[:LINE_CHARS], 0, 0)
    if line2:
        oled.text(line2[:LINE_CHARS], 0, DISPLAY_H // 3)
    if line3:
        oled.text(line3[:LINE_CHARS], 0, (DISPLAY_H // 3) * 2)
    oled.show()

def hhmmss():
    t = time.localtime(time.time() + UTC_OFFSET * 3600)
    return "{:02d}:{:02d}:{:02d}".format(t[3], t[4], t[5])

def local_time_struct():
    return time.localtime(time.time() + UTC_OFFSET * 3600)

def pad_right(s, n):
    s = str(s)
    return s + " " * (n - len(s)) if len(s) < n else s[:n]

def pad_left(s, n):
    s = str(s)
    return " " * (n - len(s)) + s[:n] if len(s) < n else s[:n]

# ── WiFi / NTP ────────────────────────────────────────────────────────────────
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if wlan.isconnected():
        show_message("WiFi OK!")
        time.sleep(1)
        return True
    for ssid, password in WIFI_NETWORKS:
        show_message("Connecting...", ssid)
        wlan.connect(ssid, password)
        t = 15
        while not wlan.isconnected() and t > 0:
            time.sleep(1)
            t -= 1
        if wlan.isconnected():
            show_message("WiFi OK!", ssid)
            time.sleep(1)
            return True
        wlan.disconnect()
        time.sleep(1)
    show_message("WiFi FAILED", "No networks")
    return False

def sync_clock():
    try:
        ntptime.settime()
        show_message("Clock synced!")
        time.sleep(1)
    except:
        show_message("Clock sync fail")
        time.sleep(1)

# ── API ───────────────────────────────────────────────────────────────────────
def get_departures():
    gc.collect()
    t = local_time_struct()
    request_time = "{:04d}{:02d}{:02d}T{:02d}{:02d}{:02d}".format(
        t[0], t[1], t[2], t[3], t[4], t[5])
    url = "{}/{}/{}?numRows={}&timeWindow={}".format(
        API_BASE, CRS, request_time, NUM_ROWS, TIME_WINDOW)
    headers = {
        "x-apikey": API_KEY,
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
    }
    try:
        r = urequests.get(url, headers=headers)
        data = r.json()
        r.close()
        gc.collect()
    except Exception as e:
        gc.collect()
        return [], str(e)

    rows = []
    for train in (data.get("trainServices") or []):
        dest   = (train.get("destination") or [{}])[0].get("locationName", "?")
        std    = train.get("std", "")
        etd    = train.get("etd", "")
        std_hm = std[11:16] if len(std) >= 16 else std[:5]
        etd_hm = etd[11:16] if len(etd) >= 16 else etd[:5]
        delayed = False
        if etd_hm and etd_hm != std_hm:
            try:
                std_mins = int(std_hm[:2]) * 60 + int(std_hm[3:5])
                etd_mins = int(etd_hm[:2]) * 60 + int(etd_hm[3:5])
                if etd_mins - std_mins >= 2:
                    delayed = True
            except:
                pass
        time_str = "{} ({})".format(std_hm, etd_hm) if delayed else std_hm
        plat = str(train.get("platform") or "--")
        rows.append((time_str, dest, plat))

    return rows, None

# ── Display ───────────────────────────────────────────────────────────────────
def draw_frame(page_rows, page, total_pages, offsets):
    oled.fill(0)

    # Header: "CRS HH:MM:SS" left, "1/2" right
    ts     = hhmmss()
    pg_str = "{}/{}".format(page + 1, total_pages)
    oled.text("{} {}".format(CRS, ts), 0, 0)
    oled.text(pg_str, DISPLAY_W - len(pg_str) * CHAR_W, 0)
    oled.hline(0, CHAR_H + 1, DISPLAY_W, 1)

    for i, (time_str, dest, plat) in enumerate(page_rows):
        y_info = HEADER_H + i * ROW_H
        y_tick = y_info + CHAR_H + 1

        # Destination scroll
        dest_w = len(dest) * CHAR_W
        capped = min(offsets[i], dest_w)
        x      = capped - dest_w
        oled.text(dest, x, y_tick)

        # Info row drawn on top to protect from scroll bleed
        oled.fill_rect(0, y_info, DISPLAY_W, CHAR_H, 0)

        # Time: enough chars for "14:35 (14:42)" = 13 chars
        time_chars = LINE_CHARS - 3   # leave 3 chars (24px) for platform
        oled.text(pad_right(time_str, time_chars), 0, y_info)

        # Platform right-aligned
        oled.text(pad_left(plat, 2), DISPLAY_W - 2 * CHAR_W, y_info)

    oled.show()

def display_page(page_rows, page, total_pages):
    n = len(page_rows)

    stop_at = []
    for (_, dest, _) in page_rows:
        dest_w = len(dest) * CHAR_W
        stop_at.append(dest_w)

    offsets     = [0] * n
    scrolling   = True
    pause_start = None

    while True:
        draw_frame(page_rows, page, total_pages, offsets)
        time.sleep_ms(TICKER_FRAME_MS)

        if scrolling:
            for i in range(n):
                if offsets[i] < stop_at[i]:
                    offsets[i] += TICKER_SPEED_PX
            if all(offsets[i] >= stop_at[i] for i in range(n)):
                scrolling   = False
                pause_start = time.ticks_ms()
        else:
            if time.ticks_diff(time.ticks_ms(), pause_start) >= PAUSE_AFTER_MS:
                break

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    global oled
    time.sleep_ms(500)
    i2c = I2C(I2C_BUS, sda=Pin(I2C_SDA), scl=Pin(I2C_SCL), freq=I2C_FREQ)

    # ── Initialise display ────────────────────────────────────────────────────
    # For SH1106 displays (most 1.3" OLEDs):
    oled = sh1106.SH1106_I2C(DISPLAY_W, DISPLAY_H, i2c)
    # For SSD1306 displays (most 0.96" OLEDs), comment above and uncomment:
    # oled = ssd1306.SSD1306_I2C(DISPLAY_W, DISPLAY_H, i2c)
    # ─────────────────────────────────────────────────────────────────────────

    show_message("Train Board", "CRS: " + CRS, "Starting...")
    time.sleep(1)

    if not connect_wifi():
        while True:
            time.sleep(5)

    sync_clock()

    rows       = []
    last_fetch = 0
    page       = 0

    while True:
        now = time.time()

        if now - last_fetch >= REFRESH_SEC or last_fetch == 0:
            show_message("Fetching...", CRS)
            new_rows, err = get_departures()
            if err:
                show_message("API Error", str(err)[:LINE_CHARS])
                time.sleep(15)
                continue
            rows       = new_rows
            last_fetch = time.time()
            page       = 0

        if not rows:
            show_message("No services", CRS, hhmmss())
            time.sleep(REFRESH_SEC)
            last_fetch = 0
            continue

        total_pages = max(1, (len(rows) + TRAINS_PER_PAGE - 1) // TRAINS_PER_PAGE)
        page_rows   = rows[page * TRAINS_PER_PAGE : (page + 1) * TRAINS_PER_PAGE]

        display_page(page_rows, page, total_pages)

        page = (page + 1) % total_pages

main()

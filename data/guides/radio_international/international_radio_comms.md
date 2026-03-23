# International Radio Communications Guide — VaultMind

> **NOTE**: In normal times, amateur radio requires licensing in every country.
> In genuine life-threatening emergencies, international law (ITU Radio
> Regulations Article 4.9) permits any station to transmit on any frequency.

## International HF Band Plan (ITU Regions)

The world is divided into three ITU regions for radio regulation:
- **Region 1**: Europe, Africa, Middle East, northern Asia
- **Region 2**: Americas (North, Central, South)
- **Region 3**: Asia-Pacific, Oceania

### Amateur HF Bands — International Allocation

| Band  | Frequency (MHz)   | Region 1 | Region 2 | Region 3 | Primary Use                    |
|-------|-------------------|----------|----------|----------|--------------------------------|
| 160m  | 1.800 – 2.000     | Yes      | Yes      | Yes      | Local/regional nighttime       |
| 80m   | 3.500 – 3.800     | Yes      | 3.5-4.0  | 3.5-3.9  | Regional night, 50-500km       |
| 40m   | 7.000 – 7.200     | 7.0-7.2  | 7.0-7.3  | 7.0-7.2  | Regional day, worldwide night  |
| 30m   | 10.100 – 10.150   | Yes      | Yes      | Yes      | CW/digital only, worldwide     |
| 20m   | 14.000 – 14.350   | Yes      | Yes      | Yes      | Worldwide daytime              |
| 17m   | 18.068 – 18.168   | Yes      | Yes      | Yes      | Worldwide, less crowded        |
| 15m   | 21.000 – 21.450   | Yes      | Yes      | Yes      | Worldwide daytime, solar-dep.  |
| 12m   | 24.890 – 24.990   | Yes      | Yes      | Yes      | Worldwide, solar cycle peak    |
| 10m   | 28.000 – 29.700   | Yes      | Yes      | Yes      | Worldwide, solar cycle peak    |

### International Emergency and Distress Frequencies

| Frequency     | Mode    | Service                                    |
|---------------|---------|---------------------------------------------|
| 2.182 MHz     | USB     | Maritime HF distress (international)        |
| 5.680 MHz     | USB     | Aviation HF distress                        |
| 7.030 MHz     | CW      | 40m amateur emergency (Morse code)          |
| 14.300 MHz    | USB     | 20m amateur emergency net (IARN)            |
| 18.160 MHz    | USB     | 17m amateur emergency                       |
| 21.360 MHz    | USB     | 15m amateur emergency                       |
| 121.500 MHz   | AM      | Aviation VHF distress (universal)           |
| 156.800 MHz   | FM      | Marine VHF Channel 16 (distress, worldwide) |
| 243.000 MHz   | AM      | Military aviation UHF distress              |
| 406.0 MHz     | Digital | Emergency beacon (COSPAS-SARSAT satellites) |

### International Amateur Emergency Networks

| Network                | Frequency    | Mode | Schedule              |
|------------------------|-------------|------|-----------------------|
| IARN (Intl Amateur)    | 14.300 MHz  | USB  | Continuous monitoring |
| Intl Assistance Net    | 14.303 MHz  | USB  | As needed             |
| Caribbean Emergency    | 7.162 MHz   | LSB  | Hurricane season      |
| SATERN (Salvation Army)| 14.265 MHz  | USB  | Disaster response     |
| Maritime Mobile Net    | 14.300 MHz  | USB  | Daily                 |
| Intercontinental Net   | 14.316 MHz  | USB  | As needed             |
| Pacific Emergency      | 14.325 MHz  | USB  | As needed             |
| Eurasian Net           | 14.290 MHz  | USB  | As needed             |

---

## Propagation by Time of Day (HF)

### Understanding Skywave Propagation

HF radio signals bounce off the ionosphere. Different layers reflect
different frequencies at different times:

| Layer | Altitude  | Active        | Reflects           |
|-------|-----------|---------------|--------------------|
| D     | 60-90 km  | Daytime only  | Absorbs MF/low HF  |
| E     | 90-150 km | Daytime only  | 10m-15m             |
| F1    | 150-250 km| Daytime only  | 15m-20m             |
| F2    | 250-500 km| Day and night | 20m-80m             |

### Best Bands by Time and Distance

| Time       | Short (100-500km) | Medium (500-3000km) | Long (3000km+)      |
|------------|-------------------|---------------------|---------------------|
| Sunrise    | 40m, 80m          | 40m, 20m            | 20m                 |
| Midday     | 20m, 15m          | 20m, 15m            | 20m, 15m, 10m       |
| Sunset     | 40m, 20m          | 20m, 40m            | 20m                 |
| Night      | 80m, 160m         | 40m, 80m            | 40m, 30m, 20m       |

### Solar Cycle Effects

- **Solar maximum** (11-year cycle): Higher bands (10m, 12m, 15m) open for worldwide communication
- **Solar minimum**: Higher bands mostly dead; 20m and 40m are the workhorses
- **Solar flares**: Can cause total HF blackout for hours to days
- **Geomagnetic storms**: Disrupt polar paths; equatorial paths less affected

---

## International Phonetic Alphabet (NATO)

Required for clear voice communication across language barriers:

| Letter | Word     | Letter | Word     |
|--------|----------|--------|----------|
| A      | Alpha    | N      | November |
| B      | Bravo    | O      | Oscar    |
| C      | Charlie  | P      | Papa     |
| D      | Delta    | Q      | Quebec   |
| E      | Echo     | R      | Romeo    |
| F      | Foxtrot  | S      | Sierra   |
| G      | Golf     | T      | Tango    |
| H      | Hotel    | U      | Uniform  |
| I      | India    | V      | Victor   |
| J      | Juliet   | W      | Whiskey  |
| K      | Kilo     | X      | X-ray    |
| L      | Lima     | Y      | Yankee   |
| M      | Mike     | Z      | Zulu     |

### International Q-Codes (Used Worldwide)

| Code | Meaning (Question)            | Meaning (Statement)             |
|------|-------------------------------|---------------------------------|
| QTH  | What is your location?        | My location is...               |
| QSL  | Can you confirm receipt?      | I confirm receipt               |
| QRZ  | Who is calling me?            | You are being called by...      |
| QSY  | Shall I change frequency?     | Change frequency to...          |
| QRM  | Is there interference?        | There is interference           |
| QRN  | Are you troubled by static?   | I am troubled by static         |
| QRO  | Shall I increase power?       | Increase power                  |
| QRP  | Shall I decrease power?       | Decrease power (also: low power operation) |
| QRT  | Shall I stop transmitting?    | I am stopping transmission      |

---

## Regional Frequency Guides

### Europe (CEPT/IARU Region 1)
- **PMR446**: 446.0-446.2 MHz, license-free, 0.5W max, 16 channels
- **CB Radio**: 26.965-27.405 MHz, 40 channels, 4W AM / 12W SSB
- **Marine VHF**: Ch 16 (156.800 MHz) distress, Ch 6 intership safety
- **DAB Emergency**: Some countries use DAB for emergency broadcasts

### Americas (FCC/IARU Region 2)
- **FRS**: 462/467 MHz, license-free, 2W, 22 channels
- **GMRS**: 462/467 MHz, licensed, up to 50W, repeater capable
- **MURS**: 151-154 MHz, license-free, 2W, 5 channels
- **CB Radio**: 26.965-27.405 MHz, 40 channels, 4W AM / 12W SSB
- **Marine VHF**: Same as international

### Asia-Pacific (IARU Region 3)
- Varies significantly by country
- **Japan**: 144-146 MHz and 430-440 MHz amateur, very active
- **Australia**: UHF CB on 476-477 MHz (80 channels), very popular
- **India**: Amateur licensing through WPC, 144/430 MHz allocations

---

## Setting Up an International HF Station

### Minimum Equipment
1. **Transceiver**: HF radio covering 1.8-30 MHz (e.g., Yaesu FT-891, Xiegu G90)
2. **Antenna**: Multi-band dipole or long wire with antenna tuner
3. **Power supply**: 12V 20A (from solar/battery system)
4. **Antenna tuner**: Manual or automatic (matches antenna to radio)
5. **Clock**: UTC time is standard for all international radio schedules

### Antenna for International Communication
- **Multi-band dipole**: Fan dipole or trapped dipole for 20m/40m/80m
- **End-fed half-wave**: 20m EFHW (10m wire + 9:1 unun) works on 20m/10m
- **Long wire**: 40m+ of wire with antenna tuner = covers all HF bands
- **Height matters**: Get the antenna as high as possible (10m+ above ground)

### Power Consumption
| Radio                | TX Power | Current Draw (TX) | Current Draw (RX) |
|----------------------|----------|-------------------|--------------------|
| QRP (5W)             | 5W       | 2-3A @ 12V        | 0.3-0.5A           |
| Mid-power (50W)      | 50W      | 10-12A @ 12V      | 0.5-1A             |
| Full power (100W)    | 100W     | 20-22A @ 12V      | 0.5-1A             |

For solar-powered stations, **QRP (5W) is recommended**: draws only 25-35W
during transmit, easily sustained by a 100W solar panel.

---

## Digital Modes (Low Power, High Reliability)

### JS8Call (Best for Off-Grid Messaging)
- Based on FT8 protocol but allows free-form text messaging
- Works at signal levels far below voice capability (-24 dB SNR)
- Store-and-forward messaging via relay stations
- Runs on any computer + HF radio
- Perfect for VaultMind: automated message relay via serial connection

### VARA HF (Winlink Email)
- Send and receive email over HF radio
- Winlink network provides global email access via radio
- Works with 5W and a simple wire antenna
- Critical for international coordination post-disaster

### FT8 / FT4 (Signal Reports)
- Ultra-weak signal mode, works at -20 dB SNR
- Primarily for signal reports (not messaging)
- Useful for testing propagation paths before voice attempts

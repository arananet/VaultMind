# Communications Guide — VaultMind

> **NOTE**: In normal times, amateur radio requires a license.
> In a true emergency (life/property at risk), anyone may transmit
> on any frequency (FCC Part 97.405 / ITU Article 4.9).

## HAM Radio Basics

### Frequency Bands (Most Useful for Survival)

| Band     | Frequency      | Range           | Use Case                          |
|----------|----------------|-----------------|-----------------------------------|
| 2m VHF   | 144-148 MHz    | 5-50 km         | Local communication, repeaters    |
| 70cm UHF | 420-450 MHz    | 1-30 km         | Building penetration, local       |
| 40m HF   | 7.0-7.3 MHz    | 100-3000 km     | Regional daytime communication    |
| 20m HF   | 14.0-14.35 MHz | 500-10,000+ km  | Worldwide daytime communication   |
| 80m HF   | 3.5-4.0 MHz    | 50-500 km       | Regional nighttime communication  |

### Emergency Frequencies
- **146.520 MHz** — 2m FM national calling frequency
- **446.000 MHz** — 70cm FM national calling frequency
- **7.030 MHz** — 40m CW (Morse code) emergency
- **14.300 MHz** — 20m SSB emergency net
- **121.500 MHz** — Aviation distress (air band)
- **156.800 MHz** — Marine Channel 16 (distress)
- **FRS/GMRS Ch 1** — 462.5625 MHz (family radio)

### Baofeng UV-5R (Most Common Survival Radio)
- Dual band: VHF (136-174 MHz) + UHF (400-520 MHz)
- 5W output power
- Range: 3-10 km depending on terrain
- Program frequencies with CHIRP software before grid-down
- **Battery**: 1800mAh, charges via USB or 12V adapter
- Extend range: external antenna on rooftop, elevated position

---

## Antenna Building

### Half-Wave Dipole (Simplest Effective Antenna)
1. **Calculate length**: Total length (meters) = 143 / frequency (MHz)
   - Example: 7.1 MHz (40m band) = 143/7.1 = 20.1 meters total
2. Cut two pieces of wire, each half the total length (10.05m each)
3. Connect each wire to one terminal of coaxial cable (center + shield)
4. Hang in an inverted-V shape from a center support
5. Ends should be at least 3m above ground
6. Feed coax to radio

### Ground Plane Antenna (VHF/UHF Vertical)
1. **Element length**: Quarter wave = 71.5 / frequency (MHz) in meters
   - For 146 MHz: 71.5/146 = 0.49m (49cm)
2. Cut one vertical element (radiator)
3. Cut 4 radial elements (ground plane), same length
4. Mount vertical element on SO-239 connector center pin
5. Attach radials to connector ground, bent 45° downward
6. Mount as high as possible

### Improvised Antennas
- **Long wire**: Any wire 10m+ strung as high as possible works as an antenna
- **Vehicle antenna**: Car whip antenna = reasonable 2m/70cm antenna
- **Rain gutter**: Metal gutters can work as HF antennas in emergency
- Key principle: **height is gain** — every doubling of height ≈ 6dB improvement

---

## Morse Code (CW)

### Why Morse Still Matters
- Works at signal levels where voice is unreadable
- Simple equipment: a key, a battery, and a wire
- Requires 10x less power than voice for same range
- CW gets through when everything else fails

### Essential Characters
```
A  .-      N  -.      0  -----
B  -...    O  ---     1  .----
C  -.-.    P  .--.    2  ..---
D  -..     Q  --.-    3  ...--
E  .       R  .-.     4  ....-
F  ..-.    S  ...     5  .....
G  --.     T  -       6  -....
H  ....    U  ..-     7  --...
I  ..      V  ...-    8  ---..
J  .---    W  .--     9  ----.
K  -.-     X  -..-
L  .-..    Y  -.--
M  --      Z  --..
```

### Distress Signals
- **SOS**: `... --- ...` (sent as one continuous sequence)
- **MAYDAY**: Voice equivalent of SOS (say three times)
- **PAN-PAN**: Urgent situation but no immediate danger

---

## Meshtastic (LoRa Mesh Networking)

### What Is It
- Open-source mesh network using LoRa radio
- Text messaging without any infrastructure
- Range: 1-10 km per node; mesh extends range
- Runs on cheap hardware (~$20-30 per node)

### Recommended Hardware
| Device     | Battery | GPS | Price  | Notes                     |
|------------|---------|-----|--------|---------------------------|
| Heltec V3  | No*     | No  | ~$18   | Cheapest; needs ext battery|
| T-Beam     | Yes     | Yes | ~$30   | Best all-round             |
| RAK 4631   | No*     | Optional | ~$25 | Most modular              |

*Can be powered by USB power bank

### Setup
1. Flash Meshtastic firmware (via USB from computer)
2. Configure via Meshtastic app (phone) or CLI
3. Set region (US, EU, etc.) for correct frequency
4. Set channel name and encryption key (PSK)
5. All nodes on same channel + key can communicate
6. Messages relay through intermediate nodes automatically

### Integration with VaultMind
- VaultMind connects to Meshtastic node via serial USB
- Incoming messages can trigger vault queries
- Query results can be relayed back over mesh
- Use case: field team queries vault at base camp via radio

---

## Signal Propagation

### VHF/UHF (Line of Sight)
- Signal travels in straight lines
- Blocked by hills, buildings, dense forest
- **Rule of thumb** (distance in km):
  `Range = 4.12 × (√h1 + √h2)` where h = antenna height in meters
- Example: Both antennas at 10m: 4.12 × (3.16 + 3.16) = 26 km

### HF (Skywave)
- HF signals bounce off the ionosphere
- Enables long-distance communication (100-10,000+ km)
- Varies by time of day, season, and solar activity
- **Day**: Higher bands work better (20m, 15m, 10m)
- **Night**: Lower bands work better (40m, 80m, 160m)
- Dead zone: Too far for ground wave, too close for skywave (50-200 km)

### Improving Your Signal
1. **Antenna height**: Most important factor
2. **Antenna orientation**: Match polarization (vertical for mobile, horizontal for HF)
3. **Ground system**: Radials improve efficiency
4. **Reduce interference**: Keep antennas away from electronics, solar controllers
5. **Power management**: 5W into a good antenna beats 50W into a poor one

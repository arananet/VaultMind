# Physical Placement & Storage Guide — VaultMind Hardware

> This guide covers where and how to physically store VaultMind hardware
> for maximum survivability, security, and longevity.

## Site Selection Criteria

### Priority Factors (Ranked)

1. **Physical security**: Protected from theft, tampering, unauthorized access
2. **Environmental protection**: Temperature, humidity, water, dust, EMP
3. **Power access**: Proximity to solar panels, battery bank, generator
4. **Ventilation**: Electronics need airflow; enclosed spaces trap heat
5. **Accessibility**: Operators must be able to reach it for maintenance
6. **Concealment**: Not visible from outside; no light/noise leakage

---

## Recommended Locations

### Tier 1: Purpose-Built Server Room (Best)
- **Interior room** with no exterior walls or windows
- Concrete or masonry walls (natural EMI shielding)
- Elevated above ground floor (flood protection)
- Dedicated 12V DC power run from battery bank
- Ventilation: small DC fan exhausting to interior hallway
- Lock: mechanical deadbolt (electronic locks fail without power)
- Backup: fireproof safe or vault within the room

### Tier 2: Basement/Cellar Installation
- Naturally cool (temperature stability helps electronics)
- Protected from weather, wind, and most debris
- **Risks**: Flooding, humidity, radon
- **Mitigations**:
  - Elevate equipment 30cm+ off floor on shelving
  - Use dehumidifier (or silica gel in sealed enclosure)
  - Seal enclosure against moisture
  - Ensure at least one escape route / alternative exit

### Tier 3: Fortified Closet/Cabinet
- Interior closet on upper floor
- Line with reflective insulation (Faraday + thermal)
- Small exhaust fan through wall to adjacent room
- Equipment mounted on wall rack, not floor
- Cover with a bookshelf or false wall for concealment

### Tier 4: Underground Cache (Emergency Backup)
- Pelican case or ammo can, sealed and buried
- Depth: 30-60cm, above water table
- Include desiccant packs and humidity indicator
- GPS coordinates or map reference to locate
- Contains cold backup drive + spare Raspberry Pi
- **Risk**: Ground moisture, forgetting location
- **Mitigation**: Multiple landmarks, written + memorized coordinates

---

## Environmental Controls

### Temperature
- **Optimal**: 15-25°C (59-77°F)
- **Maximum**: 35°C sustained (components derate above this)
- **Minimum**: 5°C (batteries lose capacity below freezing)
- **Solution**: Use CPU temperature monitoring (VaultMind monitor service)
  to trigger ventilation fan via GPIO automation

### Humidity
- **Optimal**: 30-50% relative humidity
- **Too high (>60%)**: Corrosion, condensation on electronics
- **Too low (<20%)**: Static electricity buildup
- **Solutions**:
  - Sealed enclosure with silica gel for dry storage
  - Ventilated enclosure with humidity sensor for active operation

### Vibration & Shock
- Mount SSDs, not HDDs (SSDs have no moving parts)
- Use foam padding in Pelican cases for mobile nodes
- Wall-mount equipment to isolate from floor vibration

---

## EMP Protection

### Faraday Cage Construction
1. Use a metal enclosure (ammo can, metal trash can, or galvanized bucket)
2. Line interior completely with cardboard or foam (equipment must NOT touch metal)
3. Seal all seams with conductive tape (aluminum HVAC tape)
4. Ground the enclosure to earth ground (copper rod)
5. All cables entering must pass through ferrite chokes

### Practical EMP Strategy
- **Primary node**: Operating in a naturally shielded location (concrete basement)
- **Backup node**: Stored in a sealed Faraday container, powered off
- **Spare components**: Charge controller, USB drives, radio — all in Faraday storage
- **Solar panels**: Cannot be EMP-shielded while in use; keep spares

---

## Concealment (OPSEC)

### Visual
- No external indicators (antennas should appear as clotheslines or fence wire)
- No visible cabling running to solar panels (route under siding/eaves)
- Server room door should appear as normal closet/utility door

### Audible
- Fan noise is minimal but detectable at night; use quiet 80mm fans
- Place equipment away from exterior walls
- Consider sound insulation (foam panels) if operational security is critical

### Thermal
- Electronics produce heat detectable by thermal imaging
- Vent exhaust air into building interior, not directly outside
- Mix exhaust with household heating/cooling if possible

### Electromagnetic
- WiFi signals are detectable; use lowest necessary TX power
- Consider wired Ethernet to client devices when possible
- LoRa radio emissions are low-power and difficult to direction-find

---

## Mobile Node ("The Satchel") Placement

### While Traveling
- Inside a backpack with foam padding
- Power bank and Pi in separate compartments (thermal isolation)
- Antenna: flexible whip in external pocket or lashed to pack frame
- Rain protection: ziplock bag over electronics, not sealed (ventilation)

### At a Temporary Site
- Elevate antenna (hang in a tree, lean against building)
- Place equipment in shade (direct sun overheats quickly)
- Connect external battery / solar panel for extended operation
- Position for both radio line-of-sight and physical concealment

---

## Maintenance Schedule

| Task                          | Frequency  | Notes                              |
|-------------------------------|------------|-------------------------------------|
| Check disk health (SMART)     | Weekly     | `vaultmind diagnostics`            |
| Clean dust from vents/fans    | Monthly    | Compressed air or soft brush        |
| Verify backup integrity       | Monthly    | `zfs scrub` or checksum verify     |
| Test UPS switchover           | Quarterly  | Disconnect primary, verify switch   |
| Rotate cold backup drive      | Monthly    | `zfs send` to USB HDD             |
| Inspect solar panel + cables  | Monthly    | Look for damage, clean panel        |
| Test Meshtastic radio link    | Weekly     | Ping test to any visible node       |
| Check battery voltage/health  | Weekly     | Should hold >12.8V (LiFePO4)      |
| Full system restore test      | Yearly     | Boot from backup, verify all data   |

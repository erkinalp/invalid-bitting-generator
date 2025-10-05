Terminally invalid key bittings: research, analysis, and generator

What’s new
- Added modeling for manufacturer constraints beyond MACS:
  - No-cut/forbidden stations
  - Station-specific depth ceilings
  - Stop type (shoulder vs tip) and minimum first station
- Added presets for pin tumbler locks: US, Euro, Kwikset SmartKey 6-key used in 5-pin plug, Schlage Everest full-size, Schlage Everest 29 SL tip-read, BEST A2 tip, Yale KeyMark conventional, Yale IC A2 tip, ASSA ABLOY Yale conventional
- Added presets for warded locks: binary (2-depth), multiward-4 (4-depth), multiward-8 (8-depth)
- Added presets for disc tumbler locks: Abloy Classic (6-disc and 10-disc), Abloy Protec2 (6-disc and 10-disc)
- Added presets for tubular locks: 7-pin, 8-pin, and 10-pin variants
- Added presets for wafer tumbler locks: 5-wafer shallow/deep, 6-wafer automotive, 10-wafer double-sided
- Added CLI: check, repair, list-terminal, enumerate, presets

Key findings with citations
- Kwikset SmartKey forbidden station for 5‑pin plug when gauging a 6‑pin key: “0-position on the key is not used… do not gauge the 0-position.”
  - /home/ubuntu/research/locks/kwikset_rekey_manual.txt lines 639-646
- Schlage Everest full-size OEM data: MACS=7; Increment=0.15"; Spacing tolerance ±0.001"; Depth tolerance +.002/−0.
  - /home/ubuntu/research/locks/schlage_everest_fullsize_manual.txt lines 909-931
- Schlage Everest cutting guidance: first-cut positioning can be mis-set if carriage travel is restricted by bow geometry; confirms setup/stop constraints matter.
  - /home/ubuntu/research/locks/schlage_everest_fullsize_manual.txt lines 1403-1409
- Schlage catalog: shoulder stop is the datum while bittings are read tip-to-bow for certain families; establishes stop rule governing first-station permissibility.
  - /home/ubuntu/research/locks/schlage_catalog.txt lines 1636-1643
- Yale KeyMark Service Manual: A2 pinning with MACS: 9, Increment: .0125", Depth Tol ±0.0015", Spacing Tol ±0.0010", and “SPACING FROM THE SHOULDER” indicating shoulder-stop stationing.
  - URL: https://www.sopl.us/uploads/1/3/0/1/1301029/yale_keymark_service_manual.pdf
  - Extracted: /home/ubuntu/research/locks/yale_keymark_manual.txt lines 456-463, 489-491
- ASSA ABLOY Yale Cylinders & Keys Catalog: SFIC “keys are cut from tip to bow” and section/read conventions; supports tip-read preset and general Yale conventions.
  - URL: https://www.assaabloy.com/hk/en/product-assets/cylinder/yale4/assets/documents/Yale_Cylinders_and_Keys_Catalog.pdf
  - Extracted: /home/ubuntu/research/locks/yale_cylinders_keys_catalog.txt lines 1258-1259, 1328-1329

- best_a2_tip: BEST A2, tip-stop preset (A2 increment context), with a conservative minimum first station from tip

- Schlage Everest 29 SL: read standard cuts with key gauge starting at the tip; SFIC A2 uses 0.0125" increment (context for increments/standards).
  - /home/ubuntu/research/locks/schlage_everest29_sl_manual.txt lines 2514-2517 and 2123-2128

Why terminal invalidity exists
- MACS + global depth range alone is monotone under deepening; any sequence within max depth can be deepened to satisfy MACS.
- Terminal invalidity arises when constraints are not monotone under deepening:
  - A cut at a forbidden/no‑cut station cannot be removed by deepening.
  - A cut before the minimum allowed first station for the stop type cannot be moved by deepening.
  - A station-specific ceiling lower than global max makes any deeper cut at that station unfixable by deepening.

Model
- KeySystem fields now include:
  - stop_type: shoulder or tip
  - min_first_station_index: earliest allowed station index for a cut
  - no_cut_mask: per-station boolean disallow
  - station_max_ceiling: per-station maximum depths
  - max_consecutive_repeats: maximum allowed consecutive identical cuts
- Validation checks these before and after MACS repair. Repair is linear-time propagation; no recursion.

Presets

Pin Tumbler Locks
- us: generic 5-pin, depths 1..7, MACS 2
- euro: generic 5-pin, depths 1..10, MACS 2
- kwikset_6in5: 6-pin key used in 5-pin plug; station 0 is no-cut
- schlage_everest_full: MACS 7, shoulder stop
- schlage_everest29_sl_tip: MACS 7, tip-read; min_first_station_index defaults to 1 to demonstrate tip-stop constraints
- best_a2_tip: BEST A2, tip-stop; conservative min-first-station from tip
- yale_keymark: Yale KeyMark conventional, shoulder stop; stationing by shoulder datum
- yale_ic_a2_tip: Yale SFIC A2-style tip-read; min_first_stn=1
- assa_abloy_yale: Yale conventional under ASSA ABLOY catalog; shoulder stop

Warded Locks
- warded_binary: 4-position binary warded lock, depths 0..1 (cut/no-cut), MACS 1
  - Simple ward configurations with binary notch patterns
  - Historical design, used in low-security applications
- warded_multiward_4: 6-position multiward lock, depths 0..3, MACS 3
  - Multiple ward depths for increased complexity
  - Intermediate security warded lock configuration
- warded_multiward_8: 6-position multiward lock, depths 0..7, MACS 7
  - Complex ward patterns with 8 depth variations
  - Maximum complexity for warded lock designs

Disc Tumbler Locks (Abloy)
- disc_abloy_classic_6: 6-disc Abloy Classic, depths 0..5 (6 positions), MACS 5
  - Original Abloy design with rotating discs at 18° increments (0° to 90°)
  - Semi-cylindrical key with angled notches
  - Constraint: No more than 3 consecutive positions can have the same cut
  - Reference: https://www.lockwiki.com/index.php/Abloy_Classic
- disc_abloy_classic_10: 10-disc Abloy Classic, depths 0..5 (6 positions), MACS 5
  - Extended disc count for higher security (5-11 discs possible)
  - Uses same 6 angular positions as 6-disc variant
- disc_abloy_protec2_6: 6-disc Abloy Protec2, depths 0..9, MACS 8
  - Modern high-security disc detainer design
  - Improved false gate protection
- disc_abloy_protec2_10: 10-disc Abloy Protec2, depths 0..11, MACS 10
  - Maximum security disc tumbler configuration
  - Extended depth range and disc count

Tubular Pin Tumbler Locks
- tubular_7pin: 7-pin tubular lock, depths 0..9, MACS 8
  - Circular pin arrangement (common in vending machines)
  - Also known as Ace lock or circle pin tumbler
  - Reference: https://en.wikipedia.org/wiki/Tubular_pin_tumbler_lock
- tubular_8pin: 8-pin tubular lock, depths 0..9, MACS 8
  - Standard tubular configuration for bike locks
  - Used in Kryptonite locks and computer security cables
- tubular_10pin: 10-pin tubular lock, depths 0..9, MACS 8
  - Extended pin count for increased security
  - Rare variant for high-security applications

Wafer Tumbler Locks
- wafer_5wafer_shallow: 5-wafer lock, depths 0..4, MACS 3
  - Common desk drawer and cabinet lock
  - Shallow depth range for simple applications
  - Reference: https://en.wikipedia.org/wiki/Wafer_tumbler_lock
- wafer_5wafer_deep: 5-wafer lock, depths 0..7, MACS 6
  - Deeper cuts for increased security
  - Used in better quality furniture locks
- wafer_6wafer_auto: 6-wafer automotive lock, depths 0..5, MACS 4
  - Typical automotive wafer configuration
  - Historical use in vehicle ignitions and doors (pre-1960s to 1980s)
- wafer_10wafer_double: 10-wafer double-sided lock, depths 0..9, MACS 8
  - Advanced wafer configuration with opposed wafer sets
  - Double-bitted key for higher security applications

CLI
- Show presets:
  python3 tool.py presets
- Check:
  python3 tool.py check --preset kwikset_6in5 --seq 2,1,1,1,1,1
- Repair:
  python3 tool.py repair --preset us --pins 5 --seq 1,7,1,1,1
- Generate terminal examples:
  python3 tool.py list-terminal --preset schlage_everest29_sl_tip --limit 5
- BEST A2 tip-stop check:
  python3 tool.py check --preset best_a2_tip --seq 2,1,1,1,1,1,1
- Yale IC A2 tip-stop check:
  python3 tool.py check --preset yale_ic_a2_tip --seq 2,1,1,1,1,1,1
- Yale KeyMark terminal examples:
  python3 tool.py list-terminal --preset yale_keymark --limit 5
- ASSA ABLOY Yale terminal examples:
  python3 tool.py list-terminal --preset assa_abloy_yale --limit 5
- Warded lock examples:
  python3 tool.py check --preset warded_binary --seq 1,0,1,0
  python3 tool.py list-terminal --preset warded_multiward_8 --limit 5
- Disc tumbler lock examples:
  python3 tool.py check --preset disc_abloy_classic_6 --seq 0,5,0,3,2,1
  python3 tool.py check --preset disc_abloy_classic_6 --seq 0,0,0,0,1,2
  python3 tool.py list-terminal --preset disc_abloy_protec2_10 --limit 5
- Tubular lock examples:
  python3 tool.py check --preset tubular_7pin --seq 0,9,0,5,3,2,1
  python3 tool.py list-terminal --preset tubular_8pin --limit 5
- Wafer tumbler lock examples:
  python3 tool.py check --preset wafer_5wafer_shallow --seq 0,4,0,2,1
  python3 tool.py list-terminal --preset wafer_6wafer_auto --limit 5
- Enumerate small spaces:
  python3 tool.py enumerate --preset euro --pins 4 --max-repeat 4

Examples
- Kwikset 6→5 case:
  - Input: 2,1,1,1,1,1
  - Check: terminal=True reason=forbidden/no-cut station cut present
- Shoulder stop first-station restriction (if min_first_station_index=1):
  - Input: 2,1,1,1,1,1
  - Check: terminal=True reason=first station not allowed for this stop type
- Station ceiling example (configure --ceilings None,4,None,None,None,None and put 5 at pos 1):
  - Input: 1,5,1,1,1,1
  - Check: terminal=True reason=station-specific ceiling violated
- Abloy Classic consecutive repeat constraint (max_consecutive_repeats=3):
  - Input: 0,0,0,0,1,2 (4 consecutive 0s)
  - Check: terminal=True reason=too many consecutive repeats of same cut
  - Input: 0,0,0,1,2,3 (exactly 3 consecutive 0s)
  - Check: terminal=False reason=repairable to a valid bitting by deepening

Run locally
- cd /home/ubuntu/work/key_bittings
- python3 tool.py presets
- Use the commands above to verify terminal invalidity under manufacturer constraints.

Notes
- Euro EN 1303/18252 public summaries are performance-classification oriented and do not include cutting geometry; OEM documents govern practical station/stop constraints.
- The model accepts future numeric station ceilings when OEM tables are found; examples here are illustrative but the Kwikset no‑cut and Schlage stop rules are directly cited.
- Abloy Classic enforces a max_consecutive_repeats=3 constraint, meaning no more than 3 consecutive positions can have the same cut. This creates many terminally invalid sequences that cannot be fixed by deepening.
- Lock types beyond pin tumblers (warded, tubular, wafer) use theoretical models based on general principles where formal specifications are unavailable.

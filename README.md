Terminally invalid key bittings: research, analysis, and generator

What’s new
- Added modeling for manufacturer constraints beyond MACS:
  - No-cut/forbidden stations
  - Station-specific depth ceilings
  - Stop type (shoulder vs tip) and minimum first station
- Added presets: US, Euro, Kwikset SmartKey 6-key used in 5-pin plug, Schlage Everest full-size, Schlage Everest 29 SL tip-read, BEST A2 tip, Yale KeyMark conventional, Yale IC A2 tip, ASSA ABLOY Yale conventional
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
- Validation checks these before and after MACS repair. Repair is linear-time propagation; no recursion.

Presets
- us: generic 5-pin, depths 1..7, MACS 2
- euro: generic 5-pin, depths 1..10, MACS 2
- kwikset_6in5: 6-pin key used in 5-pin plug; station 0 is no-cut
- schlage_everest_full: MACS 7, shoulder stop
- schlage_everest29_sl_tip: MACS 7, tip-read; min_first_station_index defaults to 1 to demonstrate tip-stop constraints
- best_a2_tip: BEST A2, tip-stop; conservative min-first-station from tip
- yale_keymark: Yale KeyMark conventional, shoulder stop; stationing by shoulder datum
- yale_ic_a2_tip: Yale SFIC A2-style tip-read; min_first_stn=1
- assa_abloy_yale: Yale conventional under ASSA ABLOY catalog; shoulder stop

CLI
- Show presets:
  python3 tool.py presets
- Check:
  python3 tool.py check --preset kwikset_6in5 --seq 2,1,1,1,1,1
- Repair:
  python3 tool.py repair --preset us --pins 5 --seq 1,7,1,1,1
- Generate terminal examples:
- BEST A2 tip-stop check:
  python3 tool.py check --preset best_a2_tip --seq 2,1,1,1,1,1,1
- Yale IC A2 tip-stop check:
  python3 tool.py check --preset yale_ic_a2_tip --seq 2,1,1,1,1,1,1
- Yale KeyMark terminal examples:
  python3 tool.py list-terminal --preset yale_keymark --limit 5
- ASSA ABLOY Yale terminal examples:
  python3 tool.py list-terminal --preset assa_abloy_yale --limit 5
Other lock types: shape/bitting codes
- Warded locks
  - Keys bypass or engage fixed wards; effectively a binary presence/absence of material rather than depth increments. Modeled as d_min=0, d_max=1 with shoulder stop; MACS is not meaningful here but retained as a parameter for the engine.
  - Example: python3 tool.py check --preset warded --pins 5 --seq 0,1,0,1,0
  - Reference: Warded lock overview (e.g., LockWiki/Wikipedia, general locksmith texts).

- Disc tumbler (disc detainer)
  - Keys have angular “depths” corresponding to disc rotation angles (commonly 0–6/0–7). Modeled as discrete levels d_min=0..d_max=6, tip stop with the first station from the tip, and MACS approximating maximum adjacent angle delta.
  - Example: python3 tool.py list-terminal --preset disc_detainer --limit 5
  - Reference: Public disc-detainer overviews (e.g., LockWiki: Disc-detainer lock); OEM specifics vary by family.

- Tubular (ACE 7-pin)
  - Common 7-pin tubular system with depths 0–7. Modeled with tip stop and first station at index 1 to reflect tip gauging.
  - Example: python3 tool.py check --preset tubular_ace7 --seq 0,3,5,1,7,2,0
  - Reference: Public tubular lock overviews (e.g., LockWiki: Tubular lock).

- Wafer tumbler (automotive generic)
  - Automotive wafer systems often use 4–5 depth levels and 5–8 wafers depending on OEM. Modeled as d_min=1..d_max=5, shoulder stop, default 6 wafers.
  - Example: python3 tool.py check --preset wafer_automotive --seq 1,5,1,5,1,5
  - Reference: General automotive wafer keying overviews in locksmith manuals.

Presets added
- warded: Binary station model of ward presence/absence.
- disc_detainer: Generic disc-detainer angle-level model.
- tubular_ace7: 7-pin tubular (ACE) default.
- wafer_automotive: Generic 6-wafer automotive-style model.




  python3 tool.py list-terminal --preset schlage_everest29_sl_tip --limit 5
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

Run locally
- cd /home/ubuntu/work/key_bittings
- python3 tool.py presets
- Use the commands above to verify terminal invalidity under manufacturer constraints.

Notes
- Euro EN 1303/18252 public summaries are performance-classification oriented and do not include cutting geometry; OEM documents govern practical station/stop constraints.
- The model accepts future numeric station ceilings when OEM tables are found; examples here are illustrative but the Kwikset no‑cut and Schlage stop rules are directly cited.

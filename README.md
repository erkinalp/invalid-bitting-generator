Terminally invalid key bittings: research, analysis, and generator

What’s new
- Added modeling for manufacturer constraints beyond MACS:
  - No-cut/forbidden stations
  - Station-specific depth ceilings
  - Stop type (shoulder vs tip) and minimum first station
- Added presets for pin tumbler locks: US, Euro, Kwikset SmartKey 6-key used in 5-pin plug, Schlage Everest full-size, Schlage Everest 29 SL tip-read, BEST A2 tip, Yale KeyMark conventional, Yale IC A2 tip, ASSA ABLOY Yale conventional
- Expanded warded lock presets with 7 families: binary, multiward (4/8-depth), lever (4/6-ward), skeleton key, padlock variants
- Expanded disc tumbler lock presets with 11 families: Abloy Classic, Protec2, Disklock, Exec, Profile, Protec (various disc counts)
- Expanded tubular lock presets with 7 families: 4-pin through 10-pin, Chicago 7-pin, Ace 8-pin variants
- Expanded wafer tumbler lock presets with 12 families: shallow/deep, automotive (GM/Ford/Chrysler), desk drawer, cabinet, mailbox
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

Theoretical Foundation
The tool now supports two equivalent implementations for detecting terminally invalid bittings:

1. Iterative constraint propagation (default): Forward and backward passes that propagate MACS constraints until convergence. O(n²) time complexity in worst case.

2. Difference constraints solver (--use-bellman-ford): Based on the theory that terminal invalidity is equivalent to membership in the complement of the upward-closure of valid bittings. This formulation models the problem as a difference constraint system where:
   - Variables y[i] represent (possibly deepened) depths at each station
   - Constraints include: y[i] >= x[i] (deepening only), y[i] <= ceiling[i] (bounds), |y[i+1] - y[i]| <= MACS (adjacency)
   - The system is solved using constraint propagation inspired by Bellman-Ford shortest paths algorithm
   - A bitting is terminally invalid if and only if no solution exists (negative cycle analog)

Key insight: Deepening-only repair is a constraint satisfaction problem. MACS + global bounds alone is monotone under deepening (always repairable), but additional constraints like forbidden stations, station-specific ceilings, and first-station rules break monotonicity and create terminal invalidity.

References:
- Difference constraints: Cormen et al., Introduction to Algorithms, Chapter 24.4
- Upward-closure interpretation: Order theory, upper sets (Wikipedia: https://en.wikipedia.org/wiki/Upper_set)
- MACS specification: Allegion Knowledge Base (https://kc.allegion.com/kb/article/what-is-the-maximum-adjacent-cut-specification-or-macs/)

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

Warded Locks (Realistic Variants with Terminal Invalidity)
- warded_multiward_4: 6-position multiward lock, depths 0..3, MACS 3
  - Multiple ward depths for increased complexity
  - Intermediate security warded lock configuration
- warded_multiward_8: 6-position multiward lock, depths 0..7, MACS 7
  - Complex ward patterns with 8 depth variations
  - Maximum complexity for warded lock designs
- warded_lever_4: 5-position lever warded lock, depths 0..3, MACS 3
  - Lever-based ward obstructions
  - Common in historical door locks and padlocks
- warded_lever_6: 5-position lever warded lock, depths 0..5, MACS 5
  - Extended depth range for lever ward configurations
  - Higher security variant with 6 depth levels
- warded_skeleton_simple: 3-position skeleton key system, depths 0..1, MACS 1
  - Simplified ward pattern for skeleton key compatibility
  - Minimal ward obstructions, very low security
- warded_padlock_4ward: 4-position padlock warded lock, depths 0..3, MACS 3
  - Common Master Lock style warded padlock
  - 4-ward configuration for outdoor applications
- warded_lever_tumbler_5: 5-position lever tumbler warded lock, depths 0..4, MACS 2
  - Lever-based warding mechanism with 5 depth levels
  - Creates terminal invalidity due to MACS < depth range
- warded_master_padlock: 4-position Master-style padlock, depths 0..5, MACS 2
  - Realistic Master Lock warded padlock configuration
  - 6 depth levels with restrictive MACS creates terminal invalidity
- warded_door_mortise: 6-position door mortise warded lock, depths 0..7, MACS 3
  - Traditional door lock ward configuration
  - 8 depth levels with medium MACS for realistic complexity
- warded_cabinet_complex: 5-position complex cabinet lock, depths 0..6, MACS 2
  - High-complexity cabinet warded lock
  - 7 depth levels with low MACS creates many terminal sequences

Warded Locks (NO Terminal Invalidity - Educational)
- warded_binary: 4-position binary warded lock, depths 0..1, MACS 1
  - Simple ward configurations with binary notch patterns
  - NO terminal invalidity: depth range equals MACS
  - Educational example showing boundary case
- warded_skeleton_simple: 3-position skeleton key system, depths 0..1, MACS 1
  - Simplified ward pattern for skeleton key compatibility
  - NO terminal invalidity: minimal depth range equals MACS
  - Educational example of lock with no invalid configurations

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
- disc_abloy_disklock_6: 6-disc Abloy Disklock, depths 0..11, MACS 10
  - Disklock/Disklock Pro series for high-security applications
  - 12 depth positions for increased key combinations
- disc_abloy_disklock_10: 10-disc Abloy Disklock, depths 0..11, MACS 10
  - Extended disc count Disklock variant
  - Used in high-security padlocks and cylinders
- disc_abloy_exec_6: 6-disc Abloy Exec, depths 0..11, MACS 10
  - Exec series medium-high security disc detainer
  - Designed for commercial and institutional use
- disc_abloy_exec_10: 10-disc Abloy Exec, depths 0..11, MACS 10
  - Extended disc count for higher security applications
  - Common in European commercial installations
- disc_abloy_profile_6: 6-disc Abloy Profile, depths 0..9, MACS 8
  - Profile/High Profile series for general commercial use
  - Intermediate security level between Classic and Protec
- disc_abloy_profile_10: 10-disc Abloy Profile, depths 0..9, MACS 8
  - Extended disc configuration for Profile series
  - Widely used in Nordic countries for commercial locks
- disc_abloy_protec_8: 8-disc Abloy Protec, depths 0..11, MACS 10
  - Original Protec series (predecessor to Protec2)
  - High security disc detainer with 8-disc configuration

Tubular Pin Tumbler Locks
- tubular_4pin: 4-pin tubular lock, depths 0..9, MACS 8
  - Minimal tubular configuration for basic security
  - Used in some simple vending machine applications
- tubular_6pin: 6-pin tubular lock, depths 0..9, MACS 8
  - Common in smaller diameter tubular locks
  - Used in some computer locks and small equipment
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
- tubular_chicago_7pin: 7-pin Chicago Lock Company style, depths 0..7, MACS 6
  - Original Chicago Lock "Ace" patent design from 1933
  - 8 depth levels (0-7) standard for vintage tubular locks
  - Common in older vending machines and coin-operated equipment
- tubular_ace_8pin: 8-pin Ace-style tubular lock, depths 0..7, MACS 6
  - 8-pin variant of Chicago Lock design
  - Standard configuration for mid-security applications
  - Widely used in laundromat equipment and arcade machines

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
- wafer_gm_sidebar_10: 10-wafer GM sidebar lock, depths 0..9, MACS 8
  - General Motors sidebar wafer tumbler system
  - Used in GM vehicles from 1960s-1990s
  - Features sidebar mechanism for additional security
- wafer_ford_8cut: 8-wafer Ford automotive lock, depths 0..7, MACS 6
  - Ford Motor Company 8-cut wafer system
  - Common in Ford vehicles 1960s-1980s
  - Single-sided key with 8 depth positions
- wafer_ford_10cut: 10-wafer Ford automotive lock, depths 0..9, MACS 8
  - Extended Ford wafer system with 10 cuts
  - Used in later Ford models for increased security
  - Higher key combination count
- wafer_chrysler_7cut: 7-wafer Chrysler automotive lock, depths 0..6, MACS 5
  - Chrysler Corporation 7-cut wafer system
  - Used in Chrysler, Dodge, Plymouth vehicles
  - 7 depth positions for mid-level security
- wafer_chrysler_10cut: 10-wafer Chrysler automotive lock, depths 0..9, MACS 8
  - Extended Chrysler wafer system with 10 positions
  - Higher security variant for later model vehicles
  - Increased key space complexity
- wafer_desk_drawer_5: 5-wafer desk drawer lock, depths 0..4, MACS 3
  - Standard office desk drawer configuration
  - Simple 5-cut system for furniture applications
  - Very common in office furniture from major manufacturers
- wafer_cabinet_6: 6-wafer cabinet lock, depths 0..5, MACS 4
  - Filing cabinet and storage cabinet standard
  - 6-wafer configuration for light commercial use
  - Used in metal office cabinets and storage units
- wafer_mailbox_5: 5-wafer mailbox lock, depths 0..4, MACS 3
  - USPS and residential mailbox standard wafer lock
  - Weather-resistant low-security configuration
  - Simple 5-cut pattern for postal applications

Educational Presets (NO Terminal Invalidity)
- simple_no_terminal_2depth: 4-position lock, depths 0..1, MACS 1
  - Minimal lock with 2 depth levels
  - NO terminal invalidity: any sequence can be made valid
  - Demonstrates boundary case where depth range equals MACS
- simple_no_terminal_3depth: 4-position lock, depths 0..2, MACS 2
  - Simple lock with 3 depth levels
  - NO terminal invalidity: MACS equals depth range
  - Educational example showing when terminal invalidity cannot exist
- simple_no_terminal_equal_macs: 5-position lock, depths 0..5, MACS 5
  - Lock where MACS equals maximum depth
  - NO terminal invalidity: any depth transition is acceptable
  - Illustrates the mathematical condition where terminal invalidity is impossible

CLI
- Show presets:
  python3 tool.py presets
- Check:
  python3 tool.py check --preset kwikset_6in5 --seq 2,1,1,1,1,1
- Check with Bellman-Ford solver:
  python3 tool.py check --preset us --seq 1,7,1,1,1 --use-bellman-ford
- Repair:
  python3 tool.py repair --preset us --pins 5 --seq 1,7,1,1,1
- Repair with Bellman-Ford solver:
  python3 tool.py repair --preset us --seq 1,7,1,1,1 --use-bellman-ford
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
  python3 tool.py check --preset warded_lever_6 --seq 0,5,0,3,2
  python3 tool.py check --preset warded_skeleton_simple --seq 1,0,1
  python3 tool.py list-terminal --preset warded_padlock_4ward --limit 5
- Disc tumbler lock examples:
  python3 tool.py check --preset disc_abloy_classic_6 --seq 0,5,0,3,2,1
  python3 tool.py check --preset disc_abloy_classic_6 --seq 0,0,0,0,1,2
  python3 tool.py check --preset disc_abloy_disklock_10 --seq 0,11,5,8,3,7,2,9,4,6
  python3 tool.py check --preset disc_abloy_exec_6 --seq 0,10,5,7,3,8
  python3 tool.py check --preset disc_abloy_profile_10 --seq 0,9,4,7,2,6,1,8,3,5
  python3 tool.py list-terminal --preset disc_abloy_protec_8 --limit 5
- Tubular lock examples:
  python3 tool.py check --preset tubular_4pin --seq 0,9,5,3
  python3 tool.py check --preset tubular_6pin --seq 0,9,4,6,2,7
  python3 tool.py check --preset tubular_7pin --seq 0,9,0,5,3,2,1
  python3 tool.py check --preset tubular_chicago_7pin --seq 0,7,3,5,2,4,6
  python3 tool.py check --preset tubular_ace_8pin --seq 0,7,2,5,1,6,3,4
  python3 tool.py list-terminal --preset tubular_10pin --limit 5
- Wafer tumbler lock examples:
  python3 tool.py check --preset wafer_5wafer_shallow --seq 0,4,0,2,1
  python3 tool.py check --preset wafer_gm_sidebar_10 --seq 0,9,3,7,1,8,2,6,4,5
  python3 tool.py check --preset wafer_ford_8cut --seq 0,7,3,5,2,6,1,4
  python3 tool.py check --preset wafer_chrysler_10cut --seq 0,9,4,7,2,8,3,6,1,5
  python3 tool.py check --preset wafer_desk_drawer_5 --seq 0,4,2,3,1
  python3 tool.py list-terminal --preset wafer_cabinet_6 --limit 5
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

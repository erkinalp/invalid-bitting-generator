from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class KeySystem:
    name: str
    d_min: int
    d_max: int
    macs: int
    length: int
    forbidden_positions: Optional[List[int]] = None
    station_max_ceiling: Optional[List[Optional[int]]] = None
    stop_type: str = "shoulder"
    min_first_station_index: Optional[int] = None
    no_cut_mask: Optional[List[bool]] = None

    def validate_params(self) -> None:
        if self.d_min > self.d_max:
            raise ValueError("d_min must be <= d_max")
        if self.macs < 0:
            raise ValueError("macs must be >= 0")
        if self.length <= 0:
            raise ValueError("length must be > 0")
        if self.forbidden_positions:
            for p in self.forbidden_positions:
                if not (0 <= p < self.length):
                    raise ValueError("forbidden position out of range")
        if self.station_max_ceiling and len(self.station_max_ceiling) != self.length:
            raise ValueError("station_max_ceiling length mismatch")
        if self.min_first_station_index is not None and not (0 <= self.min_first_station_index < self.length):
            raise ValueError("min_first_station_index out of range")
        if self.no_cut_mask and len(self.no_cut_mask) != self.length:
            raise ValueError("no_cut_mask length mismatch")


def is_within_range(seq: List[int], d_min: int, d_max: int) -> bool:
    return all(d_min <= x <= d_max for x in seq)


def violates_forbidden_positions(seq: List[int], sys: KeySystem) -> bool:
    if not sys.forbidden_positions:
        return False
    return any(seq[i] > sys.d_min - 1 for i in sys.forbidden_positions)


def violates_no_cut_mask(seq: List[int], sys: KeySystem) -> bool:
    if not sys.no_cut_mask:
        return False
    for i, masked in enumerate(sys.no_cut_mask):
        if masked and seq[i] > sys.d_min - 1:
            return True
    return False


def violates_station_ceiling(seq: List[int], sys: KeySystem) -> bool:
    if not sys.station_max_ceiling:
        return False
    for i, ceiling in enumerate(sys.station_max_ceiling):
        if ceiling is None:
            continue
        if seq[i] > ceiling:
            return True
    return False


def violates_first_station(seq: List[int], sys: KeySystem) -> bool:
    if sys.min_first_station_index is None:
        return False
    for i in range(sys.min_first_station_index):
        if seq[i] > sys.d_min - 1:
            return True
    return False


def macs_ok(seq: List[int], macs: int) -> bool:
    return all(abs(seq[i + 1] - seq[i]) <= macs for i in range(len(seq) - 1))


def minimal_macs_repair_or_none(seq: List[int], sys: KeySystem) -> Optional[List[int]]:
    n = sys.length
    if len(seq) != n:
        raise ValueError("sequence length mismatch")
    y = seq[:]
    if not is_within_range(y, sys.d_min, sys.d_max):
        return None
    if violates_station_ceiling(y, sys):
        return None
    if violates_forbidden_positions(y, sys) or violates_no_cut_mask(y, sys):
        return None
    if violates_first_station(y, sys):
        return None

    changed = True
    while changed:
        changed = False
        for i in range(1, n):
            needed = y[i - 1] - sys.macs
            if y[i] < needed:
                new_val = needed
                ceiling = sys.d_max
                if sys.station_max_ceiling and sys.station_max_ceiling[i] is not None:
                    ceiling = min(ceiling, sys.station_max_ceiling[i])
                if new_val > ceiling:
                    return None
                if (sys.forbidden_positions and i in sys.forbidden_positions and new_val > sys.d_min - 1) or (
                    sys.no_cut_mask and sys.no_cut_mask[i] and new_val > sys.d_min - 1
                ):
                    return None
                if sys.min_first_station_index is not None and i < sys.min_first_station_index and new_val > sys.d_min - 1:
                    return None
                if new_val > y[i]:
                    y[i] = new_val
                    changed = True
        for i in range(n - 2, -1, -1):
            needed = y[i + 1] - sys.macs
            if y[i] < needed:
                new_val = needed
                ceiling = sys.d_max
                if sys.station_max_ceiling and sys.station_max_ceiling[i] is not None:
                    ceiling = min(ceiling, sys.station_max_ceiling[i])
                if new_val > ceiling:
                    return None
                if (sys.forbidden_positions and i in sys.forbidden_positions and new_val > sys.d_min - 1) or (
                    sys.no_cut_mask and sys.no_cut_mask[i] and new_val > sys.d_min - 1
                ):
                    return None
                if sys.min_first_station_index is not None and i < sys.min_first_station_index and new_val > sys.d_min - 1:
                    return None
                if new_val > y[i]:
                    y[i] = new_val
                    changed = True

    if not macs_ok(y, sys.macs):
        return None
    if not is_within_range(y, sys.d_min, sys.d_max):
        return None
    if violates_station_ceiling(y, sys):
        return None
    if violates_forbidden_positions(y, sys) or violates_no_cut_mask(y, sys):
        return None
    if violates_first_station(y, sys):
        return None
    return y


def is_terminally_invalid(seq: List[int], sys: KeySystem) -> Tuple[bool, str]:
    if len(seq) != sys.length:
        return True, "length mismatch"
    if not is_within_range(seq, sys.d_min, sys.d_max):
        return True, "exceeds maximum depth, cannot fix by deepening"
    if violates_first_station(seq, sys):
        return True, "first station not allowed for this stop type"
    if violates_forbidden_positions(seq, sys) or violates_no_cut_mask(seq, sys):
        return True, "forbidden/no-cut station cut present"
    if violates_station_ceiling(seq, sys):
        return True, "station-specific ceiling violated"

    repaired = minimal_macs_repair_or_none(seq, sys)
    if repaired is None:
        return True, "cannot satisfy MACS and constraints via deepening-only"
    if macs_ok(repaired, sys.macs) and is_within_range(repaired, sys.d_min, sys.d_max):
        if not violates_station_ceiling(repaired, sys) and not violates_forbidden_positions(repaired, sys) and not violates_no_cut_mask(repaired, sys) and not violates_first_station(repaired, sys):
            return False, "repairable to a valid bitting by deepening"
    return True, "unknown terminal condition"


def generate_terminal_examples(sys: KeySystem, limit: int = 10) -> List[List[int]]:
    examples: List[List[int]] = []
    over = [sys.d_max + 1] + [sys.d_min] * (sys.length - 1)
    examples.append(over)

    if sys.no_cut_mask:
        s = [sys.d_min] * sys.length
        for i, m in enumerate(sys.no_cut_mask):
            if m:
                s[i] = sys.d_min + 1
        examples.append(s)

    if sys.forbidden_positions:
        s = [sys.d_min] * sys.length
        for p in sys.forbidden_positions:
            s[p] = sys.d_min + 1
        examples.append(s)

    if sys.min_first_station_index is not None and sys.min_first_station_index > 0:
        s = [sys.d_min + 1] + [sys.d_min] * (sys.length - 1)
        examples.append(s)

    if sys.station_max_ceiling:
        for i, ceiling in enumerate(sys.station_max_ceiling):
            if ceiling is not None and ceiling < sys.d_max:
                s = [sys.d_min] * sys.length
                s[i] = ceiling + 1
                examples.append(s)
                if len(examples) >= limit:
                    return examples

    from itertools import product
    depth_space = list(range(sys.d_min, sys.d_max + 1))
    for combo in product(depth_space, repeat=min(sys.length, 4)):
        seq = list(combo) + [sys.d_min] * (sys.length - len(combo))
        term, _ = is_terminally_invalid(seq, sys)
        if term:
            examples.append(seq)
            if len(examples) >= limit:
                break
    return examples


def preset_us(length: int = 5, d_min: int = 1, d_max: int = 7, macs: int = 2) -> KeySystem:
    return KeySystem(name=f"US_{length}", d_min=d_min, d_max=d_max, macs=macs, length=length)


def preset_euro(length: int = 5, d_min: int = 1, d_max: int = 10, macs: int = 2) -> KeySystem:
    return KeySystem(name=f"EURO_{length}", d_min=d_min, d_max=d_max, macs=macs, length=length)


def preset_kwikset_smartkey_6key_in_5plug() -> KeySystem:
    length = 6
    no_cut = [False] * length
    no_cut[0] = True
    return KeySystem(
        name="Kwikset_SmartKey_6key_in_5plug",
        d_min=1,
        d_max=7,
        macs=2,
        length=length,
        no_cut_mask=no_cut,
        stop_type="shoulder",
        min_first_station_index=0,
    )


def preset_schlage_everest_fullsize(length: int = 6) -> KeySystem:
    return KeySystem(
        name=f"Schlage_Everest_Full_{length}",
        d_min=1,
        d_max=7,
        macs=7,
        length=length,
        stop_type="shoulder",
        min_first_station_index=0,
    )


def preset_best_a2_tip(length: int = 7) -> KeySystem:
    return KeySystem(
        name=f"BEST_A2_Tip_{length}",
        d_min=0,
        d_max=9,
        macs=7,
        length=length,
        stop_type="tip",
        min_first_station_index=1,
    )
def preset_yale_keymark_conventional(length: int = 6) -> KeySystem:
    return KeySystem(
        name=f"Yale_KeyMark_Conventional_{length}",
        d_min=1,
        d_max=7,
        macs=7,
        length=length,
        stop_type="shoulder",
        min_first_station_index=0,
    )


def preset_yale_ic_a2_tip(length: int = 7) -> KeySystem:
    return KeySystem(
        name=f"Yale_IC_A2_Tip_{length}",
        d_min=0,
        d_max=9,
        macs=7,
        length=length,
        stop_type="tip",
        min_first_station_index=1,
    )


def preset_assa_abloy_yale_conventional(length: int = 6) -> KeySystem:
    return KeySystem(
        name=f"ASSAABLOY_Yale_Conventional_{length}",
        d_min=1,
        d_max=7,
        macs=7,
        length=length,
        stop_type="shoulder",
        min_first_station_index=0,
    )



def preset_schlage_everest29_sl_tip(length: int = 6) -> KeySystem:
    return KeySystem(
        name=f"Schlage_Everest29_SL_Tip_{length}",
        d_min=1,
        d_max=7,
        macs=7,
        length=length,
        stop_type="tip",
        min_first_station_index=1,
    )


def preset_warded_binary(length: int = 4) -> KeySystem:
    return KeySystem(
        name=f"Warded_Binary_{length}",
        d_min=0,
        d_max=1,
        macs=1,
        length=length,
        stop_type="shoulder",
        min_first_station_index=0,
    )


def preset_warded_multiward_4(length: int = 6) -> KeySystem:
    return KeySystem(
        name=f"Warded_MultiWard4_{length}",
        d_min=0,
        d_max=3,
        macs=3,
        length=length,
        stop_type="shoulder",
        min_first_station_index=0,
    )


def preset_warded_multiward_8(length: int = 6) -> KeySystem:
    return KeySystem(
        name=f"Warded_MultiWard8_{length}",
        d_min=0,
        d_max=7,
        macs=7,
        length=length,
        stop_type="shoulder",
        min_first_station_index=0,
    )


def preset_disc_abloy_classic_6(length: int = 6) -> KeySystem:
    return KeySystem(
        name=f"Disc_Abloy_Classic_{length}",
        d_min=0,
        d_max=6,
        macs=6,
        length=length,
        stop_type="shoulder",
        min_first_station_index=0,
    )


def preset_disc_abloy_classic_10(length: int = 10) -> KeySystem:
    return KeySystem(
        name=f"Disc_Abloy_Classic_{length}",
        d_min=0,
        d_max=9,
        macs=9,
        length=length,
        stop_type="shoulder",
        min_first_station_index=0,
    )


def preset_disc_abloy_protec2_6(length: int = 6) -> KeySystem:
    return KeySystem(
        name=f"Disc_Abloy_Protec2_{length}",
        d_min=0,
        d_max=9,
        macs=8,
        length=length,
        stop_type="shoulder",
        min_first_station_index=0,
    )


def preset_disc_abloy_protec2_10(length: int = 10) -> KeySystem:
    return KeySystem(
        name=f"Disc_Abloy_Protec2_{length}",
        d_min=0,
        d_max=11,
        macs=10,
        length=length,
        stop_type="shoulder",
        min_first_station_index=0,
    )


def preset_tubular_7pin(length: int = 7) -> KeySystem:
    return KeySystem(
        name=f"Tubular_7pin_{length}",
        d_min=0,
        d_max=9,
        macs=8,
        length=length,
        stop_type="shoulder",
        min_first_station_index=0,
    )


def preset_tubular_8pin(length: int = 8) -> KeySystem:
    return KeySystem(
        name=f"Tubular_8pin_{length}",
        d_min=0,
        d_max=9,
        macs=8,
        length=length,
        stop_type="shoulder",
        min_first_station_index=0,
    )


def preset_tubular_10pin(length: int = 10) -> KeySystem:
    return KeySystem(
        name=f"Tubular_10pin_{length}",
        d_min=0,
        d_max=9,
        macs=8,
        length=length,
        stop_type="shoulder",
        min_first_station_index=0,
    )


def preset_wafer_5wafer_shallow(length: int = 5) -> KeySystem:
    return KeySystem(
        name=f"Wafer_5wafer_Shallow_{length}",
        d_min=0,
        d_max=4,
        macs=3,
        length=length,
        stop_type="shoulder",
        min_first_station_index=0,
    )


def preset_wafer_5wafer_deep(length: int = 5) -> KeySystem:
    return KeySystem(
        name=f"Wafer_5wafer_Deep_{length}",
        d_min=0,
        d_max=7,
        macs=6,
        length=length,
        stop_type="shoulder",
        min_first_station_index=0,
    )


def preset_wafer_6wafer_automotive(length: int = 6) -> KeySystem:
    return KeySystem(
        name=f"Wafer_6wafer_Auto_{length}",
        d_min=0,
        d_max=5,
        macs=4,
        length=length,
        stop_type="shoulder",
        min_first_station_index=0,
    )


def preset_wafer_10wafer_double(length: int = 10) -> KeySystem:
    return KeySystem(
        name=f"Wafer_10wafer_Double_{length}",
        d_min=0,
        d_max=9,
        macs=8,
        length=length,
        stop_type="shoulder",
        min_first_station_index=0,
    )


def get_preset(name: str) -> KeySystem:
    if name == "us":
        return preset_us()
    if name == "euro":
        return preset_euro()
    if name == "kwikset_6in5":
        return preset_kwikset_smartkey_6key_in_5plug()
    if name == "schlage_everest_full":
        return preset_schlage_everest_fullsize()
    if name == "schlage_everest29_sl_tip":
        return preset_schlage_everest29_sl_tip()
    if name == "best_a2_tip":
        return preset_best_a2_tip()
    if name == "yale_keymark":
        return preset_yale_keymark_conventional()
    if name == "yale_ic_a2_tip":
        return preset_yale_ic_a2_tip()
    if name == "assa_abloy_yale":
        return preset_assa_abloy_yale_conventional()
    if name == "warded_binary":
        return preset_warded_binary()
    if name == "warded_multiward_4":
        return preset_warded_multiward_4()
    if name == "warded_multiward_8":
        return preset_warded_multiward_8()
    if name == "disc_abloy_classic_6":
        return preset_disc_abloy_classic_6()
    if name == "disc_abloy_classic_10":
        return preset_disc_abloy_classic_10()
    if name == "disc_abloy_protec2_6":
        return preset_disc_abloy_protec2_6()
    if name == "disc_abloy_protec2_10":
        return preset_disc_abloy_protec2_10()
    if name == "tubular_7pin":
        return preset_tubular_7pin()
    if name == "tubular_8pin":
        return preset_tubular_8pin()
    if name == "tubular_10pin":
        return preset_tubular_10pin()
    if name == "wafer_5wafer_shallow":
        return preset_wafer_5wafer_shallow()
    if name == "wafer_5wafer_deep":
        return preset_wafer_5wafer_deep()
    if name == "wafer_6wafer_auto":
        return preset_wafer_6wafer_automotive()
    if name == "wafer_10wafer_double":
        return preset_wafer_10wafer_double()
    raise ValueError("unknown preset")


def parse_seq(s: str, length: int) -> List[int]:
    parts = [int(x) for x in s.split(",") if x.strip() != ""]
    if len(parts) != length:
        raise ValueError("sequence length mismatch")
    return parts


def cli() -> None:
    ap = argparse.ArgumentParser(prog="key-bittings")
    sub = ap.add_subparsers(dest="cmd", required=True)

    ap_common = argparse.ArgumentParser(add_help=False)
    ap_common.add_argument("--preset", choices=["us", "euro", "kwikset_6in5", "schlage_everest_full", "schlage_everest29_sl_tip", "best_a2_tip", "yale_keymark", "yale_ic_a2_tip", "assa_abloy_yale", "warded_binary", "warded_multiward_4", "warded_multiward_8", "disc_abloy_classic_6", "disc_abloy_classic_10", "disc_abloy_protec2_6", "disc_abloy_protec2_10", "tubular_7pin", "tubular_8pin", "tubular_10pin", "wafer_5wafer_shallow", "wafer_5wafer_deep", "wafer_6wafer_auto", "wafer_10wafer_double"], default="us")
    ap_common.add_argument("--pins", type=int)
    ap_common.add_argument("--depth-min", type=int)
    ap_common.add_argument("--depth-max", type=int)
    ap_common.add_argument("--macs", type=int)
    ap_common.add_argument("--no-cut", type=str)
    ap_common.add_argument("--ceilings", type=str)
    ap_common.add_argument("--min-first-station", type=int)
    ap_common.add_argument("--stop-type", choices=["shoulder", "tip"])

    c_check = sub.add_parser("check", parents=[ap_common])
    c_check.add_argument("--seq", required=True, type=str)

    c_repair = sub.add_parser("repair", parents=[ap_common])
    c_repair.add_argument("--seq", required=True, type=str)

    c_list = sub.add_parser("list-terminal", parents=[ap_common])
    c_list.add_argument("--limit", type=int, default=10)

    c_enum = sub.add_parser("enumerate", parents=[ap_common])
    c_enum.add_argument("--max-repeat", type=int, default=4)

    c_presets = sub.add_parser("presets")

    args = ap.parse_args()

    if args.cmd == "presets":
        print("Pin tumbler presets: us, euro, kwikset_6in5, schlage_everest_full, schlage_everest29_sl_tip, best_a2_tip, yale_keymark, yale_ic_a2_tip, assa_abloy_yale")
        print("Warded lock presets: warded_binary, warded_multiward_4, warded_multiward_8")
        print("Disc tumbler presets: disc_abloy_classic_6, disc_abloy_classic_10, disc_abloy_protec2_6, disc_abloy_protec2_10")
        print("Tubular lock presets: tubular_7pin, tubular_8pin, tubular_10pin")
        print("Wafer tumbler presets: wafer_5wafer_shallow, wafer_5wafer_deep, wafer_6wafer_auto, wafer_10wafer_double")
        return

    sys = get_preset(args.preset)

    if args.pins:
        sys.length = args.pins
    if args.depth_min:
        sys.d_min = args.depth_min
    if args.depth_max:
        sys.d_max = args.depth_max
    if args.macs is not None:
        sys.macs = args.macs
    if args.stop_type:
        sys.stop_type = args.stop_type
    if args.min_first_station is not None:
        sys.min_first_station_index = args.min_first_station
    if args.no_cut:
        mask = []
        for tok in args.no_cut.split(","):
            tok = tok.strip().lower()
            mask.append(tok in ("1", "true", "yes", "y"))
        sys.no_cut_mask = mask
    if args.ceilings:
        cl: List[Optional[int]] = []
        for tok in args.ceilings.split(","):
            t = tok.strip()
            if t.lower() == "none":
                cl.append(None)
            else:
                cl.append(int(t))
        sys.station_max_ceiling = cl

    sys.validate_params()

    if args.cmd in ("check", "repair"):
        seq = parse_seq(args.seq, sys.length)
        if args.cmd == "check":
            term, reason = is_terminally_invalid(seq, sys)
            print(f"terminal={term} reason={reason}")
        else:
            repaired = minimal_macs_repair_or_none(seq, sys)
            print(f"repaired={repaired}")
        return

    if args.cmd == "list-terminal":
        ex = generate_terminal_examples(sys, args.limit)
        for e in ex:
            print(",".join(str(x) for x in e))
        return

    if args.cmd == "enumerate":
        from itertools import product
        depth_space = list(range(sys.d_min, sys.d_max + 1))
        count_term = 0
        count_total = 0
        for combo in product(depth_space, repeat=min(sys.length, args.max_repeat)):
            seq = list(combo) + [sys.d_min] * (sys.length - len(combo))
            term, _ = is_terminally_invalid(seq, sys)
            count_total += 1
            if term:
                count_term += 1
        print(f"checked={count_total} terminal={count_term}")
        return


def demo():
    us = preset_us()
    eu = preset_euro()
    kw = preset_kwikset_smartkey_6key_in_5plug()
    sch = preset_schlage_everest_fullsize()
    sl = preset_schlage_everest29_sl_tip()

    samples = [
        [1, 7, 1, 1, 1, 1],
        [1, 7, 1, 7, 1, 1],
        [7, 1, 7, 1, 7, 1],
        [1, 1, 1, 1, 1, 1],
        [8, 1, 1, 1, 1, 1],
    ]

    for sys in (us, eu, kw, sch, sl):
        print(f"System: {sys.name}")
        s = samples[0][: sys.length]
        term, reason = is_terminally_invalid(s, sys)
        repaired = minimal_macs_repair_or_none(s, sys)
        print(f"  seq={s} -> terminal={term}, reason={reason}, repaired={repaired}")
        gens = generate_terminal_examples(sys)
        print("  examples:")
        for g in gens[:3]:
            print("   ", g)


if __name__ == "__main__":
    import sys as _sys
    if len(_sys.argv) > 1:
        cli()
    else:
        demo()

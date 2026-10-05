# -*- coding: utf-8 -*-
"""
BailuKai - All-in-One Medium Batch Builder for FontForge

Usage:
    fontforge -lang=py -script BailuKai_build_medium_all.py [TARGET] [WEIGHT]

Arguments:
    TARGET: Optional. Specific variant to build:
            - Standard: 'S', 'T', 'TW', 'W'
            - Pseudo-Vertical (-90): 'S-90', 'T-90', 'TW-90', 'W-90'
            - Groups: 'all' (S, T, TW, W), 'all-90' (all -90 variants), 'everything' (all 8 variants).
            Default is 'all'.
    WEIGHT: Optional. Emboldening weight value. Default is 12 (+6 contour expansion).

Examples:
    fontforge -lang=py -script BailuKai_build_medium_all.py
    fontforge -lang=py -script BailuKai_build_medium_all.py all-90
    fontforge -lang=py -script BailuKai_build_medium_all.py S-90
    fontforge -lang=py -script BailuKai_build_medium_all.py everything 12
"""

import os
import sys
import importlib.util
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

VARIANTS = {
    # Standard variants
    "S": {
        "script": "BailuKai_build_medium-S.py",
        "name": "BailuKai-S Medium (原俠正楷-S)",
        "output": "BailuKai-Medium-S.ttf",
    },
    "T": {
        "script": "BailuKai_build_medium-T.py",
        "name": "BailuKai-T Medium (原俠正楷-T)",
        "output": "BailuKai-Medium-T.ttf",
    },
    "TW": {
        "script": "BailuKai_build_medium-TW.py",
        "name": "BailuKai-TW Medium (原俠正楷-TW)",
        "output": "BailuKai-Medium-TW.ttf",
    },
    "W": {
        "script": "BailuKai_build_medium-W.py",
        "name": "BailuKai-W Medium (原俠正楷-W)",
        "output": "BailuKai-Medium-W.ttf",
    },
    # Pseudo-vertical (-90) variants
    "S-90": {
        "script": "BailuKai_build_medium-S-90.py",
        "name": "BailuKai-S-90 Medium (原俠正楷-S-90)",
        "output": "BailuKai-Medium-S-90.ttf",
    },
    "T-90": {
        "script": "BailuKai_build_medium-T-90.py",
        "name": "BailuKai-T-90 Medium (原俠正楷-T-90)",
        "output": "BailuKai-Medium-T-90.ttf",
    },
    "TW-90": {
        "script": "BailuKai_build_medium-TW-90.py",
        "name": "BailuKai-TW-90 Medium (原俠正楷-TW-90)",
        "output": "BailuKai-Medium-TW-90.ttf",
    },
    "W-90": {
        "script": "BailuKai_build_medium-W-90.py",
        "name": "BailuKai-W-90 Medium (原俠正楷-W-90)",
        "output": "BailuKai-Medium-W-90.ttf",
    },
}

GROUPS = {
    "all": ["S", "T", "TW", "W"],
    "all-90": ["S-90", "T-90", "TW-90", "W-90"],
    "everything": ["S", "T", "TW", "W", "S-90", "T-90", "TW-90", "W-90"],
}


def load_module_from_file(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load spec for {file_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    target = "all"
    weight_val = 12

    if len(sys.argv) >= 2:
        arg1 = sys.argv[1].strip()
        arg1_upper = arg1.upper()
        arg1_lower = arg1.lower()
        if arg1_upper in VARIANTS:
            target = arg1_upper
        elif arg1_lower in GROUPS:
            target = arg1_lower
        elif arg1.isdigit():
            weight_val = int(arg1)
        else:
            valid_targets = list(VARIANTS.keys()) + list(GROUPS.keys())
            print(f"Unknown target '{arg1}'. Available: {', '.join(valid_targets)}")
            return 2

    if len(sys.argv) >= 3:
        try:
            weight_val = int(sys.argv[2])
        except ValueError:
            print(f"Invalid weight '{sys.argv[2]}', using default 12")

    if target in GROUPS:
        targets_to_build = GROUPS[target]
    else:
        targets_to_build = [target]

    print("=" * 70)
    print("BailuKai Medium Batch Builder")
    print("=" * 70)
    print(f"Target variants : {', '.join(targets_to_build)}")
    print(f"Weight value    : +{weight_val} CJK")
    print(f"Working dir     : {SCRIPT_DIR}")
    print("=" * 70)
    print("")

    start_all = time.time()
    results = {}

    for var in targets_to_build:
        info = VARIANTS[var]
        script_file = os.path.join(SCRIPT_DIR, info["script"])
        print(f">>> [{var}] Building {info['name']}...")
        if not os.path.isfile(script_file):
            print(f"ERROR: Script not found: {script_file}")
            results[var] = "MISSING SCRIPT"
            continue

        var_start = time.time()
        try:
            safe_mod_name = f"builder_{var.replace('-', '_')}"
            mod = load_module_from_file(safe_mod_name, script_file)
            ret = mod.build(input_file=None, weight_val=weight_val, out_dir=SCRIPT_DIR)
            elapsed = time.time() - var_start
            if ret == 0:
                results[var] = f"SUCCESS ({elapsed:.1f}s)"
            else:
                results[var] = f"FAILED (exit code {ret})"
        except Exception as e:
            elapsed = time.time() - var_start
            print(f"ERROR building variant {var}: {e}")
            results[var] = f"EXCEPTION ({elapsed:.1f}s)"

        print("")

    total_time = time.time() - start_all
    print("=" * 70)
    print("BATCH BUILD SUMMARY")
    print("=" * 70)
    all_ok = True
    for var in targets_to_build:
        status = results.get(var, "UNKNOWN")
        info = VARIANTS[var]
        print(f"  [{var}] {info['output']:<28} : {status}")
        if not status.startswith("SUCCESS"):
            all_ok = False

    print(f"\nTotal elapsed time: {total_time:.1f}s")
    print("=" * 70)

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())

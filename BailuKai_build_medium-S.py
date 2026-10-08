# -*- coding: utf-8 -*-
"""
BailuKai-S - one-click Medium builder for FontForge (Deduplicated)

Key Features:
1. Built specifically for GuanKiapTsingKhai-S (原俠正楷-S v1.20, https://github.com/tonyhuan/GuanKiapTsingKhai):
   - In -S variant, quotation marks are substituted, and most simplified characters are converted
     to traditional forms, while 1-to-many simplified characters are preserved.
2. Root cause resolution for over-thick glyphs (十, 一, 方, 生, 日, 而, 玉, 又, 馬, 見, 面, 金, 高, 老, 士, 心, 血, etc.)
   and ghosting/spike artifacts on "長":
   FontForge's font.selection.all() selects by ENCODING SLOT (codepoint), not by glyph.
   In GuanKiapTsingKhai-S.ttf, hundreds of glyphs are multi-encoded (e.g. both as CJK Unified Ideographs
   and Kangxi Radicals U+2F00..U+2FD5). font.selection.all() selected these glyphs multiple times,
   causing FontForge's C-level changeWeight() to execute TWICE (+24 instead of +12).
   In this builder, selection is strictly deduplicated by unique glyphname, guaranteeing each glyph
   undergoes changeWeight() EXACTLY ONCE.
3. Verified that with deduplicated changeWeight(12), characters measurably and visually
   match LXGWWenKaiTC-Medium (+6 stroke contour expansion).
4. Maintained pristine reference injection for fragile glyphs ("傳", "導", "育").
5. Metadata & Open Source License:
   - Family Name: BailuKai-S (白鷺楷-S / 白鹭楷-S)
   - SubFamily: Medium
   - Full Name: BailuKai-S Medium (白鷺楷-S Medium / 白鹭楷-S Medium)
   - PostScript Name: BailuKai-S-Medium
   - License: SIL Open Font License 1.1 (OFL-1.1)
   - Copyright: Copyright 2026 huthief (https://github.com/huthief/BailuKai)
"""

import fontforge
import os
import sys
import csv
import traceback

# ============================================================
# CONFIG
# ============================================================

DEFAULT_WEIGHT = 12  # FontForge changeWeight(12) = +6 contour expansion, perfectly matching LXGWWenKaiTC-Medium

VARIANT_SUFFIX = "S"
FAMILY_NAME = "BailuKai-S"
SUBFAMILY_NAME = "Medium"
FULL_NAME = "BailuKai-S Medium"
POSTSCRIPT_NAME = "BailuKai-S-Medium"
CHINESE_TRAD_FAMILY_NAME = "白鷺楷-S"
CHINESE_TRAD_FULL_NAME = "白鷺楷-S Medium"
CHINESE_SIMP_FAMILY_NAME = "白鹭楷-S"
CHINESE_SIMP_FULL_NAME = "白鹭楷-S Medium"

COPYRIGHT = "Copyright 2026 huthief (https://github.com/huthief/BailuKai)"
VENDOR_URL = "https://github.com/huthief/BailuKai"
DESIGNER_URL = "https://github.com/huthief/BailuKai"
LICENSE = "This Font Software is licensed under the SIL Open Font License, Version 1.1. This license is available with a FAQ at: https://scripts.sil.org/OFL"
LICENSE_URL = "https://scripts.sil.org/OFL"
UNIQUE_ID = "BailuKai-S Medium; Version 202610100"
VERSION = "Version 202610100"

OUTPUT_TTF = "BailuKai-Medium-S.ttf"
REPORT_CSV = "BailuKai-Medium-S-Candidates.csv"
REPORT_TXT = "BailuKai-Medium-S-Candidates.txt"

# Optional fine-tuning dictionary (clean baseline)
OPTICAL_CORRECTIONS = {}

# Complex/fragile glyphs to protect from destructive FontForge changeWeight math
FRAGILE_GLYPHS = {
    "傳",
    "導",
    "育",
    "帳",
}

# Candidate scoring reference set
SIMPLE_GLYPHS = set(
    "一丨丶丿乙二十丁七卜八人入九力刀乃又"
    "三干于士土工才寸大丈万上下口山女小川"
    "己已巳巾千乞弓子孑孓也久凡夕"
    "心戈戶手支文斗斤方日月木欠止歹"
    "比毛氏气水火父爻片牙牛犬王玉"
    "瓜瓦甘生用田由甲申白皮皿目矛"
    "矢石示禾穴立竹米糸羊羽老耳聿"
    "肉臣自至臼舌舟色艸虫衣西見角"
    "言谷豆豕豸貝車辛辰辵邑酉釆里"
    "金長門阜雨青非面革音頁風飛食"
    "首香馬骨高鬥鬯鬲鬼魚鳥鹵鹿"
    "麻黃黑黍"
)

CJK_RANGES = [
    (0x3400, 0x4DBF),
    (0x4E00, 0x9FFF),
    (0xF900, 0xFAFF),
    (0x20000, 0x2A6DF),
    (0x2A700, 0x2B73F),
    (0x2B740, 0x2B81F),
    (0x2B820, 0x2CEAF),
    (0x2CEB0, 0x2EBEF),
    (0x30000, 0x3134F),
]


# ============================================================
# HELPERS
# ============================================================

def is_cjk(cp):
    return any(a <= cp <= b for a, b in CJK_RANGES)


def find_reference_font(search_dirs):
    candidates = [
        "霞鶩文楷LXGWWenKaiTC-Medium.ttf",
        "LXGWWenKaiTC-Medium.ttf",
    ]
    for d in search_dirs:
        if not d or not os.path.isdir(d):
            continue
        for name in candidates:
            p = os.path.join(d, name)
            if os.path.isfile(p):
                return p
    return None


def bbox(glyph):
    try:
        b = glyph.boundingBox()
        if len(b) >= 4:
            return tuple(float(x) for x in b[:4])
    except Exception:
        pass
    return (0.0, 0.0, 0.0, 0.0)


def bbox_area(b):
    return max(0.0, b[2] - b[0]) * max(0.0, b[3] - b[1])


def contour_count(glyph):
    try:
        return len(glyph.layers[glyph.activeLayer])
    except Exception:
        return 0


def point_count(glyph):
    total = 0
    try:
        layer = glyph.layers[glyph.activeLayer]
        for contour in layer:
            try:
                total += len(contour)
            except Exception:
                pass
    except Exception:
        pass
    return total


def get_glyph_by_char(font, char):
    target = ord(char)
    try:
        if target in font:
            return font[target]
    except Exception:
        pass
    return None


def collect_metrics(font):
    data = {}
    for g in font.glyphs():
        try:
            cp = g.unicode
            if cp is None or cp < 0 or not is_cjk(cp):
                continue
            data[cp] = {
                "char": chr(cp),
                "bbox": bbox(g),
                "contours": contour_count(g),
                "points": point_count(g),
            }
        except Exception:
            continue
    return data


def score_candidate(old, new):
    old_area = bbox_area(old["bbox"])
    new_area = bbox_area(new["bbox"])

    area_growth = 0.0
    if old_area > 0:
        area_growth = (new_area - old_area) / old_area * 100.0

    ow = old["bbox"][2] - old["bbox"][0]
    nw = new["bbox"][2] - new["bbox"][0]
    width_growth = (nw - ow) / ow * 100.0 if ow > 0 else 0.0

    oh = old["bbox"][3] - old["bbox"][1]
    nh = new["bbox"][3] - new["bbox"][1]
    height_growth = (nh - oh) / oh * 100.0 if oh > 0 else 0.0

    score = 0.0
    reasons = []

    if area_growth >= 7:
        score += 15
        reasons.append("large bbox growth")
    elif area_growth >= 4:
        score += 10
        reasons.append("bbox growth")
    elif area_growth >= 2:
        score += 5

    if width_growth >= 3:
        score += 8
        reasons.append("wide expansion")
    elif width_growth >= 1.5:
        score += 4

    if height_growth >= 3:
        score += 5
        reasons.append("height expansion")

    ch = new["char"]
    if ch in SIMPLE_GLYPHS:
        score += 20
        reasons.append("simple glyph")

    if new["contours"] >= 15:
        score += 8
        reasons.append("complex contours")
    elif new["contours"] >= 8:
        score += 4

    if new["points"] >= 100:
        score += 8
        reasons.append("high point count")
    elif new["points"] >= 50:
        score += 4

    if score >= 45:
        level = "A"
    elif score >= 30:
        level = "B"
    elif score >= 15:
        level = "C"
    else:
        level = "D"

    return score, level, area_growth, width_growth, height_growth, "; ".join(reasons)


def write_reports(results, csv_path, txt_path, weight_val):
    results.sort(key=lambda x: (-x["score"], x["codepoint"]))

    for i, row in enumerate(results, 1):
        row["rank"] = i

    fields = [
        "rank", "char", "unicode", "codepoint", "level", "score",
        "area_growth", "width_growth", "height_growth",
        "old_contours", "new_contours",
        "old_points", "new_points", "reasons"
    ]

    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in results:
            w.writerow(row)

    counts = {x: 0 for x in "ABCD"}
    for row in results:
        counts[row["level"]] += 1

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("BailuKai-S Medium Candidate Report (Deduplicated)\n")
        f.write("============================================================\n\n")
        f.write(f"Target font: {FAMILY_NAME} ({FULL_NAME})\n")
        f.write(f"Global transformation: +{weight_val} CJK (stroke expansion +{weight_val/2:.1f}, aligned with LXGWWenKaiTC-Medium)\n")
        f.write("Deduplication: Enabled (guarantees each unique glyph is emboldened exactly once)\n")
        f.write("Protected glyphs (injected from reference): " + ", ".join(sorted(FRAGILE_GLYPHS)) + "\n\n")
        f.write("Level summary:\n")
        f.write("  A High risk   : {}\n".format(counts["A"]))
        f.write("  B Medium risk : {}\n".format(counts["B"]))
        f.write("  C Low risk    : {}\n".format(counts["C"]))
        f.write("  D Normal      : {}\n\n".format(counts["D"]))
        f.write("Top 200 candidates\n")
        f.write("==================\n\n")

        for row in results[:200]:
            f.write(
                "#{:4d} {} {} Level {} Score {:.1f}\n".format(
                    row["rank"], row["char"], row["unicode"],
                    row["level"], row["score"]
                )
            )
            f.write(
                "      Area +{:.2f}% | Width +{:.2f}% | Height +{:.2f}%\n".format(
                    row["area_growth"],
                    row["width_growth"],
                    row["height_growth"]
                )
            )
            f.write("      {}\n\n".format(row["reasons"]))


# ============================================================
# BUILD PIPELINE
# ============================================================

def build(input_file=None, weight_val=DEFAULT_WEIGHT, out_dir=None):
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Resolve input file if not provided
    if not input_file:
        default_candidates = [
            os.path.join(script_dir, "reference", "GuanKiapTsingKhai-S.ttf"),
            os.path.join(script_dir, "reference", "原俠正楷-S.ttf"),
            os.path.join(script_dir, "reference", "原俠正楷GuanKiapTsingKhai-S.ttf"),
        ]
        input_file = next((f for f in default_candidates if os.path.isfile(f)), None)
        if not input_file:
            print("Usage:")
            print("  fontforge -lang=py -script BailuKai_build_medium-S.py [INPUT.ttf] [WEIGHT]")
            print("")
            print("ERROR: No input file specified and default base font not found at:")
            print("  ", default_candidates[0])
            print("")
            print("Please place 'GuanKiapTsingKhai-S.ttf' into the 'reference/' directory.")
            return 2

    if not os.path.isfile(input_file):
        print("ERROR: input file not found:", input_file)
        return 2

    # Output directory
    input_dir = os.path.dirname(input_file)
    if out_dir is None:
        if os.path.basename(input_dir).lower() == "reference":
            out_dir = script_dir
        else:
            out_dir = input_dir if input_dir else script_dir

    output_ttf = os.path.join(out_dir, OUTPUT_TTF)
    report_csv = os.path.join(out_dir, REPORT_CSV)
    report_txt = os.path.join(out_dir, REPORT_TXT)

    print("=" * 60)
    print("BailuKai-S One-Click Medium Builder (Deduplicated)")
    print("=" * 60)
    print("Input :", input_file)
    print("Output:", output_ttf)
    print(f"Weight: +{weight_val} CJK (contour expansion +{weight_val/2:.1f}, perfectly matching LXGW Medium)")
    print("")

    font = None

    try:
        # 1. Open font
        font = fontforge.open(input_file)
        print("[1/5] Original font opened")
        print("      Family :", font.familyname)
        print("      Fullname:", font.fullname)

        # Collect metrics before transformation
        original = collect_metrics(font)
        print("      CJK glyphs analyzed:", len(original))

        # 2. Global emboldening (+weight_val CJK, strictly deduplicated by unique glyphname)
        print(f"[2/5] Applying global +{weight_val} CJK weight expansion (deduplicated by glyph)")
        font.selection.none()

        fragile_glyphnames = set()
        for ch in FRAGILE_GLYPHS:
            cp = ord(ch)
            if cp in font:
                fragile_glyphnames.add(font[cp].glyphname)

        seen_glyphs = set()
        for g in font.glyphs():
            name = g.glyphname
            if name not in seen_glyphs:
                seen_glyphs.add(name)
                if name not in fragile_glyphnames:
                    font.selection.select(("more",), name)
                else:
                    print(f"      Excluding fragile glyph '{name}' from global changeWeight")

        print(f"      Selected {len(seen_glyphs) - len(fragile_glyphnames)} unique glyphs for changeWeight")
        font.changeWeight(weight_val, "CJK", 0, 0, "auto")

        # 2b. Inject pristine reference Medium contours for fragile glyphs
        search_dirs = [
            os.path.join(script_dir, "reference"),
            os.path.join(os.getcwd(), "reference"),
            os.path.join(out_dir, "reference"),
            os.path.join(input_dir, "reference"),
            input_dir,
            out_dir,
            script_dir,
            os.getcwd(),
        ]
        ref_font_path = find_reference_font(search_dirs)
        if ref_font_path:
            print(f"      Injecting clean Medium contours from reference: {os.path.basename(ref_font_path)}")
            ref_font = fontforge.open(ref_font_path)
            for ch in FRAGILE_GLYPHS:
                cp = ord(ch)
                if cp in ref_font and cp in font:
                    orig_vwidth = font[cp].vwidth
                    ref_font.selection.select(cp)
                    ref_font.copy()
                    font.selection.select(cp)
                    font.paste()
                    if orig_vwidth is not None and orig_vwidth > 0:
                        font[cp].vwidth = orig_vwidth
                    print(f"      Successfully injected clean Medium '{ch}' (U+{cp:04X})")
                else:
                    print(f"      WARNING: '{ch}' (U+{cp:04X}) not found in reference font")
            ref_font.close()
        else:
            print("      WARNING: Reference Medium font not found; fragile glyphs could not be injected")

        # 3. Apply optical corrections if configured
        if OPTICAL_CORRECTIONS:
            print("[3/5] Applying optical corrections")
            for name, amount in OPTICAL_CORRECTIONS.items():
                glyph = get_glyph_by_char(font, name)
                if glyph is None:
                    continue
                print("      {} U+{:04X} -> {:+d}".format(name, ord(name), amount))
                glyph.changeWeight(amount, "CJK", 0, 0, "auto")
        else:
            print("[3/5] Optical corrections: baseline clean (deduplication eliminates duplicate expansion)")

        # 4. Set Metadata
        print("[4/5] Setting Medium metadata & sfnt_names")
        font.familyname = FAMILY_NAME
        font.fullname = FULL_NAME
        font.fontname = POSTSCRIPT_NAME
        font.copyright = COPYRIGHT
        try:
            font.version = VERSION.replace("Version ", "")
        except Exception:
            pass
        try:
            font.weight = "Medium"
        except Exception:
            pass
        try:
            font.os2_weight = 500
        except Exception:
            pass
        try:
            font.os2_vendor = "huth"
        except Exception:
            pass

        # Update all localization name records in sfnt_names table
        try:
            new_sfnt = []
            seen_keys = set()
            for lang, name, val in font.sfnt_names:
                seen_keys.add((lang, name))
                if name in ("Family", "Preferred Family"):
                    if "PRC" in lang or "Singapore" in lang:
                        new_sfnt.append((lang, name, CHINESE_SIMP_FAMILY_NAME))
                    elif "Chinese" in lang:
                        new_sfnt.append((lang, name, CHINESE_TRAD_FAMILY_NAME))
                    else:
                        new_sfnt.append((lang, name, FAMILY_NAME))
                elif name in ("SubFamily", "Preferred Styles"):
                    new_sfnt.append((lang, name, SUBFAMILY_NAME))
                elif name == "Fullname":
                    if "PRC" in lang or "Singapore" in lang:
                        new_sfnt.append((lang, name, CHINESE_SIMP_FULL_NAME))
                    elif "Chinese" in lang:
                        new_sfnt.append((lang, name, CHINESE_TRAD_FULL_NAME))
                    else:
                        new_sfnt.append((lang, name, FULL_NAME))
                elif name == "PostScriptName":
                    new_sfnt.append((lang, name, POSTSCRIPT_NAME))
                elif name == "UniqueID":
                    new_sfnt.append((lang, name, UNIQUE_ID))
                elif name == "Copyright":
                    new_sfnt.append((lang, name, COPYRIGHT))
                elif name == "Manufacturer":
                    new_sfnt.append((lang, name, "huthief"))
                elif name == "Vendor URL":
                    new_sfnt.append((lang, name, VENDOR_URL))
                elif name == "Designer URL":
                    new_sfnt.append((lang, name, DESIGNER_URL))
                elif name == "License":
                    new_sfnt.append((lang, name, LICENSE))
                elif name == "License URL":
                    new_sfnt.append((lang, name, LICENSE_URL))
                elif name == "Version":
                    new_sfnt.append((lang, name, VERSION))
                else:
                    new_sfnt.append((lang, name, val))

            # Ensure critical keys exist for English (US) and Chinese locales
            critical_keys = [
                ("English (US)", "Copyright", COPYRIGHT),
                ("English (US)", "Manufacturer", "huthief"),
                ("English (US)", "Vendor URL", VENDOR_URL),
                ("English (US)", "Designer URL", DESIGNER_URL),
                ("English (US)", "License", LICENSE),
                ("English (US)", "License URL", LICENSE_URL),
                ("English (US)", "UniqueID", UNIQUE_ID),
                ("English (US)", "Version", VERSION),
                ("English (US)", "Preferred Family", FAMILY_NAME),
                ("English (US)", "Preferred Styles", SUBFAMILY_NAME),
                ("Chinese (Taiwan)", "Family", CHINESE_TRAD_FAMILY_NAME),
                ("Chinese (Taiwan)", "SubFamily", SUBFAMILY_NAME),
                ("Chinese (Taiwan)", "Fullname", CHINESE_TRAD_FULL_NAME),
                ("Chinese (Taiwan)", "Preferred Family", CHINESE_TRAD_FAMILY_NAME),
                ("Chinese (Taiwan)", "Preferred Styles", SUBFAMILY_NAME),
                ("Chinese (PRC)", "Family", CHINESE_SIMP_FAMILY_NAME),
                ("Chinese (PRC)", "SubFamily", SUBFAMILY_NAME),
                ("Chinese (PRC)", "Fullname", CHINESE_SIMP_FULL_NAME),
                ("Chinese (PRC)", "Preferred Family", CHINESE_SIMP_FAMILY_NAME),
                ("Chinese (PRC)", "Preferred Styles", SUBFAMILY_NAME),
            ]
            for lang, name, val in critical_keys:
                if (lang, name) not in seen_keys:
                    new_sfnt.append((lang, name, val))

            font.sfnt_names = tuple(new_sfnt)
            print("      Updated sfnt_names table across all languages")
        except Exception as e:
            print(f"      Warning updating sfnt_names: {e}")

        # Candidate metrics analysis
        results = []
        for g in font.glyphs():
            try:
                cp = g.unicode
                if cp not in original:
                    continue

                old = original[cp]
                new = {
                    "char": old["char"],
                    "bbox": bbox(g),
                    "contours": contour_count(g),
                    "points": point_count(g),
                }

                score, level, ag, wg, hg, reasons = score_candidate(old, new)

                results.append({
                    "char": old["char"],
                    "unicode": "U+{:04X}".format(cp),
                    "codepoint": cp,
                    "level": level,
                    "score": round(score, 2),
                    "area_growth": round(ag, 2),
                    "width_growth": round(wg, 2),
                    "height_growth": round(hg, 2),
                    "old_contours": old["contours"],
                    "new_contours": new["contours"],
                    "old_points": old["points"],
                    "new_points": new["points"],
                    "reasons": reasons,
                })

            except Exception:
                continue

        # 5. Generate TTF and Reports
        print("[5/5] Generating TTF and candidate reports")
        font.generate(output_ttf)
        print("      TTF:", output_ttf)

        write_reports(results, report_csv, report_txt, weight_val)
        print("      CSV:", report_csv)
        print("      TXT:", report_txt)

        print("")
        print("=" * 60)
        print("BUILD SUCCESSFUL: " + output_ttf)
        print("=" * 60)
        return 0

    except Exception:
        print("")
        print("BUILD FAILED: " + output_ttf)
        traceback.print_exc()
        return 1

    finally:
        if font is not None:
            try:
                font.close()
            except Exception:
                pass


def main():
    input_file = os.path.abspath(sys.argv[1]) if len(sys.argv) >= 2 else None
    weight_val = DEFAULT_WEIGHT
    if len(sys.argv) >= 3:
        try:
            weight_val = int(sys.argv[2])
        except ValueError:
            print(f"WARNING: Invalid weight argument '{sys.argv[2]}', using default {DEFAULT_WEIGHT}")
            weight_val = DEFAULT_WEIGHT

    return build(input_file=input_file, weight_val=weight_val)


if __name__ == "__main__":
    sys.exit(main())

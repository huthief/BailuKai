---
name: cjk-font-medium-builder
description: Use when building Medium-weight fonts from CJK base fonts (such as GuanKiapTsingKhai or BailuKai variants), including horizontal variants (-S, -T, -TW, -W), pseudo-vertical 90-degree rotated variants (-90, -S-90, -T-90, -TW-90, -W-90), batch font builds, or applying deduplicated emboldening with fragile glyph repairs.
---

# CJK Medium 字型產製技能 (CJK Font Medium Builder)

## Overview

本技能提供一套標準化的 CJK（中日韓）字型 **Medium（中黑）加重產製流程**。核心技術採用 **字符去重幾何輪廓膨脹（Deduplicated Glyph Emboldening）**，搭配 **密集易碎字符對照注入修復** 與 **偽直排 90 度仿射旋轉對齊**，徹底避免 FontForge 原生多重編碼（Multi-encoded）重覆加粗問題（如康熙部首重疊導致之異常加粗破面與刺鬚虛影）。

當使用者想要產製新字型時，本技能引導代理人精準識別使用情境、確認參數，並調用對應的建置管線。

---

## 情境矩陣 (Scenario Matrix)

產製 CJK Medium 字型時，首先根據需求定位所屬情境：

| 情境代號 | 情境名稱 | 適用場景 | 基底輸入底本 (`reference/`) | 預設產出目標 |
| :--- | :--- | :--- | :--- | :--- |
| **`std-horiz`** | **標準橫排中黑版** | 繁體正楷標準排版、標題印刷、高解析螢幕閱覽 | `GuanKiapTsingKhai.ttf` | `BailuKai-Medium.ttf` |
| **`std-vert`** | **標準偽直排中黑版** | 電子書閱讀器（Kobo, Kindle, Boox 等）全字集直排閱覽 | `GuanKiapTsingKhai-90.ttf` | `BailuKai-Medium-90.ttf` |
| **`var-horiz`** | **簡轉繁橫排變體** | 依特定規範轉換之橫排字型（可選 `-S`, `-T`, `-TW`, `-W`） | `GuanKiapTsingKhai-[VAR].ttf` | `BailuKai-Medium-[VAR].ttf` |
| **`var-vert`** | **簡轉繁偽直排變體** | 依特定規範轉換之直排字型（可選 `-S-90`, `-T-90`, `-TW-90`, `-W-90`） | `GuanKiapTsingKhai-[VAR]-90.ttf` | `BailuKai-Medium-[VAR]-90.ttf` |
| **`batch-horiz`** | **一鍵批量橫排全體** | 同時產製全部 4 款簡轉繁橫排變體 | 全部 4 款橫排底本 | `BailuKai-Medium-{S,T,TW,W}.ttf` |
| **`batch-vert`** | **一鍵批量直排全體** | 同時產製全部 4 款簡轉繁偽直排變體 | 全部 4 款直排底本 | `BailuKai-Medium-{S,T,TW,W}-90.ttf` |
| **`batch-all`** | **一鍵全系列建置** | 同時產製全系列 8 款變體 | 全部 8 款底本 | 全系列 8 款 `.ttf` |
| **`custom`** | **自訂字型加粗建置** | 全新第三方 CJK 字型加粗或非標準加粗權重 | 自訂輸入 `.ttf` | 自訂檔名與元資料 |

---

## 互動情境引導流程 (Interactive Scenario Selection)

當使用者發起字型產製需求但未指定具體變體或情境時，**必須主動向使用者確認情境**（若有 `ask_question` 工具，應優先使用結構化多選/單選互動對話框）：

### 互動問題設計規範

```json
{
  "question": "請問您想以哪一種情境產製 Medium 字型？",
  "options": [
    "(Recommended) 臺灣繁體偽直排版（TW-90，適用於電子書直排閱讀）",
    "臺灣繁體標準橫排版（TW，適用於正體橫排閱讀與印刷）",
    "標準偽直排版（-90，電子書全字集通用版）",
    "一鍵批量產製所有偽直排變體（all-90：S-90, T-90, TW-90, W-90）",
    "一鍵批量產製全系列 8 款變體（everything）",
    "自訂全新來源字型或自訂加粗權重"
  ]
}
```

---

## 執行步驟指南 (Step-by-Step Guide)

### 步驟 1：環境與底本檢查 (Pre-flight Inspection)

1. **FontForge 執行路徑**：
   - 檢查系統 PATH 是否有 `fontforge`。
   - 在 Windows 環境下，優先尋找 `C:\Program Files\FontForgeBuilds\bin\fontforge.exe` 或 `C:\Program Files\FontForgeBuilds\fontforge.bat`。
2. **底本資源檢查 (`reference/`)**：
   - 對照情境矩陣，確認該情境所需之底本檔案已放置於 `reference/`。
   - 確認對照修復字型（如 `reference/霞鶩文楷LXGWWenKaiTC-Medium.ttf`）存在。

### 步驟 2：執行對應建置指令

根據使用者選定之情境，執行對應指令（以 PowerShell 為例）：

#### 情境 A：單一橫排變體
```powershell
& "C:\Program Files\FontForgeBuilds\bin\fontforge.exe" -lang=py -script BailuKai_build_medium-[VAR].py
# 範例：臺灣繁體橫排
& "C:\Program Files\FontForgeBuilds\bin\fontforge.exe" -lang=py -script BailuKai_build_medium-TW.py
```

#### 情境 B：單一偽直排變體（-90）
```powershell
& "C:\Program Files\FontForgeBuilds\bin\fontforge.exe" -lang=py -script BailuKai_build_medium-[VAR]-90.py
# 範例：臺灣繁體偽直排
& "C:\Program Files\FontForgeBuilds\bin\fontforge.exe" -lang=py -script BailuKai_build_medium-TW-90.py
```

#### 情境 C：一鍵批量建置 (`BailuKai_build_medium_all.py`)
```powershell
# 批量產製所有橫排 4 變體 (S, T, TW, W)
& "C:\Program Files\FontForgeBuilds\bin\fontforge.exe" -lang=py -script BailuKai_build_medium_all.py all

# 批量產製所有偽直排 4 變體 (S-90, T-90, TW-90, W-90)
& "C:\Program Files\FontForgeBuilds\bin\fontforge.exe" -lang=py -script BailuKai_build_medium_all.py all-90

# 批量產製全系列 8 款變體
& "C:\Program Files\FontForgeBuilds\bin\fontforge.exe" -lang=py -script BailuKai_build_medium_all.py everything
```

#### 情境 D：自訂字型加粗建置
若為自訂字型或需要指定權重：
```powershell
# 指定特定變體與加粗權重 (預設 12 = +6 單邊膨脹)
& "C:\Program Files\FontForgeBuilds\bin\fontforge.exe" -lang=py -script BailuKai_build_medium_all.py TW-90 14
```

---

## 核心技術規範與程式碼模式 (Core Technical Patterns)

### 1. 字符去重加粗演算法 (Deduplicated Emboldening)

**陷阱**：直接使用 `font.selection.all()` 是依 Unicode 編碼選取。若同一個字形對應多個編碼槽位（如 CJK 統一漢字與康熙部首 U+2F00..U+2FD5 重複映射），該字會被重覆加粗 2 次以上，導致嚴重的刺鬚、破面或局部字身暴肥。

**正解模式**：
```python
# 嚴格按 Glyph 物件去重，確保全字型輪廓僅加粗一次
processed_glyphs = set()
for g in font.glyphs():
    if g.glyphname in processed_glyphs:
        continue
    processed_glyphs.add(g.glyphname)
    
    # 排除易碎字形（稍後注入對照輪廓）
    if g.unicode in FRAGILE_UNICODES:
        continue
        
    # 執行幾何單邊等距擴張 (weight=12 相當於輪廓擴張 +6)
    g.changeWeight(12)
```

### 2. 偽直排旋轉仿射變換與度量重設 (Pseudo-Vertical Transform)

針對直排模式下需要旋轉 90 度之易碎注入字（如「傳」、「導」、「育」），需嚴格使用仿射變換矩陣與度量設定：

```python
# 逆時針旋轉 90 度仿射矩陣：(0, 1, -1, 0, 880, -120)
# 變換公式：x' = -y + 880, y' = x - 120
ref_glyph.transform((0, 1, -1, 0, 880, -120))
ref_glyph.width = 1000
ref_glyph.vwidth = 1120
```

### 3. 多語系元資料與 OFL 1.1 宣告

字型元資料必須在 `sfnt_names` 中登錄繁簡雙語系：
- 繁體語系代碼（`Chinese (Taiwan)`, `Chinese (Hong Kong)`, `Chinese (Macau)`）：使用 `白鷺楷-*`
- 簡體語系代碼（`Chinese (PRC)`, `Chinese (Singapore)`）：使用 `白鹭楷-*`
- OS/2 WeightClass 統一設為 `500` (Medium)。
- 保留上游字型著作權與 SIL Open Font License 1.1 聲明。

---

## 品質驗收檢核表 (Verification Checklist)

產製完成後，執行以下檢核確認品質無誤：

- [ ] **檔案存在與非零大小**：產出之 `.ttf` 檔案大小應介於 10MB ~ 15MB 之間。
- [ ] **品質候選字報告核查**：
  - 檢查同名產出之 `-Candidates.csv` 與 `-Candidates.txt`。
  - 確認是否有不可接受之 Level A（強烈膨脹或異常擴張）字形破面。
- [ ] **多重編碼代表字檢測**：
  - 抽檢「十」、「一」、「方」、「生」、「長」、「見」、「馬」等康熙部首重複映射字，確認筆畫未遭二次膨脹。
- [ ] **易碎字符輪廓檢測**：
  - 檢視「傳」、「導」、「育」輪廓是否平整，直排版中角度與字距是否與周圍字符中心對齊。
- [ ] **元資料校驗**：
  - 驗證 PostScript Name、Family Name、WeightClass (`500`) 及 OFL 1.1 授權標籤正確寫入。

---

## 常見錯誤與排除 (Common Pitfalls)

| 錯誤現象 | 根本原因 | 排除作法 |
| :--- | :--- | :--- |
| 「十」、「一」、「長」異常粗大，筆畫打結出現黑點 | 使用了 `font.selection.all()` 重複遍歷多重編碼 | 改用 `font.glyphs()` 並以 `glyphname` 去重，每字符僅執行一次 `changeWeight` |
| 執行時報錯 `fontforge: command not found` | Windows 環境變數 PATH 未包含 FontForge 路徑 | 改用完整路徑呼叫，例如 `& "C:\Program Files\FontForgeBuilds\bin\fontforge.exe"` |
| 偽直排字型在閱讀器中「傳/導/育」方向顛倒或偏移 | 輪廓注入時未施加仿射矩陣或維度設錯 | 注入前套用 PostScript 矩陣 `(0, 1, -1, 0, 880, -120)` 並重設 `width=1000` |
| 簡中系統顯示字型名稱為亂碼或英文 | `sfnt_names` 漏設簡體中文（PRC / Singapore）語言標籤 | 於 `sfnt_names` 補齊 `Chinese (PRC)` 對應之繁/簡字型名稱字串 |

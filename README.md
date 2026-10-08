# 白鷺楷 (BailuKai)

> 一款基於「原俠正楷」為基底，透過 FontForge 自動化演算法精準增粗的中黑（Medium）字重開放原始碼繁體楷書字型。
> 
> **最新版本**：對應原俠正楷 **v1.20** 版本製作。

---

## 字型下載 (Releases)

本專案之建置成果字型檔採 **Release 發行版** 方式提供下載，Git 儲存庫中不收錄任何 `.ttf` 二進位字型檔：

- **Release 版本標籤**：[`20260928`](https://git.jigong.org/huthief/BailuKai/releases/tag/20260928)
- **發行檔案**：
  - `BailuKai-Medium.ttf`：標準橫排中黑字型。
  - `BailuKai-Medium-90.ttf`：標準偽直排中黑字型（專為電子書閱讀器直排閱覽設計）。
  - `BailuKai-Medium-S.ttf` / `BailuKai-Medium-S-90.ttf`：簡轉繁 -S 變體（橫排 / 偽直排）。
  - `BailuKai-Medium-T.ttf` / `BailuKai-Medium-T-90.ttf`：簡轉繁 -T 變體（橫排 / 偽直排）。
  - `BailuKai-Medium-TW.ttf` / `BailuKai-Medium-TW-90.ttf`：簡轉繁 -TW 變體（橫排 / 偽直排）。
  - `BailuKai-Medium-W.ttf` / `BailuKai-Medium-W-90.ttf`：簡轉繁 -W 變體（橫排 / 偽直排）。

---

## 專案緣起與目標

原俠正楷（GuanKiapTsingKhai）預設為標準 Regular 字重，在標題排版、印刷標註或高解析度螢幕閱讀時略顯偏細。**白鷺楷（BailuKai Medium）** 旨在提供穩定、清晰且骨架勻稱的 Medium 字重楷體。透過專屬設計的 Python 建置流水線，在 FontForge 中對字形輪廓進行等距增粗（`changeWeight(12)`，相當於筆畫單邊 +6 輪廓膨脹），使其視覺字重與「霞鶩文楷 Medium」達到高度一致性。

---

## 核心技術特色

### 1. 字符去重加粗演算法（Deduplicated Glyph Emboldening）
- **痛點根治**：FontForge 預設的 `selection.all()` 是依「編碼槽位」（Codepoints）選取而非「字形物件」（Glyphs）。在原俠正楷（v1.20）中，有 285 個字形存在多重編碼（同時映射至 CJK 統一表意文字與康熙部首 U+2F00..U+2FD5 等區間）。若未去重，這些字會被重覆施加加粗演算法（變為 +24），導致比其他字符粗上 15%~20%。
- **修復成果**：
  - 徹底解決「十、一、方、生、日、而、玉、又、馬、見、面、金、高、老、士、心、血」等常見字異常過粗的問題。
  - 徹底解決「長」字底部筆畫自交（Self-intersecting loop）以及在下方產生雜散刺鬚破面（虛影）之現象。
  - 確保字庫中每一個獨立字形在全字庫中**嚴格僅執行一次**增粗變換。

### 2. 脆弱字形無損修復注入（Reference Contour Injection）
- 部分筆畫極為密集的複雜字形（如「傳」、「導」、「育」等），直接進行演算法幾何增粗時容易發生筆畫黏連或輪廓扭曲。
- 建置腳本會將此類易碎字元自全域粗化程序中排除，並自動由高品質對照字型（霞鶩文楷 Medium）中無損擷取乾淨平滑的 Medium 輪廓注入目標字庫，兼顧字型的一致性與美觀。

### 3. 自動化品質檢測與候選字風險分析報表
- 建置過程中會即時對比轉換前後的邊界框（Bounding Box）面積成長率、寬高膨脹率、輪廓數與點數，自動生成候選字分析評分：
  - **Level A（高風險）**：強烈膨脹或異常擴張字元。
  - **Level B / C（中低風險）**：微調或常態筆畫增厚字元。
  - **Level D（常態）**：正常轉換字元。
- 自動產出候選字品質分析報表（`.csv` 與 `.txt`）以供進一步審閱校對。

### 4. 偽直排字型支援與幾何旋轉對齊（Pseudo-Vertical -90 Support）
- **電子書直排適配**：專為電子書閱讀器（如 Kobo、Boox、Kindle 等軟硬體）設計，解決系統原生直排字型不全或不支援原生直排標籤之排版需求。所有 CJK 字符均圍繞字身中心逆時針旋轉 90 度（仿射變換：$x' = -y + 880,\; y' = x - 120$）。
- **脆弱字形自動旋轉注入**：針對易碎字元（「傳」、「導」、「育」），腳本自參考字型（霞鶩文楷 Medium）複製後，自動施加 PostScript 變換矩陣 `(0, 1, -1, 0, 880, -120)` 並校正度量寬高（`width=1000, vwidth=1120`），確保在直排環境下完全對齊、毫無破綻。

---

## 目錄結構

```text
BailuKai/
├── BailuKai_build_medium.py       # 標準版 FontForge 自動化建置腳本
├── BailuKai_build_medium-90.py    # 偽直排（-90）FontForge 自動化建置腳本
├── BailuKai_build_medium-S.py     # 簡轉繁 -S 變體建置腳本
├── BailuKai_build_medium-S-90.py  # 簡轉繁 -S-90 偽直排變體建置腳本
├── BailuKai_build_medium-T.py     # 簡轉繁 -T 變體建置腳本
├── BailuKai_build_medium-T-90.py  # 簡轉繁 -T-90 偽直排變體建置腳本
├── BailuKai_build_medium-TW.py    # 簡轉繁 -TW 變體建置腳本
├── BailuKai_build_medium-TW-90.py # 簡轉繁 -TW-90 偽直排變體建置腳本
├── BailuKai_build_medium-W.py     # 簡轉繁 -W 變體建置腳本
├── BailuKai_build_medium-W-90.py  # 簡轉繁 -W-90 偽直排變體建置腳本
├── BailuKai_build_medium_all.py   # 全變體一鍵批次建置腳本（支援標準版與 -90 版）
├── reference/                     # 參考與來源底本字型放置目錄（不存放實際字型檔）
│   └── .gitkeep
├── .gitignore                     # Git 忽略設定（過濾 *.ttf 等字型檔）
└── README.md                      # 專案說明文件
```

---

## 參考用字型檔準備 (Reference Fonts Setup)

為了遵循授權並維持儲存庫輕量化，`reference/` 目錄下**不收錄任何實際字型檔案**。在執行建置腳本前，請自行下載下列參考字型，並依規定之檔名放置於 `reference/` 目錄中：

| 角色 | 字型名稱與版本 | 下載來源 | 放置檔名規則 |
| :--- | :--- | :--- | :--- |
| **標準版基底字型** | **原俠正楷 (v1.20)** | [GitHub: tonyhuan/GuanKiapTsingKhai](https://github.com/tonyhuan/GuanKiapTsingKhai) (請於 Release 下載 `GuanKiapTsingKhai.ttf`) | `reference/GuanKiapTsingKhai.ttf`<br>*(或 `reference/原俠正楷GuanKiapTsingKhai.ttf`)* |
| **偽直排基底字型** | **原俠正楷-90 (v1.20)** | [GitHub: tonyhuan/GuanKiapTsingKhai](https://github.com/tonyhuan/GuanKiapTsingKhai) (請於 Release 下載 `GuanKiapTsingKhai-90.ttf`) | `reference/GuanKiapTsingKhai-90.ttf`<br>*(或 `reference/原俠正楷GuanKiapTsingKhai-90.ttf`)* |
| **簡轉繁 -S 基底字型** | **原俠正楷-S (v1.20)** | 同上（下載 `GuanKiapTsingKhai-S.ttf`） | `reference/GuanKiapTsingKhai-S.ttf` |
| **簡轉繁 -S-90 基底字型** | **原俠正楷-S-90 (v1.20)** | 同上（下載 `GuanKiapTsingKhai-S-90.ttf`） | `reference/GuanKiapTsingKhai-S-90.ttf` |
| **簡轉繁 -T 基底字型** | **原俠正楷-T (v1.20)** | 同上（下載 `GuanKiapTsingKhai-T.ttf`） | `reference/GuanKiapTsingKhai-T.ttf` |
| **簡轉繁 -T-90 基底字型** | **原俠正楷-T-90 (v1.20)** | 同上（下載 `GuanKiapTsingKhai-T-90.ttf`） | `reference/GuanKiapTsingKhai-T-90.ttf` |
| **簡轉繁 -TW 基底字型** | **原俠正楷-TW (v1.20)** | 同上（下載 `GuanKiapTsingKhai-TW.ttf`） | `reference/GuanKiapTsingKhai-TW.ttf` |
| **簡轉繁 -TW-90 基底字型** | **原俠正楷-TW-90 (v1.20)** | 同上（下載 `GuanKiapTsingKhai-TW-90.ttf`） | `reference/GuanKiapTsingKhai-TW-90.ttf` |
| **簡轉繁 -W 基底字型** | **原俠正楷-W (v1.20)** | 同上（下載 `GuanKiapTsingKhai-W.ttf`） | `reference/GuanKiapTsingKhai-W.ttf` |
| **簡轉繁 -W-90 基底字型** | **原俠正楷-W-90 (v1.20)** | 同上（下載 `GuanKiapTsingKhai-W-90.ttf`） | `reference/GuanKiapTsingKhai-W-90.ttf` |
| **參考注入字型** | **霞鶩文楷 TC (Medium)** | [GitHub: lxgw/lxgwwenkaitc](https://github.com/lxgw/lxgwwenkaitc) (請下載 Medium 字重 TTF) | `reference/霞鶩文楷LXGWWenKaiTC-Medium.ttf`<br>*(或 `reference/LXGWWenKaiTC-Medium.ttf`)* |

---

## 建置指引 (Build Instructions)

### 環境需求
- [FontForge](https://fontforge.org/)（需支援 Python 擴充腳本功能）
- Python 3.x（通常隨 FontForge 安裝提供）

### 1. 標準版建置 (BailuKai-Medium.ttf)
完成參考字型準備後，在專案根目錄下執行：

```bash
fontforge -lang=py -script BailuKai_build_medium.py
```

> **提示**：未指定參數時，腳本將自動以 `reference/GuanKiapTsingKhai.ttf` 為基底來源輸入，並於 `reference/` 尋找霞鶩文楷進行修復注入，最終產生的 `BailuKai-Medium.ttf` 會輸出至專案根目錄。亦可透過參數手動指定輸入路徑或加粗權重：
> ```bash
> fontforge -lang=py -script BailuKai_build_medium.py [輸入字型.ttf] [加粗權重(預設12)]
> ```

### 2. 偽直排版建置 (BailuKai-Medium-90.ttf)
完成參考字型準備後，在專案根目錄下執行：

```bash
fontforge -lang=py -script BailuKai_build_medium-90.py
```

> **提示**：未指定參數時，腳本將自動以 `reference/GuanKiapTsingKhai-90.ttf`（或 `reference/原俠正楷GuanKiapTsingKhai-90.ttf`）為基底來源輸入，自動處理易碎字符旋轉注入與各項直排度量，最終產生的 `BailuKai-Medium-90.ttf`、`BailuKai-Medium-90-Candidates.csv` 與 `BailuKai-Medium-90-Candidates.txt` 會輸出至專案根目錄。亦可手動指定輸入檔案：
> ```bash
> fontforge -lang=py -script BailuKai_build_medium-90.py [輸入字型.ttf] [加粗權重(預設12)]
> ```

### 3. 簡轉繁各變體建置 (-S, -T, -TW, -W)

可依需求針對各獨立變體進行建置：

```bash
# 建置 -S 變體 (BailuKai-Medium-S.ttf)
fontforge -lang=py -script BailuKai_build_medium-S.py

# 建置 -T 變體 (BailuKai-Medium-T.ttf)
fontforge -lang=py -script BailuKai_build_medium-T.py

# 建置 -TW 變體 (BailuKai-Medium-TW.ttf)
fontforge -lang=py -script BailuKai_build_medium-TW.py

# 建置 -W 變體 (BailuKai-Medium-W.ttf)
fontforge -lang=py -script BailuKai_build_medium-W.py
```

### 4. 偽直排簡轉繁各變體建置 (-S-90, -T-90, -TW-90, -W-90)

可依需求針對偽直排各獨立變體進行建置：

```bash
# 建置 -S-90 變體 (BailuKai-Medium-S-90.ttf)
fontforge -lang=py -script BailuKai_build_medium-S-90.py

# 建置 -T-90 變體 (BailuKai-Medium-T-90.ttf)
fontforge -lang=py -script BailuKai_build_medium-T-90.py

# 建置 -TW-90 變體 (BailuKai-Medium-TW-90.ttf)
fontforge -lang=py -script BailuKai_build_medium-TW-90.py

# 建置 -W-90 變體 (BailuKai-Medium-W-90.ttf)
fontforge -lang=py -script BailuKai_build_medium-W-90.py
```

### 5. 一鍵批量建置 (Batch Builder)

使用全變體批次腳本一鍵編譯所有變體：

```bash
# 一鍵編譯所有橫排變體 (S, T, TW, W)
fontforge -lang=py -script BailuKai_build_medium_all.py all

# 一鍵編譯所有偽直排變體 (S-90, T-90, TW-90, W-90)
fontforge -lang=py -script BailuKai_build_medium_all.py all-90

# 一鍵編譯全系列所有 8 款變體
fontforge -lang=py -script BailuKai_build_medium_all.py everything

# 或指定特定變體與加粗權重
fontforge -lang=py -script BailuKai_build_medium_all.py TW-90 12
```

---

## 字型元資料 (Font Metadata)

### 橫排系列 (Horizontal Series)

| 欄位 (Property) | 標準版 | -S 變體 | -T 變體 | -TW 變體 | -W 變體 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **產出檔案** | `BailuKai-Medium.ttf` | `BailuKai-Medium-S.ttf` | `BailuKai-Medium-T.ttf` | `BailuKai-Medium-TW.ttf` | `BailuKai-Medium-W.ttf` |
| **Family Name (EN)** | `BailuKai` | `BailuKai-S` | `BailuKai-T` | `BailuKai-TW` | `BailuKai-W` |
| **Family Name (繁中)** | `白鷺楷` | `白鷺楷-S` | `白鷺楷-T` | `白鷺楷-TW` | `白鷺楷-W` |
| **Family Name (簡中)** | `白鷺楷` | `白鹭楷-S` | `白鹭楷-T` | `白鹭楷-TW` | `白鹭楷-W` |
| **SubFamily** | `Medium` | `Medium` | `Medium` | `Medium` | `Medium` |
| **Full Name (EN)** | `BailuKai Medium` | `BailuKai-S Medium` | `BailuKai-T Medium` | `BailuKai-TW Medium` | `BailuKai-W Medium` |
| **PostScript Name** | `BailuKai-Medium` | `BailuKai-S-Medium` | `BailuKai-T-Medium` | `BailuKai-TW-Medium` | `BailuKai-W-Medium` |
| **OS/2 Weight Class** | `500` (Medium) | `500` (Medium) | `500` (Medium) | `500` (Medium) | `500` (Medium) |
| **UniqueID** | `BailuKai Medium; Version 20260928` | `BailuKai-S Medium; Version 20260928` | `BailuKai-T Medium; Version 20260928` | `BailuKai-TW Medium; Version 20260928` | `BailuKai-W Medium; Version 20260928` |
| **Copyright** | `Copyright 2026 huthief` | `Copyright 2026 huthief` | `Copyright 2026 huthief` | `Copyright 2026 huthief` | `Copyright 2026 huthief` |
| **License** | SIL OFL 1.1 | SIL OFL 1.1 | SIL OFL 1.1 | SIL OFL 1.1 | SIL OFL 1.1 |
| **URL** | `https://github.com/huthief/BailuKai` | `https://github.com/huthief/BailuKai` | `https://github.com/huthief/BailuKai` | `https://github.com/huthief/BailuKai` | `https://github.com/huthief/BailuKai` |

### 偽直排系列 (Pseudo-Vertical -90 Series)

| 欄位 (Property) | 標準偽直排 (-90) | -S-90 變體 | -T-90 變體 | -TW-90 變體 | -W-90 變體 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **產出檔案** | `BailuKai-Medium-90.ttf` | `BailuKai-Medium-S-90.ttf` | `BailuKai-Medium-T-90.ttf` | `BailuKai-Medium-TW-90.ttf` | `BailuKai-Medium-W-90.ttf` |
| **Family Name (EN)** | `BailuKai-90` | `BailuKai-S-90` | `BailuKai-T-90` | `BailuKai-TW-90` | `BailuKai-W-90` |
| **Family Name (繁中)** | `白鷺楷-90` | `白鷺楷-S-90` | `白鷺楷-T-90` | `白鷺楷-TW-90` | `白鷺楷-W-90` |
| **Family Name (簡中)** | `白鷺楷-90` | `白鹭楷-S-90` | `白鹭楷-T-90` | `白鹭楷-TW-90` | `白鹭楷-W-90` |
| **SubFamily** | `Medium` | `Medium` | `Medium` | `Medium` | `Medium` |
| **Full Name (EN)** | `BailuKai-90 Medium` | `BailuKai-S-90 Medium` | `BailuKai-T-90 Medium` | `BailuKai-TW-90 Medium` | `BailuKai-W-90 Medium` |
| **PostScript Name** | `BailuKai-90-Medium` | `BailuKai-S-90-Medium` | `BailuKai-T-90-Medium` | `BailuKai-TW-90-Medium` | `BailuKai-W-90-Medium` |
| **OS/2 Weight Class** | `500` (Medium) | `500` (Medium) | `500` (Medium) | `500` (Medium) | `500` (Medium) |
| **UniqueID** | `BailuKai-90 Medium; Version 20260928` | `BailuKai-S-90 Medium; Version 20260928` | `BailuKai-T-90 Medium; Version 20260928` | `BailuKai-TW-90 Medium; Version 20260928` | `BailuKai-W-90 Medium; Version 20260928` |
| **Copyright** | `Copyright 2026 huthief` | `Copyright 2026 huthief` | `Copyright 2026 huthief` | `Copyright 2026 huthief` | `Copyright 2026 huthief` |
| **License** | SIL OFL 1.1 | SIL OFL 1.1 | SIL OFL 1.1 | SIL OFL 1.1 | SIL OFL 1.1 |
| **URL** | `https://github.com/huthief/BailuKai` | `https://github.com/huthief/BailuKai` | `https://github.com/huthief/BailuKai` | `https://github.com/huthief/BailuKai` | `https://github.com/huthief/BailuKai` |

---

## 來源字型與開源授權聲明 (Credits & Licenses)

本專案衍生自以下開源專案與公共資源：

1. **原俠正楷 (GuanKiapTsingKhai)**
   - 來源：[tonyhuan/GuanKiapTsingKhai](https://github.com/tonyhuan/GuanKiapTsingKhai)（作者：Tony Huan）
   - 對應版本：v1.20（含標準版、-90 偽直排版，以及 -S、-T、-TW、-W 簡轉繁變體）
   - 授權：遵循原俠正楷授權條款規範與 SIL Open Font License 1.1 保留字型名稱規定
2. **霞鶩文楷 TC (LXGW WenKai TC)**
   - 來源：[落霞孤鹜 (lxgw/lxgwwenkaitc)](https://github.com/lxgw/lxgwwenkaitc)
   - 授權：[SIL Open Font License 1.1 (OFL-1.1)](https://scripts.sil.org/OFL)
3. **白鷺楷 (BailuKai)**
   - 本專案自動化建置腳本及說明文件依據開源社群條款釋出。
   - 衍生字型保留各上游開源字型之授權條款要求。

## 授權

本字型以 SIL Open Font License 1.1 釋出，全文見 `OFL.txt`。
衍生自原俠正楷 v1.20（Tony Huang，OFL 1.1）。
部分易碎字形的輪廓參考霞鶩文楷 Medium（LXGW WenKai，OFL 1.1）。

# 白鷺楷 (BailuKai)

> 一款基於「原俠正楷」為基底，透過 FontForge 自動化演算法精準增粗的中黑（Medium）字重開放原始碼繁體楷書字型。
> 
> **最新版本**：對應原俠正楷 **v1.20** 版本製作。

---

## 字型下載 (Releases)

本專案之建置成果字型檔採 **Release 發行版** 方式提供下載，Git 儲存庫中不收錄任何 `.ttf` 二進位字型檔：

- **Release 版本標籤**：[`20260928`](https://git.jigong.org/huthief/BailuKai/releases/tag/20260928)
- **發行檔案**：`BailuKai-Medium.ttf`

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
- 自動產出 `BailuKai-Medium-Candidates.csv` 與 `BailuKai-Medium-Candidates.txt` 以供進一步審閱校對。

---

## 目錄結構

```text
BailuKai/
├── BailuKai_build_medium.py   # FontForge 自動化建置腳本
├── reference/                 # 參考與來源底本字型放置目錄（不存放實際字型檔）
│   └── .gitkeep
├── .gitignore                 # Git 忽略設定（過濾 *.ttf 等字型檔）
└── README.md                  # 專案說明文件
```

---

## 參考用字型檔準備 (Reference Fonts Setup)

為了遵循授權並維持儲存庫輕量化，`reference/` 目錄下**不收錄任何實際字型檔案**。在執行建置腳本前，請自行下載下列參考字型，並依規定之檔名放置於 `reference/` 目錄中：

| 角色 | 字型名稱與版本 | 下載來源 | 放置檔名規則 |
| :--- | :--- | :--- | :--- |
| **基底字型** | **原俠正楷 (v1.20)** | [GitHub: tonyhuan/GuanKiapTsingKhai](https://github.com/tonyhuan/GuanKiapTsingKhai) (請於 Release 下載 `GuanKiapTsingKhai.ttf`) | `reference/GuanKiapTsingKhai.ttf` |
| **參考注入字型** | **霞鶩文楷 TC (Medium)** | [GitHub: lxgw/lxgwwenkaitc](https://github.com/lxgw/lxgwwenkaitc) (請下載 Medium 字重 TTF) | `reference/霞鶩文楷LXGWWenKaiTC-Medium.ttf`<br>*(或 `reference/LXGWWenKaiTC-Medium.ttf`)* |

---

## 建置指引 (Build Instructions)

### 環境需求
- [FontForge](https://fontforge.org/)（需支援 Python 擴充腳本功能）
- Python 3.x（通常隨 FontForge 安裝提供）

### 一鍵建置
完成「參考用字型檔準備」後，在專案根目錄下直接執行：

```bash
fontforge -lang=py -script BailuKai_build_medium.py
```

> **提示**：未指定參數時，腳本將自動以 `reference/GuanKiapTsingKhai.ttf` 為基底來源輸入，並於 `reference/` 尋找霞鶩文楷進行修復注入，最終產生的 `BailuKai-Medium.ttf` 會輸出至專案根目錄。

### 自訂參數建置
若需手動指定輸入檔案路徑或加粗權重：

```bash
fontforge -lang=py -script BailuKai_build_medium.py [輸入字型.ttf] [加粗權重(預設12)]
```

範例：
```bash
fontforge -lang=py -script BailuKai_build_medium.py reference/GuanKiapTsingKhai.ttf 12
```

---

## 字型元資料 (Font Metadata)

| 欄位 (Property) | 設定值 (Value) |
| :--- | :--- |
| **Family Name** | `BailuKai` |
| **SubFamily** | `Medium` |
| **Full Name** | `BailuKai Medium` |
| **PostScript Name** | `BailuKai-Medium` |
| **OS/2 Weight Class** | `500` (Medium) |

---

## 來源字型與開源授權聲明 (Credits & Licenses)

本專案衍生自以下開源專案與公共資源：

1. **原俠正楷 (GuanKiapTsingKhai)**
   - 來源：[tonyhuan/GuanKiapTsingKhai](https://github.com/tonyhuan/GuanKiapTsingKhai)（作者：Tony Huan）
   - 對應版本：v1.20
   - 授權：遵循原俠正楷授權條款規範
2. **霞鶩文楷 TC (LXGW WenKai TC)**
   - 來源：[落霞孤鹜 (lxgw/lxgwwenkaitc)](https://github.com/lxgw/lxgwwenkaitc)
   - 授權：[SIL Open Font License 1.1 (OFL-1.1)](https://scripts.sil.org/OFL)
3. **白鷺楷 (BailuKai)**
   - 本專案自動化建置腳本及說明文件依據開源社群條款釋出。
   - 衍生字型保留各上游開源字型之授權條款要求。

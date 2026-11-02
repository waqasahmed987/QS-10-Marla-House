# 10 Marla House – QS Cost Dashboard (Kohistan Enclave, Wah Cantt)

A Streamlit web app built on the Excel workbook
`data/10_Marla_House_MRS_vs_Market_Wah_Cantt.xlsx`. It shows every sheet of the
workbook as interactive tables, charts and filters:

| Page | Workbook sheet(s) |
|---|---|
| ✨ Home | Landing page: hero, live payment card, BOQ register card, rate-overrun alert |
| 🏠 Overall Summary | Overall Summary |
| 🤖 AI Assistant (Groq) | Answers questions from all sheets (needs a Groq API key) |
| 🏗️ Contractor Option 1 | Contractor Option 1 (Kohistan Arena Real Estate & Builders) |
| 🔑 Rent vs Own | Rent vs Own (+ what-if rent calculator) |
| ⚖️ Options A–D & Other Costs | Summary, Other Costs, Option D - Owner Supply |
| 📈 Monthly Cash Flow & S-Curve | Monthly Cash Flow (S-curve, phase bars, Gantt) |
| 📋 BOQ (MRS vs Market) | BOQ, MRS Rate Build-up |
| 📚 MRS 2026 Schedule | MRS Schedule 2026 (4,885 rate lines, searchable) |
| ☀️ Solar System | Solar System |
| 🔮 5-Year Forecast | 5-Yr Forecast |
| 🤝 Responsibility Matrix | Responsibility Matrix |
| 📐 Drawing Register | Drawing Register |
| 🧱 Assumptions & Material Rates | Assumptions, Material Rates |
| 📝 QS Analysis Report | Analysis Report (downloadable as Markdown) |
| 🗂️ All Sheets (raw) | Any sheet, exactly as in Excel |

---

## Folder structure (modular)

```
qs_house_app/
├── app.py                 # entry point: sidebar, data source, page routing
├── requirements.txt       # Python packages for Streamlit Cloud
├── README.md
├── .gitignore
├── .streamlit/config.toml # theme + upload size
├── .streamlit/secrets.toml.example  # template for GROQ_API_KEY (never commit the real one)
├── data/
│   └── 10_Marla_House_MRS_vs_Market_Wah_Cantt.xlsx
├── core/                  # reusable logic (no page layout here)
│   ├── loader.py          # reads the workbook (cached) into one DataFrame per sheet
│   ├── tables.py          # finds tables by their header text (robust to row shifts)
│   ├── extract.py         # one function per sheet -> tidy DataFrames
│   ├── ui.py              # number formatting, tables, metric cards, downloads
│   ├── charts.py          # Plotly chart builders (S-curve, Gantt, bars, lines, pie)
│   ├── theme.py           # dark UI: global CSS, fonts, hero/pill/card/alert components
│   ├── calc.py            # what-if calculators (rent schedule)
│   └── ai.py              # Groq key lookup + workbook context for the AI assistant
└── views/                 # one file per page; each has TITLE, ICON and render(sheets)
    ├── __init__.py        # PAGES registry (order of the sidebar)
    ├── overview.py  contractor.py  rent.py  costs.py  cashflow.py  boq.py  mrs.py
    └── solar.py  forecast.py  responsibility.py  drawings.py  materials.py  report.py  sheets.py
```

---

## Step-by-step: publish the app (no coding needed)

### Step 1 – Create a GitHub account and repository
1. Go to **https://github.com** and sign up (free) or sign in.
2. Click **＋ (top right) → New repository**.
3. Name it e.g. `qs-10-marla-house`, choose **Public** (Streamlit's free tier needs public repos, or connect a private repo after granting access), tick **Add a README** off, click **Create repository**.

### Step 2 – Upload the app files
1. Unzip `qs_house_app.zip` on your computer.
2. In the new repository click **Add file → Upload files**.
3. Open the unzipped `qs_house_app` folder, select **everything inside it** (app.py, requirements.txt, README.md, .gitignore and the folders `core`, `views`, `data`, `.streamlit`) and drag them into the browser window.
   - Tip: hidden items (`.streamlit`, `.gitignore`) may not show in Windows Explorer / macOS Finder. Turn on "show hidden files" (Windows: View → Show → Hidden items; macOS: Cmd + Shift + .). The app still works without them – they only set the theme.
4. Write a message such as "First version" and click **Commit changes**.
5. Check that the repository root now shows `app.py` and the folders `core`, `views`, `data` (not a single folder called `qs_house_app`). If you see only `qs_house_app/`, that is fine too – just set the main file path to `qs_house_app/app.py` in Step 3.

### Step 3 – Deploy on Streamlit Community Cloud (free)
1. Go to **https://share.streamlit.io** and click **Continue with GitHub**; authorise Streamlit.
2. Click **Create app → Deploy a public app from GitHub**.
3. Fill in:
   - **Repository:** `your-username/qs-10-marla-house`
   - **Branch:** `main`
   - **Main file path:** `app.py`
   - **App URL:** choose a name, e.g. `qs-10-marla-house`
4. (Optional) **Advanced settings → Python version 3.11 or 3.12.**
5. Click **Deploy**. The first build installs `requirements.txt` and takes 2–4 minutes.
6. Your app is live at `https://<your-app-name>.streamlit.app` – share this link.

### Step 4 – Update the numbers later
- **Quick (no GitHub):** open the Excel file, change the blue/yellow input cells (e.g. Kohistan Arena's quoted rate on
  *Contractor Option 1*), **Save in Excel**, then use **"Use an updated workbook"** in the app sidebar to upload it.
  The whole app recalculates from your file for that session.
- **Permanent:** in GitHub open the `data` folder → **Add file → Upload files**, upload the saved workbook with the
  **same file name** (`10_Marla_House_MRS_vs_Market_Wah_Cantt.xlsx`) and commit. Streamlit Cloud redeploys automatically.

> Always save the workbook in Excel/LibreOffice before uploading – the app reads the values Excel calculated
> (it does not recalculate formulas itself). If you see "no calculated values", open the file, press Save, re-upload.

---

## Adding your Groq API key (for the 🤖 AI Assistant page)

### 1. Get a key
1. Go to **https://console.groq.com** and sign in (Google/GitHub/email).
2. Left menu **API Keys → Create API Key**, give it a name (e.g. `qs-house-app`), click **Submit**.
3. **Copy the key immediately** – it starts with `gsk_` and is shown only once.

### 2a. On Streamlit Community Cloud (the deployed app)
1. Open **https://share.streamlit.io**, find your app, click **⋮ → Settings → Secrets**.
2. Paste exactly this line (TOML format – name in capitals, key in double quotes), then **Save**:
   ```toml
   GROQ_API_KEY = "gsk_your_key_here"
   ```
3. The app restarts in a few seconds; open the **🤖 AI Assistant** page.

### 2b. On your own computer
1. Copy `.streamlit/secrets.toml.example` to **`.streamlit/secrets.toml`** (same folder as `config.toml`).
2. Put your key in it:
   ```toml
   GROQ_API_KEY = "gsk_your_key_here"
   ```
3. Run `streamlit run app.py`.

Alternative: set an environment variable `GROQ_API_KEY`, or paste the key in the sidebar of the AI page (kept for that
browser session only).

### Rules
- **Never upload `secrets.toml` or your key to GitHub** (it is already in `.gitignore`). If a key leaks, delete it in
  console.groq.com and create a new one.
- Models: the app offers `openai/gpt-oss-120b` (default) and `openai/gpt-oss-20b`. Groq moved the Llama models to
  Enterprise-only in Aug 2026; if Groq changes its model list, edit `MODELS` in `core/ai.py`.
- Free-tier limits are per minute/day; if you see a 429 error wait a minute or switch to the 20B model.

---

## Run on your own computer (optional)

```bash
# 1. Install Python 3.10+ from https://www.python.org (tick "Add to PATH" on Windows)
# 2. In a terminal, inside the qs_house_app folder:
python -m venv .venv
# Windows:  .venv\Scripts\activate      macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```
The app opens at http://localhost:8501.

### Using GitHub from the command line (alternative to Step 2)
```bash
cd qs_house_app
git init
git add .
git commit -m "First version"
git branch -M main
git remote add origin https://github.com/<your-username>/qs-10-marla-house.git
git push -u origin main
```

---

## Changing the look (core/theme.py)
- **Brand name / subtitle:** edit `BRAND`, `BRAND_SUB`, `VERSION` at the top of `core/theme.py`.
- **Colours:** edit the `C` palette (orange accent `#F59E0B`, navy background `#0A0F1E`) and the matching
  colours in `.streamlit/config.toml`; chart colours are `PALETTE` in `core/charts.py`.
- **Fonts:** Archivo (headings), Inter (text) and JetBrains Mono (numbers/codes) load from Google Fonts in the CSS `@import`.
- **Reusable components** for any page: `theme.pill()`, `theme.hero()`, `theme.stats()`, `theme.summary_card()`,
  `theme.register_card()`, `theme.alert_card()`, `theme.section()`.

## Extending the app (modular design)

**Add a new page**
1. Create `views/my_page.py`:
   ```python
   import streamlit as st
   from core.ui import table

   TITLE = "My Page"
   ICON = "⭐"

   def render(S):          # S = {sheet name: DataFrame}
       st.title(TITLE)
       table(S["Summary"].dropna(how="all"), raw=True)
   ```
2. Add it to `views/__init__.py` (import it and put it in `PAGES`). It appears in the sidebar.

**Read a new table from a sheet** – add a function in `core/extract.py` using
`find_row(df, "Header text")` and `block(df, header_row, first_col, last_col, stop_label="Total")`.
Header-text search keeps working when rows move.

**Add a chart** – add a builder in `core/charts.py` and call `figure(fig)` from a view.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError` on Streamlit Cloud | Make sure `requirements.txt` is in the same folder as `app.py`, then **Manage app → Reboot**. |
| "This page could not be built" | A sheet's headers were renamed or deleted. Restore the layout or check the page under **All Sheets (raw)**. |
| "no calculated values" | Open the workbook in Excel, press **Save**, upload again. |
| Upload too large | Limit is 50 MB (`.streamlit/config.toml`). |
| AI page: "No Groq API key found" | Add `GROQ_API_KEY` in **Settings → Secrets** exactly as shown above, then reboot the app. |
| AI page: 401 / invalid key | The key was mistyped or deleted - create a new key in console.groq.com. |
| App sleeps after inactivity | Normal on the free tier – open the link and click **Wake up**. |

*Figures are QS estimates for decision-making. Verify MRS rates against the official PDF, society charges with Kohistan Enclave and contractor quotations before signing.*

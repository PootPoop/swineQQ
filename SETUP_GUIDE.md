# Setup Guide - Swine Farm AI Assistant with Charts

## Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Snowflake account credentials

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/PootPoop/swineQQ.git
cd swineQQ
```

### 2. Create Virtual Environment

**On Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**On Linux/Mac:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables

#### **Important: .env File Encoding (Windows Users)**

The `.env` file **must be saved in UTF-8 encoding** without BOM (Byte Order Mark).

**Option A: Use Notepad++ (Recommended for Windows)**

1. Copy `.env.example` to `.env`:
   ```bash
   copy .env.example .env
   ```

2. Open `.env` in Notepad++

3. Go to **Encoding** menu → Select **"Encode in UTF-8"** (NOT "UTF-8 with BOM")

4. Fill in your credentials:
   ```
   OPENAI_API_KEY=sk-your-actual-key-here
   JAPFA_ACCOUNT=your_account.region
   JAPFA_USER=your_username
   JAPFA_PASSWORD=your_password
   JAPFA_DATABASE=your_database
   JAPFA_SCHEMA=your_schema
   JAPFA_WAREHOUSE=your_warehouse
   JAPFA_ROLE=PUBLIC
   ```

5. Save the file (Ctrl+S)

**Option B: Use VS Code**

1. Copy `.env.example` to `.env`

2. Open `.env` in VS Code

3. Click on the encoding in the bottom right corner (it might say "UTF-16 LE" or "UTF-8 with BOM")

4. Select **"Save with Encoding"** → Choose **"UTF-8"**

5. Fill in your credentials

6. Save the file

**Option C: Command Line (PowerShell)**

```powershell
# Copy example file
Copy-Item .env.example .env

# Open in notepad and edit (save as UTF-8)
notepad .env
```

In Notepad: **File** → **Save As** → Set **"Encoding"** dropdown to **"UTF-8"** → Save

**Option D: Use the Template**

Create `.env` manually with this content (ensure UTF-8 encoding):

```
OPENAI_API_KEY=your_openai_api_key_here
JAPFA_ACCOUNT=your_account.region
JAPFA_USER=your_username
JAPFA_PASSWORD=your_password
JAPFA_DATABASE=your_database
JAPFA_SCHEMA=your_schema
JAPFA_WAREHOUSE=your_warehouse
JAPFA_ROLE=PUBLIC
```

### 5. Copy Original Workflow Files

You need the original workflow files from the git history:

```bash
# Copy from git history (if available)
git show HEAD~1:/tmp/swine_alert-main/agentkit_python/workflow.py > workflow.py
git show HEAD~1:/tmp/swine_alert-main/agentkit_python/guardrails_advanced.py > guardrails_advanced.py
```

Or copy them manually if you have the original files.

### 6. Run the Application

```bash
streamlit run streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

## Troubleshooting

### UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff

**Problem:** Your `.env` file is not in UTF-8 encoding.

**Solution:**

1. **Delete the current `.env` file**
   ```bash
   del .env   # Windows
   rm .env    # Linux/Mac
   ```

2. **Recreate it in UTF-8:**
   - Use one of the methods in Step 4 above
   - Ensure you select **UTF-8** encoding (NOT UTF-16, NOT UTF-8 with BOM)

3. **Verify encoding (PowerShell):**
   ```powershell
   Get-Content .env -Encoding UTF8
   ```

### ModuleNotFoundError: No module named 'workflow'

**Problem:** Original workflow files are missing.

**Solution:**

1. Copy the files from the original project:
   ```bash
   # From /tmp/swine_alert-main/agentkit_python/
   cp workflow.py .
   cp guardrails_advanced.py .
   ```

2. Or create them if you have the source code

### OpenAI API Error

**Problem:** Invalid API key or quota exceeded.

**Solution:**

1. Check your `.env` file has the correct `OPENAI_API_KEY`
2. Verify your OpenAI account has credits: https://platform.openai.com/account/usage
3. Test the API key:
   ```python
   from openai import OpenAI
   client = OpenAI(api_key="your-key-here")
   response = client.chat.completions.create(
       model="gpt-4o-mini",
       messages=[{"role": "user", "content": "Hello"}]
   )
   print(response.choices[0].message.content)
   ```

### Snowflake Connection Error / Network Policy Error

**Problem:** Can't connect to Snowflake database or see "Network policy is required" error.

**Solution:**

1. **If you see "Network policy is required":**
   - Your IP address is not whitelisted
   - See detailed guide: [NETWORK_POLICY_WORKAROUND.md](NETWORK_POLICY_WORKAROUND.md)
   - **Quick fix:** Switch to "SQLite (Local Testing)" in the sidebar

2. Verify all `JAPFA_*` variables in `.env` are correct

3. Test connection:
   ```python
   import snowflake.connector
   conn = snowflake.connector.connect(
       account='your_account',
       user='your_user',
       password='your_password'
   )
   print("✓ Connected!")
   conn.close()
   ```

4. Check Snowflake firewall/network settings

5. **Temporary workaround:** Use local SQLite mode (see "Database Connection" in sidebar)

### Charts Not Displaying

**Problem:** Charts don't render in Streamlit.

**Solution:**

1. Verify `plotly` is installed:
   ```bash
   pip install plotly==6.3.1
   ```

2. Check browser console for JavaScript errors (F12)

3. Try a simple query first: Click "📈 Mortality Trends" quick action button

4. Check that query returned data in "Raw Data" expander

## Usage

### Text Analysis (Original Workflow)

Just type your question:
```
"Which farms have high mortality?"
"Show me temperature issues"
```

### Chart Visualization (New Feature)

Use chart keywords:
```
"Show me a chart of mortality trends"
"Plot temperature over time"
"Visualize disease rates by farm"
```

### Quick Action Buttons

Click the buttons at the bottom:
- **Text:** High Mortality, Disease Outbreaks, Temperature Issues
- **Charts:** Mortality Trends, Disease Comparison, Temp vs Mortality

### Workflow Modes

In the sidebar, select:
- **Auto-detect** - AI decides chart vs text (recommended)
- **Force Charts** - All queries generate charts
- **Force Text** - All queries return text analysis

## File Structure

```
swineQQ/
├── streamlit_app.py           # Main Streamlit UI
├── workflow_unified.py        # Routes chart vs text
├── workflow_chart.py          # Chart workflow
├── chart_agents.py            # Chart AI agents
├── chart_renderer.py          # Plotly rendering
├── workflow.py                # Original text workflow
├── guardrails_advanced.py     # Security checks
├── database.py                # SQLite mirror
├── requirements.txt           # Dependencies
├── .env                       # Your credentials (UTF-8!)
├── .env.example              # Template
├── CHART_FEATURE_GUIDE.md    # Detailed feature docs
└── SETUP_GUIDE.md            # This file
```

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `JAPFA_ACCOUNT` | Snowflake account | `abc12345.us-east-1` |
| `JAPFA_USER` | Snowflake username | `ADMIN` |
| `JAPFA_PASSWORD` | Snowflake password | `your_password` |
| `JAPFA_DATABASE` | Database name | `SWINE_DB` |
| `JAPFA_SCHEMA` | Schema name | `PUBLIC` |
| `JAPFA_WAREHOUSE` | Warehouse name | `COMPUTE_WH` |
| `JAPFA_ROLE` | Role (optional) | `PUBLIC` |

## Security Notes

- **Never commit `.env` to git** (already in `.gitignore`)
- Keep your API keys secure
- Use read-only Snowflake credentials if possible
- The app only executes SELECT queries (no INSERT/UPDATE/DELETE)

## Getting Help

1. Check `CHART_FEATURE_GUIDE.md` for detailed feature documentation
2. Review error messages in Streamlit console
3. Test with quick action buttons first
4. Verify `.env` file encoding is UTF-8

## Next Steps

After setup:

1. Test text queries with quick action buttons
2. Try chart queries: "Show me a chart of mortality trends"
3. Explore the sidebar options (Auto-detect, Force Charts, Force Text)
4. Check the expandable sections (SQL, Raw Data, Chart Spec)

## License

Same as main project.

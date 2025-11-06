"""
Swine Farm AI Workflow - Standard OpenAI Library Only
NO Agent SDK required!
"""
from openai import OpenAI

from pydantic import BaseModel
from dotenv import load_dotenv
import os
import re
from guardrails_advanced import run_security_checks

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


# ===== PROMPTS =====

CREATE_SWINE_QUERY_PROMPT = """You are a translator between natural language and domain-specific language for queries related to swine farm operations (health, mortality, biosecurity, and environmental monitoring).

Your role is to transform a natural-language analytics request into a single, correct, executable Snowflake SQL query using only what is declared in the provided full_ontology.

<full_ontology>
version: 1.1
namespace: swine_farm_ontology

entities:
  jini_swine_dataset:
    table: SWINE_ALERT
    description: >
      Main integrated dataset combining farm operations, environmental metrics, 
      mortality data, disease indicators, vaccination details, and biosecurity checks
      for swine farms under the JINI monitoring system.

    columns:
      # Core Identifiers and Metadata
      UNIQUE_ID: {type: STRING, nullable: false, description: "Unique record identifier"}
      START_DATE: {type: STRING, nullable: true, description: "Start date of reporting period"}
      END_DATE: {type: STRING, nullable: true, description: "End date of reporting period"}
      OPERATION: {type: STRING, nullable: true, description: "Operational unit or region"}
      GMF_ID: {type: STRING, nullable: true, description: "Global farm identifier"}
      ZALO_GROUP_NAME: {type: STRING, nullable: true, description: "Associated Zalo group name"}
      FARM_CODE: {type: STRING, nullable: true, description: "Farm code identifier"}
      FARM_NAME: {type: STRING, nullable: true, description: "Farm name"}
      FARM_TYPE: {type: STRING, nullable: true, description: "Farm type (e.g., farrow-to-finish, nursery)"}
      REPORT_BARN_CODE: {type: STRING, nullable: true, description: "Barn code as reported"}
      SYSTEM_BARN_CODE: {type: STRING, nullable: true, description: "System-generated barn code"}
      BARN_NAME: {type: STRING, nullable: true, description: "Barn or building name"}
      BLOOD_TYPE: {type: STRING, nullable: true, description: "Blood or test type"}
      FLOCK_CODE: {type: STRING, nullable: true, description: "Internal flock code"}
      FLOCK_NAME: {type: STRING, nullable: true, description: "Internal flock name"}
      FARM_SOURCE: {type: STRING, nullable: true, description: "Origin source of data"}

      # Population & Mortality Metrics
      BEGIN_POP_TOTAL: {type: INTEGER, nullable: true, description: "Beginning total population"}
      BEGIN_POP: {type: INTEGER, nullable: true, description: "Beginning population for this record"}
      DAILY_BEGIN_POP: {type: INTEGER, nullable: true, description: "Daily beginning population"}
      PIGLET_IN: {type: INTEGER, nullable: true, description: "Number of piglets introduced"}
      SALES_TRANSFER: {type: INTEGER, nullable: true, description: "Number of pigs sold or transferred"}
      DEATH_CULLING_TOTAL: {type: INTEGER, nullable: true, description: "Total death and culling count"}
      DC_HEAD: {type: INTEGER, nullable: true, description: "Death/culling headcount"}
      DC_BEGIN_POP: {type: INTEGER, nullable: true, description: "Population base for DC% calculation"}
      DC_PERCENT: {type: FLOAT, nullable: true, description: "Death/culling percentage (Primary KPI: >5% = critical)"}
      YTD_HEAD: {type: INTEGER, nullable: true, description: "Year-to-date death count"}
      YTD_TOTAL: {type: INTEGER, nullable: true, description: "Year-to-date total population"}
      YTD_PERCENT: {type: FLOAT, nullable: true, description: "Year-to-date mortality percentage"}

      # Growth & Weight
      PIG_IN_WEIGHT: {type: FLOAT, nullable: true, description: "Average weight of pigs on entry (kg)"}
      PIG_IN_WEEK_AGE: {type: INTEGER, nullable: true, description: "Week age of pigs on entry"}
      PIG_IN_DAY_AGE: {type: INTEGER, nullable: true, description: "Day age of pigs on entry"}
      ESTIMATED_WEIGHT: {type: FLOAT, nullable: true, description: "Estimated average weight (kg)"}
      RAISE_WEEK: {type: INTEGER, nullable: true, description: "Week number in raising period"}
      RAISE_DAY: {type: INTEGER, nullable: true, description: "Day number in raising period"}
      CALCULATED_RAISING_WEEK: {type: INTEGER, nullable: true, description: "Calculated raising week"}
      CALCULATED_RAISING_DAY: {type: INTEGER, nullable: true, description: "Calculated raising day"}
      START_RAISING_DATE: {type: STRING, nullable: true, description: "Date raising began"}
      RAISING_TYPE: {type: STRING, nullable: true, description: "Type of raising system"}

      # Feed Metrics
      FEED_INTAKE_ACTUAL: {type: FLOAT, nullable: true, description: "Actual feed intake (kg/day)"}
      FEED_INTAKE_STD: {type: FLOAT, nullable: true, description: "Standard feed intake (kg/day)"}
      FEED_TYPE: {type: STRING, nullable: true, description: "Feed type used"}
      TIME_EMPTY_FEEDER: {type: STRING, nullable: true, description: "Times feeders were empty"}

      # Temperature (Environmental Stability)
      MIN_INDOOR_TEMPERATURE: {type: FLOAT, nullable: true, description: "Minimum indoor temperature (°C)"}
      MAX_INDOOR_TEMPERATURE: {type: FLOAT, nullable: true, description: "Maximum indoor temperature (°C)"}
      MIN_OUTDOOR_TEMPERATURE: {type: FLOAT, nullable: true, description: "Minimum outdoor temperature (°C)"}
      MAX_OUTDOOR_TEMPERATURE: {type: FLOAT, nullable: true, description: "Maximum outdoor temperature (°C)"}

      # Disease Indicators
      PNEUMONIA_COUNT: {type: INTEGER, nullable: true, description: "Number of pigs with pneumonia"}
      PNEUMONIA_PERCENT: {type: FLOAT, nullable: true, description: "Percent with pneumonia"}
      DIARRHEA_COUNT: {type: INTEGER, nullable: true, description: "Number of pigs with diarrhea"}
      DIARRHEA_PERCENT: {type: FLOAT, nullable: true, description: "Percent with diarrhea"}
      SUDDEN_DEATH_COUNT: {type: INTEGER, nullable: true, description: "Number of sudden deaths"}
      SUDDEN_DEATH_PERCENT: {type: FLOAT, nullable: true, description: "Percent sudden deaths"}
      FEVER_COUNT: {type: INTEGER, nullable: true, description: "Number of pigs with fever"}
      FEVER_PERCENT: {type: FLOAT, nullable: true, description: "Percent with fever"}
      CONVULSION_COUNT: {type: INTEGER, nullable: true, description: "Number of pigs with convulsions"}
      CONVULSION_PERCENT: {type: FLOAT, nullable: true, description: "Percent with convulsions"}
      ARTHRITIS_COUNT: {type: INTEGER, nullable: true, description: "Number of arthritis cases"}
      ARTHRITIS_PERCENT: {type: FLOAT, nullable: true, description: "Percent arthritis cases"}
      PARALYSIS_COUNT: {type: INTEGER, nullable: true, description: "Number of paralysis cases"}
      PARALYSIS_PERCENT: {type: FLOAT, nullable: true, description: "Percent paralysis cases"}

      # Disease & Vaccination Flags
      PRRS: {type: STRING, nullable: true, description: "PRRS (Porcine Reproductive and Respiratory Syndrome) detection status"}
      VACCINATION: {type: STRING, nullable: true, description: "Vaccination status summary"}
      EXTRACTED_VACCINES: {type: ARRAY, nullable: true, description: "List of vaccines administered"}
      GRADE_B: {type: STRING, nullable: true, description: "Farm grade or biosecurity rating"}

      # Biosecurity & Inspection Rounds
      R1_GATE_DISINFECTION_PIT: {type: STRING, nullable: true, description: "Round 1 - Gate disinfection pit status"}
      R1_INSECT_NET: {type: STRING, nullable: true, description: "Round 1 - Insect net installation"}
      R1_LIME_CORRIDOR: {type: STRING, nullable: true, description: "Round 1 - Lime corridor status"}
      R1_FLIES_DETECTED: {type: STRING, nullable: true, description: "Round 1 - Flies detected"}
      R1_RATS_DETECTED: {type: STRING, nullable: true, description: "Round 1 - Rats detected"}
      R2_GATE_DISINFECTION_PIT: {type: STRING, nullable: true, description: "Round 2 - Gate disinfection pit status"}
      R2_INSECT_NET: {type: STRING, nullable: true, description: "Round 2 - Insect net installation"}
      R2_LIME_CORRIDOR: {type: STRING, nullable: true, description: "Round 2 - Lime corridor status"}
      R2_FLIES_DETECTED: {type: STRING, nullable: true, description: "Round 2 - Flies detected"}
      R2_RATS_DETECTED: {type: STRING, nullable: true, description: "Round 2 - Rats detected"}

      # On-Site Activity (Biosecurity)
      FLIES_MOSQUITOES_DETECTED: {type: STRING, nullable: true, description: "Flies or mosquitoes detected"}
      RATS_DETECTED: {type: STRING, nullable: true, description: "Rat detection status"}
      WILD_ANIMALS_DETECTED: {type: STRING, nullable: true, description: "Wild animal detection status"}
      SPRAYING_DISINFECTANT: {type: STRING, nullable: true, description: "Disinfectant spraying status"}
      SPRAYING_FLY_POISON: {type: STRING, nullable: true, description: "Fly poison spraying status"}
      SPRINKLING_RAT_BAIT: {type: STRING, nullable: true, description: "Rat bait application status"}

      # Alerts & Reports
      ALERT_TOPIC: {type: STRING, nullable: true, description: "Alert topic or category"}
      ALERT_TYPE: {type: STRING, nullable: true, description: "Alert severity type (e.g., critical, warning, info)"}
      REASON: {type: STRING, nullable: true, description: "Reason or cause of the alert"}
      SOLUTION: {type: STRING, nullable: true, description: "Recommended solution or corrective action"}
      CONCLUDE: {type: STRING, nullable: true, description: "Overall conclusion or summary"}
      REPORT_DATE: {type: TIMESTAMP, nullable: true, description: "Date when report was created"}

    common_query_patterns:
      high_mortality: >
        SELECT FARM_NAME, BARN_NAME, DC_PERCENT, DC_HEAD, REPORT_DATE
        FROM SWINE_ALERT
        WHERE DC_PERCENT > 5.0
        ORDER BY DC_PERCENT DESC
        LIMIT 10

      temperature_instability: >
        SELECT FARM_NAME, MIN_INDOOR_TEMPERATURE, MAX_INDOOR_TEMPERATURE,
               (MAX_INDOOR_TEMPERATURE - MIN_INDOOR_TEMPERATURE) AS TEMP_VARIANCE
        FROM SWINE_ALERT
        WHERE (MAX_INDOOR_TEMPERATURE - MIN_INDOOR_TEMPERATURE) > 10
        ORDER BY TEMP_VARIANCE DESC
        LIMIT 10

      disease_outbreaks: >
        SELECT FARM_NAME,
               (PNEUMONIA_PERCENT + DIARRHEA_PERCENT + FEVER_PERCENT + SUDDEN_DEATH_PERCENT) AS TOTAL_AFFECTED_PERCENT
        FROM SWINE_ALERT
        WHERE TOTAL_AFFECTED_PERCENT > 10
        ORDER BY TOTAL_AFFECTED_PERCENT DESC
        LIMIT 10

      critical_alerts: >
        SELECT FARM_NAME, ALERT_TYPE, ALERT_TOPIC, REASON, SOLUTION, REPORT_DATE
        FROM SWINE_ALERT
        WHERE ALERT_TYPE = 'critical'
        ORDER BY REPORT_DATE DESC
        LIMIT 20

      biosecurity_issues: >
        SELECT FARM_NAME, RATS_DETECTED, FLIES_MOSQUITOES_DETECTED, WILD_ANIMALS_DETECTED, R1_GATE_DISINFECTION_PIT
        FROM SWINE_ALERT
        WHERE RATS_DETECTED = 'detected'
           OR FLIES_MOSQUITOES_DETECTED = 'detected'
           OR WILD_ANIMALS_DETECTED = 'detected'
        LIMIT 20
</full_ontology>


QUERY GENERATION RULES:

1. ALWAYS use proper Snowflake SQL syntax
2. ONLY SELECT queries (no INSERT, UPDATE, DELETE, DROP)
3. ALWAYS include LIMIT clause (default: 10, max: 100)
4. Handle NULLs correctly: IS NULL / IS NOT NULL (never = NULL or != NULL)
5. Use column names EXACTLY as defined in the ontology
6. For percentages, use dc_percent (not DC_PERCENT or Dc_Percent)
7. For farm names, use farm_name (not FARM_NAME)
8. For temperature, use min_indoor_temperature and max_indoor_temperature
9. Order results by the most relevant column (e.g., dc_percent DESC for mortality queries)

OUTPUT FORMAT:
Generate ONLY the SQL query wrapped in a markdown code block:
```sql
SELECT farm_name, dc_percent, dc_head
FROM swine_alert
WHERE dc_percent > 5.0
ORDER BY dc_percent DESC;
```

Do NOT include explanations, comments, or additional text outside the code block.
"""


SUMMARIZE_RESULTS_PROMPT = """You are an expert swine farm data analyst and agricultural consultant specializing in pig health, mortality analysis, biosecurity, and environmental management.

Your role is to analyze SQL query results from the SWINE_ALERT and provide clear, actionable insights for farm managers and veterinarians.

ANALYSIS FRAMEWORK:

1. METRIC INTERPRETATION GUIDELINES

   Mortality Metrics:
   DC_PERCENT (Daily mortality rate):
   ✅ Excellent: 0-2% (industry best practice)
   🟢 Good: 2-3% (acceptable range)
   🟡 Concerning: 3-5% (requires attention)
   🔴 Critical: >5% (urgent intervention needed)
   
   YTD_PERCENT (Year-to-date cumulative mortality):
   ✅ Excellent: 0-3%
   🟡 Concerning: 3-6%
   🔴 Critical: >6%
   
   Temperature Stability:
   Calculate variance: (MAX_INDOOR_TEMPERATURE - MIN_INDOOR_TEMPERATURE)
   ✅ Ideal: Variance < 5°C (stable environment)
   🟡 Concerning: Variance 5-10°C (monitoring needed)
   🔴 Critical: Variance > 10°C (immediate action required)
   📍 Optimal Range: 20-25°C indoor temperature
   💡 Consider outdoor impact: Check MAX_OUTDOOR_TEMPERATURE/MIN_OUTDOOR_TEMPERATURE correlation
   
   Disease Incidence (individual disease percentages):
   ✅ Minimal: < 2% (normal background)
   🟡 Concerning: 2-10% (monitor closely)
   🔴 Outbreak: > 10% (veterinary intervention)
   
   Available disease metrics:
   - PNEUMONIA_PERCENT (respiratory health indicator)
   - DIARRHEA_PERCENT (digestive health, potential infection)
   - SUDDEN_DEATH_PERCENT (acute stress/disease indicator)
   - FEVER_PERCENT (systemic infection marker)
   - CONVULSION_PERCENT (neurological issues)
   - ARTHRITIS_PERCENT (joint health, mobility)
   - PARALYSIS_PERCENT (neurological disease)
   
   Feed Efficiency:
   Compare FEED_INTAKE_ACTUAL vs FEED_INTAKE_STD:
   ✅ Good: 95-105% of standard (efficient growth)
   🟡 Review: 85-95% or 105-115% (adjust strategy)
   🔴 Critical: <85% or >115% (health or waste issues)
   💡 Check TIME_EMPTY_FEEDER for feeding disruptions
   
   Biosecurity Compliance (R1_* and R2_* inspection rounds):
   Key checkpoint fields:
   - NST (inspection passed/failed)
   - GATE_DISINFECTION_PIT
   - INSECT_NET
   - BRAN_WAREHOUSE
   - LIME_CORRIDOR
   - FLIES_DETECTED / RATS_DETECTED
   ✅ All "Pass" or "No": Compliant
   🟡 1-2 failures: Attention needed
   🔴 3+ failures: Critical biosecurity risk
   
   Population Health:
   - Monitor BEGIN_POP vs DEATH_CULLING_TOTAL ratio
   - Track SALES_TRANSFER vs mortality balance
   - RAISE_WEEK / RAISE_DAY: Age-specific mortality patterns

2. RESPONSE STRUCTURE
   A. DIRECT ANSWER (1 sentence with specific numbers from query results)
   B. KEY FINDINGS (2-4 bullet points with emojis and bold)
   C. RECOMMENDATIONS (1-3 actionable steps)
   D. CONTEXT (if relevant: FARM_NAME, BARN_NAME, FLOCK_CODE, REPORT_DATE)

3. FORMATTING RULES
   - Use **bold** for FARM_NAME, BARN_NAME, and critical metrics
   - Use emojis for visual severity indicators (✅🟢🟡🔴🚨💡📍)
   - Keep responses to 200-400 words
   - No tables unless specifically requested
   - Always cite specific column values when available

4. DATA QUALITY CHECKS
   - Verify REPORT_DATE recency
   - Note NULL values in critical fields
   - Flag suspicious outliers (e.g., DC_PERCENT > 50%)
   - Consider OPERATION type (different standards may apply)

EXAMPLE RESPONSES:

Query: "Which farms have high mortality?"
Response:
"Based on the latest data, **3 farms** show critical mortality rates exceeding 5%:

🚨 **Farm A (Barn 101)** - **DC_PERCENT: 7.2%** (36 out of 500 pigs)
   └─ Temperature variance: 12°C (MAX_INDOOR: 32°C, MIN_INDOOR: 20°C)
   └─ PNEUMONIA_PERCENT: 15% (outbreak detected)
   └─ Report Date: 2025-10-28

🔴 **Farm B (Barn 205)** - **DC_PERCENT: 5.8%** 
   └─ DIARRHEA_PERCENT: 8%, FEVER_PERCENT: 6%
   └─ R1_GATE_DISINFECTION_PIT: Failed

**Immediate Actions:**
1. Farm A: Emergency HVAC inspection + veterinary consult for pneumonia outbreak
2. Farm B: Enhance biosecurity protocols, repair disinfection pit
3. All farms: Daily DC_PERCENT monitoring until <3%"

Query: "Feed efficiency issues?"
Response:
"**2 barns** show concerning feed efficiency patterns:

🟡 **Barn 302** - FEED_INTAKE_ACTUAL: 82% of standard
   └─ TIME_EMPTY_FEEDER: 6 hours/day (feeding disruption)
   └─ ESTIMATED_WEIGHT below target

**Recommendations:**
1. Inspect feeder mechanisms in Barn 302
2. Check for dominant pig behavior limiting access
3. Monitor FEED_INTAKE_ACTUAL daily for 1 week"

NEVER make up data not in the query results.
ALWAYS reference actual column names from SWINE_ALERT.
"""


# ===== HELPER FUNCTIONS =====

def extract_sql_from_markdown(text: str) -> str:
    """Extract SQL query from markdown code block"""
    # Try markdown SQL block
    sql_match = re.search(r'```sql\n(.*?)\n```', text, re.DOTALL | re.IGNORECASE)
    if sql_match:
        return sql_match.group(1).strip()
    
    # Try any code block
    code_match = re.search(r'```\n(.*?)\n```', text, re.DOTALL)
    if code_match and 'SELECT' in code_match.group(1).upper():
        return code_match.group(1).strip()
    
    # Try SELECT statement directly
    select_match = re.search(r'(SELECT\s+.*?;)', text, re.DOTALL | re.IGNORECASE)
    if select_match:
        return select_match.group(1).strip()
    
    # Last resort
    if 'SELECT' in text.upper() and 'FROM' in text.upper():
        cleaned = text.strip()
        if not cleaned.endswith(';'):
            cleaned += ';'
        return cleaned
    
    raise ValueError(f"Could not extract SQL from response: {text[:200]}...")


def run_openai_moderation(text: str) -> dict:
    """Use OpenAI's built-in moderation API"""
    try:
        response = client.moderations.create(input=text)
        result = response.results[0]
        
        if result.flagged:
            flagged_cats = [cat for cat, val in result.categories.model_dump().items() if val]
            return {
                "blocked": True,
                "flagged_categories": flagged_cats,
                "provider": "OpenAI Moderation"
            }
        
        return {"blocked": False, "safe_text": text, "provider": "OpenAI Moderation"}
    
    except Exception as e:
        print(f"⚠️ Moderation failed: {e}")
        return {"blocked": False, "safe_text": text}


def execute_snowflake_query(sql_query: str) -> list:
    """Execute query on Snowflake database"""
    import snowflake.connector
    
    config = {
        'account': os.getenv('JAPFA_ACCOUNT'),
        'user': os.getenv('JAPFA_USER'),
        'password': os.getenv('JAPFA_PASSWORD'),
        'database': os.getenv('JAPFA_DATABASE'),
        'schema': os.getenv('JAPFA_SCHEMA'),
        'warehouse': os.getenv('JAPFA_WAREHOUSE'),
        'role': os.getenv('JAPFA_ROLE', 'PUBLIC')
    }
    
    conn = snowflake.connector.connect(**config)
    
    try:
        cursor = conn.cursor(snowflake.connector.DictCursor)
        cursor.execute(sql_query)
        results = cursor.fetchall()
        return results
    finally:
        cursor.close()
        conn.close()


# ===== MAIN WORKFLOW =====

class WorkflowInput(BaseModel):
    input_as_text: str


def run_workflow(workflow_input: WorkflowInput):
    user_input = workflow_input.input_as_text

    print("🛡️ Step 1: Multi-layer security checks...")
    security_result = run_security_checks(user_input, jailbreak_threshold=0.5)
    if security_result.get("blocked"):
        return {"success": False, "error": f"Security check failed: {security_result['reason']}"}

    print("🤖 Step 2: Generating SQL query...")
    sql_response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": CREATE_SWINE_QUERY_PROMPT},
            {"role": "user", "content": user_input}
        ],
    )
    sql_text = sql_response.choices[0].message.content
    sql_query = extract_sql_from_markdown(sql_text)

    print("💾 Step 3: Executing on Snowflake...")
    results = execute_snowflake_query(sql_query)

    print("📊 Step 4: Analyzing results...")
    analysis_response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": SUMMARIZE_RESULTS_PROMPT},
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": f"```sql\n{sql_query}\n```"},
            {"role": "system", "content": f"Query results ({len(results)} rows):\n{str(results[:20])}"}
        ],
    )
    analysis = analysis_response.choices[0].message.content

    return {"success": True, 
            "sql_query": sql_query, 
            "raw_results": results, 
            "analysis": analysis, 
            "moderation_provider": security_result.get("provider", "OpenAI Moderation")}
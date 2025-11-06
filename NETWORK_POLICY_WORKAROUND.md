# Snowflake Network Policy Workaround

## Problem: "Network policy is required" Error

If you see this error:

```
❌ Error: Query execution failed: 250001 (08001): Failed to connect to DB:
xxx.snowflakecomputing.com:443. Fail : Network policy is required.
```

This means your **Snowflake account has IP restrictions** and your current IP address is not whitelisted.

## What is a Network Policy?

A **network policy** in Snowflake restricts database connections to specific IP addresses or IP ranges. Organizations use this for security to ensure only authorized networks can access their data.

## Solutions

### ✅ Solution 1: Use Local SQLite Mode (Recommended for Testing)

The app now supports a **local SQLite database** for testing when Snowflake is not accessible.

#### Steps:

1. **Select SQLite mode in the app:**
   - Open the Streamlit app
   - Go to **Sidebar** → **Database Connection**
   - Select **"SQLite (Local Testing)"**

2. **Create the local database** (if you don't have one):

   ```python
   # Run this Python script to create sample data
   from database import SwineDatabase, SwineReportData
   import random
   from datetime import datetime, timedelta

   db = SwineDatabase("swine_data.db")

   # Generate sample data
   records = []
   farms = ["Farm A", "Farm B", "Farm C", "Farm D", "Farm E"]
   barns = ["Barn 101", "Barn 102", "Barn 201", "Barn 202"]

   for i in range(100):
       date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")

       record = SwineReportData(
           UNIQUE_ID=f"REC{i:04d}",
           REPORT_DATE=date,
           FARM_NAME=random.choice(farms),
           BARN_NAME=random.choice(barns),
           DC_PERCENT=round(random.uniform(1.0, 8.0), 2),
           YTD_PERCENT=round(random.uniform(2.0, 6.0), 2),
           BEGIN_POP=random.randint(400, 600),
           DC_HEAD=random.randint(5, 30),
           PNEUMONIA_PERCENT=round(random.uniform(0, 15), 2),
           DIARRHEA_PERCENT=round(random.uniform(0, 12), 2),
           FEVER_PERCENT=round(random.uniform(0, 10), 2),
           MIN_INDOOR_TEMPERATURE=round(random.uniform(18, 22), 1),
           MAX_INDOOR_TEMPERATURE=round(random.uniform(24, 32), 1),
           FEED_INTAKE_ACTUAL=round(random.uniform(1.8, 2.5), 2),
           FEED_INTAKE_STD=2.2
       )
       records.append(record)

   db.insert_records_batch(records)
   print(f"✓ Created {len(records)} sample records in swine_data.db")
   ```

3. **Test with charts:**
   - Try: "Show me a chart of mortality trends"
   - The app will use your local SQLite database

#### Pros:
✅ Works immediately without network access
✅ Good for development and testing
✅ No firewall/VPN required

#### Cons:
⚠️ Uses sample/local data, not production Snowflake data
⚠️ Need to create the database first

---

### 🔒 Solution 2: Contact Snowflake Administrator

Ask your Snowflake admin to whitelist your IP address.

#### Steps:

1. **Find your current IP address:**

   **Windows (PowerShell):**
   ```powershell
   (Invoke-WebRequest -Uri "https://api.ipify.org").Content
   ```

   **Linux/Mac:**
   ```bash
   curl https://api.ipify.org
   ```

   **Or visit:** https://www.whatismyip.com/

2. **Email your Snowflake admin:**

   ```
   Subject: Please whitelist my IP for Snowflake access

   Hi [Admin Name],

   I'm unable to connect to Snowflake due to a network policy restriction.

   Error: "Network policy is required"

   My current IP address: [YOUR_IP_ADDRESS]

   Could you please add this IP to the allowed list?

   Thank you!
   ```

3. **Wait for confirmation** that your IP has been whitelisted

4. **Test the connection** in the app (switch back to "Snowflake (Production)" in sidebar)

#### Pros:
✅ Access to real production data
✅ Permanent solution

#### Cons:
⚠️ Requires admin approval
⚠️ May take time
⚠️ IP might change if you're on a dynamic IP

---

### 🌐 Solution 3: Use VPN

If your organization has a VPN, connect to it before using the app.

#### Steps:

1. **Connect to your organization's VPN**
   - Use your company's VPN client (e.g., Cisco AnyConnect, OpenVPN, etc.)
   - Connect to the corporate network

2. **Verify you're connected:**
   ```powershell
   # Check your IP changed
   (Invoke-WebRequest -Uri "https://api.ipify.org").Content
   ```

3. **Run the Streamlit app:**
   ```bash
   streamlit run streamlit_app.py
   ```

4. **Keep sidebar on "Snowflake (Production)"**

#### Pros:
✅ Access to real production data
✅ Works immediately if VPN is set up
✅ Secure connection

#### Cons:
⚠️ Requires VPN access
⚠️ Need to stay connected to VPN
⚠️ May slow down connection

---

### 🔧 Solution 4: For Snowflake Admins - Modify Network Policy

If you are a Snowflake administrator, you can modify the network policy:

```sql
-- View current network policies
SHOW NETWORK POLICIES;

-- View allowed IPs in a specific policy
DESCRIBE NETWORK POLICY my_policy;

-- Add an IP address to allowed list
ALTER NETWORK POLICY my_policy
SET ALLOWED_IP_LIST = ('203.0.113.0', '198.51.100.0/24', 'NEW_IP_HERE');

-- Or create a new policy
CREATE NETWORK POLICY allow_all
  ALLOWED_IP_LIST = ('0.0.0.0/0')
  COMMENT = 'Allow all IPs (NOT RECOMMENDED for production)';

-- Apply policy to user
ALTER USER my_user SET NETWORK_POLICY = my_policy;
```

⚠️ **Warning:** Be careful with network policies in production environments!

---

## How the App Handles Network Errors

The app now **automatically detects** network policy errors and:

1. ✅ Shows a clear error message
2. ✅ Provides suggestions (switch to SQLite mode)
3. ✅ Displays helpful workaround instructions
4. ✅ Allows you to switch database mode in the sidebar

## Testing the Fix

### Test with Local SQLite:

1. Switch to "SQLite (Local Testing)" in sidebar
2. Click "📈 Mortality Trends" quick action
3. Should see a chart with local data
4. Check "Performance" expander - should say "Database: SQLite (Local)"

### Test with Snowflake (after whitelist):

1. Switch to "Snowflake (Production)" in sidebar
2. Try the same query
3. Should connect successfully
4. Check "Performance" expander - should say "Database: Snowflake (Production)"

## Frequently Asked Questions

### Q: Will my charts work with local SQLite?

**A:** Yes! The chart agents work identically with SQLite. The only difference is the data source.

### Q: Can I import my own data into SQLite?

**A:** Yes! Use the `database.py` script to import CSV files or create records programmatically.

### Q: Does the text analysis workflow support SQLite?

**A:** Currently, only the **chart workflow** supports SQLite mode. Text analysis still requires Snowflake. We're working on adding SQLite support to the text workflow as well.

### Q: How do I know which database I'm using?

**A:** Check the sidebar - it shows the selected mode. Also, the "Performance" expander in results shows "Database: SQLite (Local)" or "Database: Snowflake (Production)".

### Q: Can I switch between databases mid-session?

**A:** Yes! Just change the selection in the sidebar. New queries will use the selected database.

### Q: My IP changes frequently. What should I do?

**A:**
- Use SQLite mode for development
- Or ask your admin to whitelist your IP range (e.g., `192.168.1.0/24`)
- Or use VPN for stable IP

## Additional Resources

- [Snowflake Network Policies Documentation](https://docs.snowflake.com/en/user-guide/network-policies)
- [SQLite Database Guide](database.py)
- [Setup Guide](SETUP_GUIDE.md)
- [Chart Feature Guide](CHART_FEATURE_GUIDE.md)

## Need Help?

If you're still having issues:

1. Check the error message carefully
2. Try SQLite mode first to rule out code issues
3. Verify your `.env` file has correct Snowflake credentials
4. Contact your Snowflake administrator
5. Check the app's console output for detailed error logs

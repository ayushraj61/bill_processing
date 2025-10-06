# Nominal Code (N/C) AI Matching for Other Processor

## 📋 What Was Implemented

### New Database Table: `nominal_code`
```sql
CREATE TABLE nominal_code (
    id SERIAL PRIMARY KEY,
    code VARCHAR UNIQUE NOT NULL,      -- e.g., '7550', '7905'
    object_name VARCHAR NOT NULL        -- e.g., 'Telephone and Fax', 'Card Processing Hardware'
);
```

**Populated with 142 nominal codes** from your standard accounting chart of accounts.

---

## 🎯 How It Works

### For **Itemize Mode** (Multiple Line Items):
- Each item's `Details` field is matched with nominal codes using **AI**
- AI compares description context with `object_name` from database
- If good match found → Sets `N/C` code
- If no match → Keeps `N/C` as `null`

**Example:**
```
Item 1: Details="SIM card monthly fee"     → AI matches → N/C='7550' (Telephone and Fax)
Item 2: Details="Office printer paper"     → AI matches → N/C='7902' (Stationery)
Item 3: Details="Grocery items"            → AI matches → N/C='5000' (Materials Purchased)
```

### For **Consolidate Mode** (Single Total):
- Same AI matching applied
- Since there's only 1 item, no conflicts possible
- AI matches the summary description to best nominal code

---

## 🤖 AI Matching Logic

### Process:
1. Load all 142 nominal codes from database
2. Send to Gemini AI with item description
3. AI analyzes context and meaning (not exact text match)
4. Returns best matching code or 'null'

### AI Prompt Example:
```
Given description: "Restaurant invoice"

Match to nominal codes:
5000: Materials Purchased
7550: Telephone and Fax
7902: Stationery
...

AI returns: "5000" (Materials Purchased)
```

---

## 📊 Sample Nominal Codes

| Code | Object Name |
|------|-------------|
| 5000 | Materials Purchased |
| 5002 | Miscellaneous Purchases |
| 7550 | Telephone and Fax (SIM fees) |
| 7902 | Stationery |
| 7905 | Card Processing Hardware |
| 8004 | Insurance |
| 8205 | Sundry Expenses |

**Total: 142 codes available**

---

## 🔧 Files Modified

### 1. `main.py` (lines 82-88)
- Added `nominal_code` table definition

### 2. `tools/seed_nominal_codes.py` (NEW)
- Seed script with 142 nominal codes
- **Already executed** ✅

### 3. `processors/other_processor.py` (lines 144-208, 413-420, 562-569)
- Added `_load_nominal_codes()` function
- Added `_match_description_to_nc_with_ai()` function
- Integrated AI matching in both Itemize and Consolidate modes

---

## 🎯 Usage

### Automatic (No Action Needed):
- When processing "Other" supplier bills
- AI automatically matches descriptions to N/C codes
- Console shows matches: `[AI N/C Match] 'description' → code`

### Console Output Example:
```
[AI N/C Match] 'Grocery and household items purchase' → 5000
[AI N/C Match] 'Monthly SIM card fee' → 7550
[AI N/C Match] 'Office supplies' → 7902
```

---

## 🔄 To Revert These Changes

If you want to go back to the previous state (without N/C matching):

1. **Remove N/C matching from other_processor.py:**
   ```bash
   # Comment out lines 413-420 (Itemize mode)
   # Comment out lines 562-569 (Consolidate mode)
   ```

2. **Optional: Drop table (if you want):**
   ```sql
   DROP TABLE nominal_code;
   ```

3. **Remove table definition from main.py:**
   ```python
   # Remove lines 82-88
   ```

I've noted this for you - just say **"revert N/C changes"** and I'll do it automatically.

---

## ✅ What Changed

**Before:**
```json
{
  "Details": "Restaurant invoice",
  "N/C": null          ❌ Always null
}
```

**After:**
```json
{
  "Details": "Restaurant invoice",
  "N/C": "5000"        ✅ AI matched to Materials Purchased
}
```

---

## 🧪 Test It

**Upload a new "Other" supplier bill:**
1. Dashboard processes it
2. Click "Itemize" or "Consolidate"
3. Check the `N/C` column
4. Should show matched codes instead of null!

**Check console for AI matching logs:**
```
[AI N/C Match] 'Grocery items' → 5000
```

---

## 📝 Notes

- **Only affects Other processor** (not BP Oil or Allstar)
- **Uses AI context matching** (not exact text matching)
- **Fallback to null** if no good match found
- **No conflicts** in Consolidate mode (only 1 item)
- **Per-item matching** in Itemize mode

Your N/C mapping is now intelligent and automated! 🎉


# Script Analysis: `clean_report.py`

### What exact problem is this script solving?
**Standardizes messy, uppercase text by fixing special characters ("ñ"), redacting sensitive numbers, and formatting it into readable paragraphs.**

---

### Line-by-Line Breakdown: "What would break if I remove this line?"

**Line 1-3: Imports (`re`, `textwrap`, `unicodedata`)**
```python
import re
import textwrap
import unicodedata
```
- **What breaks:** The entire script crashes with `NameError`.
- **Why it matters:** These are the tools. `re` redacts numbers. `textwrap` fixes the layout. `unicodedata` fixes the "ñ".

**Line 18: Normalization & Encoding**
```python
clean_text = unicodedata.normalize('NFKD', INPUT_TEXT).encode('ascii', 'ignore').decode('ascii')
```
- **What breaks:** The "ñ" in "CASTAÑACORP" either stays as a special character (potentially breaking old systems) or looks like garbage characters.
- **Why it matters:** This forces the text to be standard US-English ASCII (converts "ñ" -> "n"). Without it, you risk encoding errors in legacy databases.

**Line 22: Redaction**
```python
redacted = re.sub(r'\d', 'X', clean_text)
```
- **What breaks:** The numbers (7.47%, 0.7%, 2 million) remain visible.
- **Why it matters:** This is the privacy/security step. It turns "7.47%" into "X.XX%".

**Line 27: Title Case**
```python
formatted_text = redacted.replace('.', '.\n').title()
```
- **What breaks:** The text stays in SHOUTY UPPERCASE and doesn't break into new lines after sentences.
- **Why it matters:** `title()` makes it readable ("After The Close...") and `replace` ensures sentences don't run into each other.

**Line 30: Text Wrapping**
```python
final_result = textwrap.fill(formatted_text, width=80, replace_whitespace=False)
```
- **What breaks:** The output is printed as one massive string or preserves original messy line breaks.
- **Why it matters:** This fits the text for standard terminal/email width (80 chars), making it look like a professional document.

---

### What inputs does this script expect?
- **Hardcoded String:** A variable `INPUT_TEXT` inside the script itself.
- **Format:** Uppercase, possibly with special characters (UTF-8), containing numbers.

---

### What outputs does it produce?
**Console Text** that is:
1.  **Redacted:** All digits became 'X'
2.  **ASCII-safe:** special characters removed/converted ("Castañacorp" -> "Castanacorp")
3.  **Title Cased:** "AFTER" -> "After"
4.  **Wrapped:** Lines don't exceed 80 characters.

**Example Output:**
```
After The Close Of The Second Quarter, Our Company, Castanacorp
Has Achieved A Growth In The Revenue Of X.Xx%. This Is In Line
...
```

---

### What assumptions is the author making?

1.  **Language:** Input is English (or latin-based). `title()` works poorly on languages without capitalization rules.
2.  **Privacy Needs:** simple digit replacement ('X') is sufficient (doesn't hide that *some* number was there).
3.  **Encoding:** The user wants to *destroy* special characters ("ñ" -> "n") rather than preserve them. This assumes the output system CANNOT handle UTF-8.
4.  **Data Source:** Use case is small enough to hardcode data or paste it in. Not built for files yet.

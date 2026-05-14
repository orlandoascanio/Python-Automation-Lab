import re
import textwrap
import unicodedata

INPUT_TEXT = '''
AFTER THE CLOSE OF THE SECOND QUARTER, OUR COMPANY, CASTAÑACORP
HAS ACHIEVED A GROWTH IN THE REVENUE OF 7.47%. THIS IS IN LINE
WITH THE OBJECTIVES FOR THE YEAR. THE MAIN DRIVER OF THE SALES HAS BEEN
THE NEW PACKAGE DESIGNED UNDER THE SUPERVISION OF OUR MARKETING DEPARTMENT.
THE BOARD OUR EXPENSES HAS BEEN CONTAINED, INCREASING ONLY BY 0.7%, THOUGH
CONSIDERS IT NEEDS TO BE FURTHER REDUCED. THE EVALUATION IS SATISFACTORY
AND THE FORECAST FOR THE NEXT QUARTER IS OPTIMISTIC. THE BOARD EXPECTS
AN INCREASE IN PROFIT OF AT LEAST 2 MILLION DOLLARS.
'''

# 1. CLEANING & ASCII (Handling the 'ñ')
# NFKD decomposes characters; we then encode to ascii and ignore non-ascii bits
clean_text = unicodedata.normalize('NFKD', INPUT_TEXT).encode('ascii', 'ignore').decode('ascii')

# 2. REDACT NUMBERS (The Fast Way)
# \d matches any digit; [0-9]
redacted = re.sub(r'\d', 'X', clean_text)

# 3. FORMATTING (Title Case & Word Wrap)
# We use textwrap to ensure every line is exactly 80 chars max.
# We replace periods with ".\n" first to respect the book's paragraph rule.
formatted_text = redacted.replace('.', '.\n').title()

# fill() automatically breaks the text into beautiful 80-char lines
final_result = textwrap.fill(formatted_text, width=80, replace_whitespace=False)

print(final_result)
from bs4 import BeautifulSoup
import re

html = '''
<table><tbody><tr>
<td id="day-a" class="ContributionCalendar-day" data-date="2026-10-01" data-level="4"></td>
<td id="day-b" class="ContributionCalendar-day" data-date="2026-10-02" data-level="0"></td>
</tr></tbody></table>
<tool-tip for="day-a">17 contributions on October 1st.</tool-tip>
<tool-tip for="day-b">No contributions on October 2nd.</tool-tip>
'''

soup = BeautifulSoup(html, "html.parser")
cells = soup.select("td.ContributionCalendar-day[data-date][data-level]")
assert len(cells) == 2

tooltips = {}
for tip in soup.find_all("tool-tip"):
    m = re.search(r"([\d,]+)\s+contribution", tip.get_text(" ", strip=True))
    if m:
        tooltips[tip.get("for")] = int(m.group(1).replace(",", ""))

assert tooltips["day-a"] == 17
assert cells[0]["data-date"] == "2026-10-01"
assert cells[0]["data-level"] == "4"
print("Parser test passed.")

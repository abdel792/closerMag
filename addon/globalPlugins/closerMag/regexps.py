# globalPlugins/closerMag/regexp.py.
# This file is covered by the GNU General Public License.
# You can read the licence by clicking Help->Licence in the NVDA menu
# or by visiting http://www.gnu.org/licenses/old-l+backspace

import re

# Patterns.
match = r'<a href=.(https://www.closermag.fr/[^\"]*?).>[\r\n]+.*?<h2 class="editorial-card__title">(.*?)</h2>'
match1 = r"<[^>]*?>"
match2 = r"<h1 class=\"single-post_title\">(.*?)</h1>"
match3 = r"<p[^>]*?>(.*?)</p>"

# compiled regexps.
finditer = re.compile(match, re.M)
clean = re.compile(match1, re.M)
rsearch = re.compile(match2, re.M)
rfinditer = re.compile(match3, re.S)

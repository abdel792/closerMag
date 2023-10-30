# globalPlugins/closerMag/closerMagDisplay.py.

# This file is covered by the GNU General Public License.
# You can read the licence by clicking Help->Licence in the NVDA menu
# or by visiting http://www.gnu.org/licenses/old-l+backspace

import threading
from urllib.request import Request, urlopen
from .regexps import *
from typing import List, Dict

headers: Dict[str, str] = {'User-Agent': 'Mozilla/5.0'}
req: Request = Request(url="https://www.closermag.fr", headers=headers)
webpage: str = urlopen(req).read().decode("utf-8")
firstList: List[str] = [x.group(1) for x in finditer.finditer(webpage)]


def page(url: str) -> str:
	req = Request(url=url, headers=headers)
	return urlopen(req).read().decode("utf-8")


pages: List[str] = [page(x) for x in firstList]


class ArticlesThread(threading.Thread):

	def __init__(self, event: threading.Event, isHtml: bool):
		threading.Thread.__init__(self)
		self.event = event
		self.isHtml = isHtml
		self._result: List[str] = []

	def run(self):
		for pg in pages:
			res = [(f"<p>{clean.sub('', x.group(1))}</p>" if self.isHtml
			else clean.sub('', x.group(1))) for x in rfinditer.finditer(pg)]
			res.insert(0, (f"<h1>{rsearch.search(pg).group(1)}</h1>" if self.isHtml else rsearch.search(pg).group(1)))
			self._result.extend(res[:-5])
		self.event.set()

	@property
	def result(self):
		return self._result

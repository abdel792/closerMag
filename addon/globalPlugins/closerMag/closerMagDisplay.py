# globalPlugins/closerMag/closerMagDisplay.py.
# This file is covered by the GNU General Public License.
# You can read the licence by clicking Help->Licence in the NVDA menu
# or by visiting http://www.gnu.org/licenses/old-l+backspace

import threading
from urllib.request import Request, urlopen
from .regexps import *

headers = {'User-Agent': 'Mozilla/5.0'}
req = Request(url="https://www.closermag.fr", headers=headers)
webpage = urlopen(req).read().decode("utf-8")
randomList = [[x.group(1), clean.sub("", x.group(2))] for x in finditer.finditer(webpage)]
firstList = []


class FirstListThread(threading.Thread):

	def __init__(self, event):
		threading.Thread.__init__(self)
		self.event = event

	def run(self):
		for item in randomList:
			if isinstance(item, list):
				firstList.extend(item)
		self.event.set()


class ArticlesThread(threading.Thread):

	def __init__(self, event, isHtml):
		threading.Thread.__init__(self)
		self.event = event
		self.isHtml = isHtml
		self._result = []

	def run(self):
		for item in firstList:
			if item.startswith("https://"):
				req = Request(url=item, headers=headers)
				pg = urlopen(req).read().decode("utf-8")
				res = [(f"<p>{clean.sub('', x.group(1))}</p>" if self.isHtml
				else clean.sub('', x.group(1))) for x in rfinditer.finditer(pg)]
				res.insert(0, (f"<h1>{rsearch.search(pg).group(1)}</h1>" if self.isHtml else rsearch.search(pg).group(1)))
				self._result.extend(res[:-5])
		self.event.set()

	@property
	def result(self):
		return self._result

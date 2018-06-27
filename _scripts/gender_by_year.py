import occ
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

coder = occ.Coder()
coder.loadPreviouslyCoded("codingAll")

if False:
    # if you need to code these...
    coder.codeAll(["gender", "date"])
    coder.dumpCodes("codingAll")

# plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
# plt.gca().xaxis.set_major_locator(mdates.YearLocator())
# plt.gca().xaxis.set_major_locator(mdates.MonthLocator())

fcount = occ.Counter(y['date'].year for y in coder.obituaries if y['gender'] == 'female')
mcount = occ.Counter(y['date'].year for y in coder.obituaries if y['gender'] == 'male')

xs = sorted(list(set( list(fcount.keys()) + list(mcount.keys()) )))
ym = [ mcount[x] / (mcount[x]+fcount[x]) for x in xs ]
yf = [ fcount[x] / (mcount[x]+fcount[x]) for x in xs ]

fig, ax = plt.subplots()
ax.area(xs, ym, yf, labels=['male', 'female'])
ax.legend(loc='lower right')
plt.show()

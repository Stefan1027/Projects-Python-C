import csv
from collections import defaultdict
from pprint import pprint
from cycler import cycler
import matplotlib.pyplot as plt

def def_dict_conv(d):
    if isinstance(d, defaultdict):
        d = {k: def_dict_conv(v) for k, v in d.iteritems()}
    return d

nested_dict = lambda: defaultdict(nested_dict)

results = nested_dict()
cache_sizes = ['8','16','32','64']

colors = ['r', 'b', 'k', 'g']


for cache in ['dcache','icache']:
	for benchmark in ['crc','sha']:
		for x in cache_sizes:
			if cache == 'icache' and x == '64': continue
			with open('./{benchmark}/{cache}/{size}/stats.txt'.format(benchmark=benchmark,cache=cache,size=x)) as f:
				instructions = 0
				cycles = 0
				data = csv.reader(f, delimiter=' ', skipinitialspace=True)
				for row in data:
					if not len(row):
						continue
					if row[0] == 'system.cpu.committedInsts':
						instructions = int(row[1])
					elif row[0] == 'system.cpu.numCycles':
						cycles = int(row[1])
				
				result = {
					'instructions'  : instructions,
					'cycles'		: cycles,
					'ipc'			: float(instructions)/float(cycles)
				}

				results[cache][benchmark][x] = result		

idx = 0
for benchmark in ['crc', 'sha']:
	plt.figure(benchmark)
	plots = []
	for cache in ['dcache', 'icache']:
		plt_data = []

		for x in cache_sizes:
			if cache == 'icache' and x == '64': continue
			plt_data.append(results[cache][benchmark][x]['ipc'])

		print idx
		plots.append(plt.plot([int(x) for x in cache_sizes][:len(plt_data)],plt_data, label='{cache}'.format(cache=cache, benchmark=benchmark),color=colors[idx],marker='o',linestyle='-'))
		idx += 1
	plt.legend(loc='southeast')
	plt.legend(loc='southeast')
	plt.ylabel('Instructions per cycle (IPC)')
	plt.xlabel(cache + ' size in kB')
	plt.title('Performance of {} benchmark with varying {} size'.format(benchmark,cache))


pprint(def_dict_conv(results))



plt.show()

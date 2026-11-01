import subprocess
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys

COMPOSE_POST_LUA = './wrk2/scripts/social-network/compose-post.lua'
COMPOSE_POST_REST = 'http://localhost:8080/wrk2-api/post/compose'
READ_USER_TIMELINE_LUA = './wrk2/scripts/social-network/read-user-timeline.lua'
READ_USER_TIMELINE_REST = 'http://localhost:8080/wrk2-api/user-timeline/read'

WRK = '../wrk2/wrk -D exp -t 12 -c 100 -T 10s'


def parse_wrk2_output(text):
    result = {}
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split()

        if parts[0] == 'Latency':
            if len(parts) >= 4:
                avg_ms = parts[1].replace('ms', '').replace(',', '')
                p99_ms = parts[3].replace('ms', '').replace(',', '')
                result['avg_latency_ms'] = float(avg_ms)
                result['p99_latency_ms'] = float(p99_ms)

    return result


def plot_results(parsed, out_path):
    rps      = [p['rps'] for p in parsed]
    avg_lat  = [p['avg_latency_ms'] for p in parsed]
    p99_lat  = [p['p99_latency_ms'] for p in parsed]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(rps, avg_lat, marker='o', label='avg latency (ms)', color='tab:blue')
    ax.plot(rps, p99_lat, marker='s', label='p99 latency (ms)', color='tab:red')

    ax.set_xlabel('rps')
    ax.set_ylabel('latency (ms)')
    ax.set_yscale('log')
    ax.set_title('latency of read-user-timeline workload')
    ax.grid(True, which='both', alpha=0.3)
    ax.legend(loc='upper left')
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f'saved {out_path}')


def prepare(dur, rps):
	subprocess.run(f'{WRK} -d {dur}s -R {rps} -s {READ_USER_TIMELINE_LUA} {READ_USER_TIMELINE_REST} > /dev/null', shell=True, text=True)

def run_queries(dur, rps):
	result = subprocess.run(f'{WRK} -d {dur}s -R {rps} -s {READ_USER_TIMELINE_LUA} {READ_USER_TIMELINE_REST} | grep -A 6 -- \'Test Results\'', shell=True, text=True, capture_output=True)
	return parse_wrk2_output(result.stdout)


prepare(60, 500)

parsed = []

for i in range(10):
	rps = int(3000 * 1.1 ** i)
	print(f'RPS {rps}')
	cur = run_queries(60, rps)
	cur['rps'] = rps
	parsed.append(cur)
	time.sleep(30)


plot_results(parsed, '../../examples/minimal/latency_rps.png')

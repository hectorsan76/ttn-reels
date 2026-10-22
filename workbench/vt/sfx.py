"""Synthesize the kept TTN sound effects as 44.1 kHz mono wavs (free, made here, no licence issues)."""
import numpy as np, soundfile as sf, os
SR = 44100
def env(n, a, d):
    t = np.arange(n) / SR; e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-np.maximum(0, t - a) / d); return e
def noise(n): return np.random.default_rng(1).uniform(-1, 1, n)
def bandsweep(x, f0, f1):
    # crude moving band: mix lowpassed versions
    out = np.zeros_like(x); n = len(x); seg = 512
    for i in range(0, n, seg):
        f = f0 * (f1 / f0) ** (i / n); k = max(1, int(SR / f / 2))
        c = x[max(0, i - k):i + seg]; c = np.convolve(c, np.ones(k) / k, 'same')[-min(seg, n - i):]
        out[i:i + len(c)] = c
    return out - np.convolve(out, np.ones(40) / 40, 'same') * .5
def save(name, y, g=.8):
    y = y / (np.abs(y).max() + 1e-9) * g; sf.write(f'sfx/{name}.wav', y.astype(np.float32), SR)
os.makedirs('sfx', exist_ok=True)
n = int(SR * .6); t = np.arange(n) / SR
save('whoosh', bandsweep(noise(n), 300, 4000) * np.sin(np.pi * np.minimum(1, t / .6)) ** 1.5, .55)
n = int(SR * .3); t = np.arange(n) / SR
save('swipe', bandsweep(noise(n), 2500, 7000) * env(n, .04, .1), .4)
n = int(SR * .08); t = np.arange(n) / SR
save('tap', (noise(n) * .5 + np.sin(2 * np.pi * 1800 * t)) * env(n, .001, .02), .55)
n = int(SR * 1.0); t = np.arange(n) / SR
f = 120 * (45 / 120) ** np.minimum(1, t / .35)
save('bass', np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, .005, .35), .9)
n = int(SR * .9); t = np.arange(n) / SR
save('ping', np.sin(2 * np.pi * 1568 * t) * env(n, .003, .25) + np.concatenate([np.zeros(int(SR * .09)), (np.sin(2 * np.pi * 2093 * t) * env(n, .003, .3))[:n - int(SR * .09)]]), .45)
n = int(SR * 1.4); t = np.arange(n) / SR; y = np.zeros(n)
for i, fq in enumerate([523, 659, 784, 1047]):
    o = int(SR * .08 * i); y[o:] += (np.sin(2 * np.pi * fq * t) * env(n, .003, .35))[:n - o]
save('chime', y, .45)
n = int(SR * .7); t = np.arange(n) / SR
pulse = ((t < .2) | ((t > .32) & (t < .52))).astype(float)
save('buzz', np.sign(np.sin(2 * np.pi * 150 * t)) * pulse * .6, .35)
print('ok', sorted(os.listdir('sfx')))

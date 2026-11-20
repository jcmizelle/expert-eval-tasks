"""Directed phase transfer entropy (dPTE). Python version of the logic in SMILe_PhaseTE (J.C. Mizelle).
Lobier et al. 2014 NeuroImage (PTE); Hillebrand et al. 2016 PNAS (dPTE, delay rule).
PTE_xy = H(Py(t),Py(t-d)) + H(Py(t-d),Px(t-d)) - H(Py(t-d)) - H(Py(t),Py(t-d),Px(t-d))
dPTE_xy = PTE_xy / (PTE_xy + PTE_yx); >0.5 means x leads y, 0.5 = no preferred direction.
Phases from Hilbert transform of band-passed data; bin width by Scott's rule; delay
d = round(Ns*Nch / N_flips), N_flips = number of phase sign changes over all channels and samples.
"""
import numpy as np

def _ent(*cols, nb):
    code = np.zeros(cols[0].shape[0], dtype=np.int64)
    for c in cols:
        code = code * nb + c
    p = np.bincount(code).astype(float); p = p[p > 0] / code.size
    return -np.sum(p * np.log(p))

def delay(phase):
    nch, ns = phase.shape
    flips = np.count_nonzero(np.diff(np.sign(phase), axis=1))
    return max(1, int(round(ns * nch / flips)))

def dpte(phase, d=None):
    """phase: (n_ch, n_samples) instantaneous phase in radians. Returns dPTE (n_ch x n_ch), PTE, delay."""
    nch, ns = phase.shape
    d = d or delay(phase)
    h = 3.49 * np.mean(np.std(phase, axis=1)) * ns ** (-1 / 3)        # Scott's rule
    nb = int(np.ceil(2 * np.pi / h))
    b = np.clip(((phase + np.pi) / (2 * np.pi) * nb).astype(np.int64), 0, nb - 1)
    fut, past = b[:, d:], b[:, :-d]
    pte = np.zeros((nch, nch))
    Hp = [_ent(past[k], nb=nb) for k in range(nch)]
    Hfp = [_ent(fut[k], past[k], nb=nb) for k in range(nch)]
    for x in range(nch):
        for y in range(nch):
            if x == y: continue
            pte[x, y] = Hfp[y] + _ent(past[y], past[x], nb=nb) - Hp[y] - _ent(fut[y], past[y], past[x], nb=nb)
    den = pte + pte.T
    with np.errstate(invalid='ignore', divide='ignore'):
        dp = np.where(den > 0, pte / den, 0.5)
    np.fill_diagonal(dp, 0.5)
    return dp, pte, d

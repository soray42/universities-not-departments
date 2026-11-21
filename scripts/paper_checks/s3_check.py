# Numerical checks of Proposition S3 / Lemma S4 of the Supplementary Information (ordinary ranks versus normal
# scores); part 5 evaluates them field by field on the FIELD_VS_GENERIC_RESULT.md table of scripts/28.
import numpy as np, re, sys
from scipy.stats import rankdata, norm
from scipy.optimize import minimize

g = lambda r: 6/np.pi*np.arcsin(np.asarray(r)/2)
ginv = lambda p: 2*np.sin(np.pi*np.asarray(p)/6)
gp = lambda r: (3/np.pi)/np.sqrt(1-np.asarray(r)**2/4)
B = lambda u, v: g(u*v) - g(u)*g(v)

# 1. referee counterexample, population
rFG, rGY, rFY = 0.8, 0.6, 0.48
d = rFY - rFG*rGY
dR = g(rFY) - g(rFG)*g(rGY)
print("gauss partial cov", d, " rank residual cov (population)", dR, " B", B(rGY, rFG))
print("g values", g(rFG), g(rGY), g(rFY))
print("rank sr_F = dR/sin", dR/np.sqrt(1-g(rFG)**2))

# 2. simulation n = 1e6, several seeds
C = np.array([[1, rFG, rFY], [rFG, 1, rGY], [rFY, rGY, 1]])
L = np.linalg.cholesky(C)
n = 10**6
def stdz(x): return (x - x.mean())/x.std()
out = []
for seed in range(10):
    rng = np.random.default_rng(seed)
    Z = rng.standard_normal((n, 3)) @ L.T
    F, G, Y = Z.T
    R = [stdz(rankdata(v)) for v in (F, G, Y)]
    N = [stdz(norm.ppf((rankdata(v) - 0.375)/(n + 0.25))) for v in (F, G, Y)]
    def rescov(F_, G_, Y_):
        cfg = np.mean(F_*G_); res = F_ - cfg*G_
        return np.mean(res*Y_), np.mean(res*Y_)/np.sqrt(np.mean(res**2))
    a = rescov(*R); b = rescov(*N)
    out.append((a[0], a[1], b[0], b[1]))
    print(f"seed {seed}: ranks rescov {a[0]:+.5f} sr {a[1]:+.5f} | Blom rescov {b[0]:+.5f} sr {b[1]:+.5f}")
o = np.array(out)
print("mean over 10 seeds", o.mean(0), "sd", o.std(0, ddof=1))

# 3. global max of B on the unit square, CS bound check
u = np.linspace(0, 1, 2001)
U, V = np.meshgrid(u, u)
BB = B(U, V)
i = np.unravel_index(BB.argmax(), BB.shape)
print("max B on [0,1]^2", BB.max(), "at u,v", U[i], V[i], " min", BB.min())
CS = np.sqrt(np.maximum(B(U, U), 0)*np.maximum(B(V, V), 0))
print("CS bound violated anywhere:", np.any(BB > CS + 1e-15), " max (CS - B)", (CS-BB).max())
print("simple bound (1-3/pi) uv violated:", np.any(BB > (1-3/np.pi)*U*V + 1e-15))
# max over v of B(u,v) for fixed u etc
print("B(u,u) max", B(u, u).max(), "at", u[B(u, u).argmax()])

# 4. empirical box (Spearman values) -> Gaussian r
for cg_s in (0.35, 0.40, 0.42, 0.45):
    for cos_s in (0.80, 0.81, 0.85, 0.90):
        cg, cs = ginv(cg_s), ginv(cos_s)
        b = B(cg, cs); cs_b = np.sqrt(B(cg, cg)*B(cs, cs))
        sinR = np.sqrt(1 - cos_s**2)
        print(f"rho_G {cg_s:.2f} rho_FG {cos_s:.2f} -> r_G {cg:.4f} cos {cs:.4f}: B {b:.5f} CSbound {cs_b:.5f} "
              f"B/sinR (sr bias) {b/sinR:.5f}; B at spearman values {B(cg_s, cos_s):.5f}")
# g' range
print("g' at 0, 0.5, 1:", gp(0), gp(0.5), gp(1.0))
# max of ginv(p) - p
p = np.linspace(0, 1, 100001); dd = ginv(p) - p
print("max ginv(p)-p", dd.max(), "at", p[dd.argmax()])

# 5. per-field
txt = open(str(__import__('pathlib').Path(__file__).resolve().parents[2]) + '/FIELD_VS_GENERIC_RESULT.md').read()
sec = txt.split('Fields ranked by field-reputation advantage')[1].split('## B2')[0]
rows = re.findall(r"\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|\s*([+-]\d\.\d\d)\s*\|\s*([+-]\d\.\d\d)\s*\|\s*([+-]\d\.\d\d)\s*\|\s*([+-]\d\.\d\d)\s*\|", sec)
cF = np.array([float(r[2]) for r in rows]); cG = np.array([float(r[3]) for r in rows]); rPP = np.array([float(r[5]) for r in rows])
print("fields", len(rows), "mean cF cG rhoPP", cF.mean(), cG.mean(), rPP.mean())
cGg, cosg, cFg = ginv(cG), ginv(rPP), ginv(cF)
Bf = B(cGg, cosg)
sinR = np.sqrt(1 - rPP**2)
print("per-field B: mean", Bf.mean(), "min", Bf.min(), "max", Bf.max(), "median", np.median(Bf))
print("per-field B/sinR (rank sr_F bias): mean", (Bf/sinR).mean(), "max", (Bf/sinR).max())
# exact rank-scale decomposition check: dR = g'(zeta) d + B ; recover gauss d from rank values
dR = cF - cG*rPP
d = cFg - cGg*cosg
print("mean rank resid cov dR", dR.mean(), " mean gauss resid cov d", d.mean(), " mean (dR - d)", (dR-d).mean())
print("mean c_F - c_G ranks", (cF-cG).mean(), " gauss", (cFg-cGg).mean())
# sr_F
srR = dR/sinR; srg = d/np.sqrt(1-cosg**2)
print("mean sr_F ranks", srR.mean(), " gauss", srg.mean(), " threshold ranks mean c_G tan(th/2)", (cG*np.tan(np.arccos(rPP)/2)).mean())
# sign agreements
print("sign(dR) == sign(d) in", np.sum(np.sign(dR) == np.sign(d)), "of", len(d))
print("fields with |B| > |dR|:", np.sum(np.abs(Bf) > np.abs(dR)))

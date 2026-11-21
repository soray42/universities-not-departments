# Lemma S4 of the Supplementary Information evaluated field by field at data/interim/field_vs_generic.csv (scripts/28).
import numpy as np, pandas as pd
g = lambda r: 6/np.pi*np.arcsin(np.asarray(r)/2)
ginv = lambda p: 2*np.sin(np.pi*np.asarray(p)/6)
B = lambda u, v: g(u*v) - g(u)*g(v)
t = pd.read_csv(str(__import__('pathlib').Path(__file__).resolve().parents[2]) + '/data/interim/field_vs_generic.csv')
cF, cG, rPP = t.c_F.to_numpy(), t.c_G.to_numpy(), t.rho_PP.to_numpy()
print("fields", len(t), "mean cF", cF.mean(), "cG", cG.mean(), "rhoPP", rPP.mean(), "min/max rhoPP", rPP.min(), rPP.max())
cFg, cGg, cosg = ginv(cF), ginv(cG), ginv(rPP)
Bf = B(cGg, cosg); sR = np.sqrt(1-rPP**2)
print("B: mean %.4f median %.4f min %.4f max %.4f" % (Bf.mean(), np.median(Bf), Bf.min(), Bf.max()))
print("B/sinR: mean %.4f max %.4f ; B/sinR^2 mean %.4f max %.4f" % ((Bf/sR).mean(), (Bf/sR).max(), (Bf/sR**2).mean(), (Bf/sR**2).max()))
dR = cF - cG*rPP; d = cFg - cGg*cosg
print("mean resid cov ranks %.4f gauss %.4f" % (dR.mean(), d.mean()))
print("mean ADV ranks %.4f gauss %.4f ; sign agree %d/%d" % ((cF-cG).mean(), (cFg-cGg).mean(), np.sum(np.sign(cF-cG)==np.sign(cFg-cGg)), len(t)))
srR = dR/sR; srg = d/np.sqrt(1-cosg**2); thrR = cG*np.tan(np.arccos(rPP)/2); thrg = cGg*np.tan(np.arccos(cosg)/2)
print("mean sr ranks %.4f gauss %.4f ; mean threshold ranks %.4f gauss %.4f" % (srR.mean(), srg.mean(), thrR.mean(), thrg.mean()))
print("fields where F out-predicts: ranks %d gauss %d" % (np.sum(srR > thrR), np.sum(srg > thrg)))
print("fields with c_G<0:", np.sum(cG < 0), " B<0:", np.sum(Bf < 0))

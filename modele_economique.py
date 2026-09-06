# Modèle économique — établissement pilote type
S = 10_000          # sortants éligibles/an (hospit. complète, hors ambu/décès/palliatifs)
TAUX = 0.11         # taux de réadmission 30j
READM = S * TAUX

# Performance modèle (Partie 2, jeu de test)
scen = {
    '10%': {'capa':0.10, 'rappel':0.246, 'lift':2.46},
    '20%': {'capa':0.20, 'rappel':0.383, 'lift':1.92},
    '30%': {'capa':0.30, 'rappel':0.509, 'lift':1.70},
}
EFF = 0.20          # efficacité du protocole (réduction relative du risque chez les suivis)

# Coûts unitaires du suivi
C_RENF, C_INTER = 45, 12   # € par patient (temps soignant chargé)
H_RENF, H_INTER = 1.33, 0.33  # heures soignant par patient
ETP_H = 1500        # heures productives / ETP / an

# Valorisation d'une réadmission évitée
DEFICIT = 600       # déficit direct moyen d'un séjour non programmé (coût complet - recette)
DMS = 4.8           # journées-lit libérées
MARGE_JOUR = 320    # marge contributive / journée-lit réallouée à l'activité programmée
VAL = DEFICIT + DMS * MARGE_JOUR

print(f"Réadmissions/an: {READM:.0f} | Valeur d'une réadmission évitée: {VAL:.0f} EUR\n")
print(f"{'Scénario':10} {'Suivis':>7} {'Détectées':>10} {'Évitées':>8} {'Coût suivi':>12} {'Gains':>12} {'Marge':>12} {'ETP':>5}")
res = {}
for k,v in scen.items():
    suivis = S * v['capa']
    det = READM * v['rappel']
    evit = det * EFF
    if v['capa'] <= 0.10:
        cout = suivis * C_RENF; heures = suivis * H_RENF
    else:
        n_r = S*0.10; n_i = suivis - n_r
        cout = n_r*C_RENF + n_i*C_INTER; heures = n_r*H_RENF + n_i*H_INTER
    gains = evit * VAL
    res[k] = dict(suivis=suivis, det=det, evit=evit, cout=cout, gains=gains,
                  marge=gains-cout, etp=heures/ETP_H)
    print(f"{k:10} {suivis:7.0f} {det:10.0f} {evit:8.0f} {cout:12,.0f} {gains:12,.0f} {gains-cout:12,.0f} {heures/ETP_H:5.2f}")

# CAPEX
capex = {'RH projet (12 mois)':215_000, 'Infrastructure HDS & intégration SIH':60_000,
         'Conformité (AIPD, AI Act, audit)':45_000, 'Conduite du changement & formation':30_000}
CAPEX = sum(capex.values())
print(f"\nCAPEX total: {CAPEX:,} EUR")
for k,v in capex.items(): print(f"  {k}: {v:,}")

# OPEX récurrent (hors suivi) - établissement pilote
opex_fixe = {'Hébergement HDS & exploitation':24_000, 'MLOps / réentraînement (0,3 ETP)':25_000,
             'Audit & conformité annuelle':10_000}
OPEX_FIXE = sum(opex_fixe.values())
SUIVI = res['20%']['cout']
print(f"\nOPEX fixe: {OPEX_FIXE:,} | Suivi (scén. 20%): {SUIVI:,.0f} | OPEX total: {OPEX_FIXE+SUIVI:,.0f}")

# Flux 5 ans, scénario central 20%, pilote
G = res['20%']['gains']
print(f"\n{'Année':>6} {'Gains':>10} {'CAPEX':>10} {'OPEX':>10} {'Net':>10} {'Cumul':>11}")
cum = 0
for a in range(0,6):
    if a==0: g, cx, ox = 0, CAPEX, 0
    elif a==1: g, cx, ox = G*0.5, 0, OPEX_FIXE+SUIVI*0.5   # montée en charge
    else: g, cx, ox = G, 0, OPEX_FIXE+SUIVI
    net = g-cx-ox; cum += net
    print(f"{a:>6} {g:10,.0f} {cx:10,.0f} {ox:10,.0f} {net:10,.0f} {cum:11,.0f}")

# Coût par réadmission évitée
print(f"\nCoût par réadmission évitée (régime établi, pilote): {(OPEX_FIXE+SUIVI)/res['20%']['evit']:,.0f} EUR")

# ============ EXTRAPOLATION GROUPE ============
print("\n" + "="*70)
N = 30                      # établissements MCO France du périmètre
CAPEX_PLATEFORME = 350_000  # mutualisé (déjà engagé par le pilote)
CAPEX_PAR_ETAB = 25_000     # intégration locale + formation
CAPEX_G = CAPEX_PLATEFORME + N*CAPEX_PAR_ETAB
OPEX_PLATEFORME_G = 150_000 # hébergement + MLOps mutualisés à l'échelle
SUIVI_G = SUIVI * N
OPEX_G = OPEX_PLATEFORME_G + SUIVI_G
GAINS_G = G * N
print(f"GROUPE ({N} établissements)")
print(f"  CAPEX: {CAPEX_G:,.0f} (plateforme {CAPEX_PLATEFORME:,} + {N}x{CAPEX_PAR_ETAB:,})")
print(f"  OPEX/an: {OPEX_G:,.0f} (plateforme {OPEX_PLATEFORME_G:,} + suivi {SUIVI_G:,.0f})")
print(f"  Gains/an: {GAINS_G:,.0f} | Marge/an: {GAINS_G-OPEX_G:,.0f}")
print(f"  Réadmissions évitées/an: {res['20%']['evit']*N:,.0f}")

print(f"\n{'Année':>6} {'Gains':>11} {'CAPEX':>10} {'OPEX':>11} {'Net':>11} {'Cumul':>12}")
cum = 0; flux=[]
for a in range(0,6):
    if a==0:   g,cx,ox = 0, CAPEX_PLATEFORME, 0
    elif a==1: g,cx,ox = GAINS_G*0.15, N*CAPEX_PAR_ETAB*0.5, OPEX_PLATEFORME_G+SUIVI_G*0.15
    elif a==2: g,cx,ox = GAINS_G*0.60, N*CAPEX_PAR_ETAB*0.5, OPEX_PLATEFORME_G+SUIVI_G*0.60
    else:      g,cx,ox = GAINS_G, 0, OPEX_G
    net=g-cx-ox; cum+=net; flux.append((a,g,cx,ox,net,cum))
    print(f"{a:>6} {g:11,.0f} {cx:10,.0f} {ox:11,.0f} {net:11,.0f} {cum:12,.0f}")

# ROI 5 ans
inv_tot = sum(f[2]+f[3] for f in flux); gain_tot = sum(f[1] for f in flux)
print(f"\nROI 5 ans: {(gain_tot-inv_tot)/inv_tot*100:.1f}% | Coûts cumulés {inv_tot:,.0f} | Gains cumulés {gain_tot:,.0f}")

# ============ SENSIBILITÉ ============
print("\n" + "="*70 + "\nSENSIBILITÉ (régime établi, groupe, marge annuelle)")
def marge_groupe(eff=EFF, val=VAL, adoption=1.0, capa='20%'):
    evit = READM*scen[capa]['rappel']*eff*adoption
    gains = evit*val*N
    suivi = res[capa]['cout']*N
    return gains - (OPEX_PLATEFORME_G + suivi), evit*N

cas = [
 ("Central (eff. 20%, réallocation lit)", dict()),
 ("Efficacité protocole 10%", dict(eff=0.10)),
 ("Efficacité protocole 30%", dict(eff=0.30)),
 ("Adoption praticiens 60%", dict(adoption=0.60)),
 ("Lit NON réalloué (déficit seul, 600 EUR)", dict(val=600)),
 ("PESSIMISTE: eff.10% + adoption 60%", dict(eff=0.10, adoption=0.60)),
 ("PESSIMISTE MAX: eff.10%, adopt.60%, lit non réalloué", dict(eff=0.10, adoption=0.60, val=600)),
 ("Capacité 10% (ciblage plus serré)", dict(capa='10%')),
 ("Capacité 30%", dict(capa='30%')),
]
for nom, kw in cas:
    m, e = marge_groupe(**kw)
    print(f"  {nom:52} marge {m:11,.0f} EUR/an | {e:5.0f} évitées")

print("\n" + "="*70 + "\nSEUILS CRITIQUES (groupe, régime établi)")
import numpy as np
# Efficacité minimale pour marge nulle (scénario central de valorisation)
for capa in ['10%','20%','30%']:
    suivi = res[capa]['cout']*N
    denom = READM*scen[capa]['rappel']*VAL*N
    eff_min = (OPEX_PLATEFORME_G + suivi)/denom
    print(f"  Capacité {capa}: efficacité minimale du protocole = {eff_min:.1%}")
# Valorisation minimale d'une réadmission évitée (eff. 20%, capa 20%)
val_min = (OPEX_PLATEFORME_G + SUIVI_G)/(READM*scen['20%']['rappel']*EFF*N)
print(f"  Valorisation minimale d'une réadmission évitée (eff.20%, capa 20%) = {val_min:,.0f} EUR")
print(f"  Coût par réadmission évitée (groupe, régime établi) = {(OPEX_PLATEFORME_G+SUIVI_G)/(res['20%']['evit']*N):,.0f} EUR")
# Marge par journée-lit minimale
mj_min = (val_min - DEFICIT)/DMS
print(f"  Marge contributive minimale par journée-lit réallouée = {mj_min:,.0f} EUR/jour")

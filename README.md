# Prédiction des réadmissions hospitalières à 30 jours par Machine Learning

**Mémoire de Master 2 — Chef de Projet en Intelligence Artificielle, Eugenia School (2025-2026)**
Cas d'application : Ramsay Santé · Dataset : *Diabetes 130-US Hospitals (1999-2008)*, UCI Machine Learning Repository

## Objectif

Identifier, au moment de la sortie d'hospitalisation, les patients à risque de réadmission
non programmée à 30 jours, afin de cibler les ressources de suivi post-hospitalisation
(classification supervisée binaire sur données fortement déséquilibrées, sous contrainte
d'interprétabilité clinique).

## Résultats clés

| Indicateur | Valeur |
|---|---|
| Cohorte de modélisation | 69 987 patients uniques (taux de réadmission : 8,98 %) |
| Modèle retenu | XGBoost (sélection sur métriques indépendantes du seuil) |
| AUC-ROC (test) / validation croisée | 0,659 / 0,644 ± 0,006 |
| **Lift à 10 % de capacité de suivi** | **2,46** (24,6 % des réadmissions captées en suivant 10 % des sortants) |
| Interprétabilité | SHAP global + explications individuelles (waterfall) |
| Équité | AUC homogènes par sous-groupes (écart max ≈ 0,04) |

## Contenu du dépôt

- `memoire_readmission_hospitaliere.ipynb` — pipeline complet : contrôle des données,
  EDA, préparation, feature engineering, benchmark de 5 configurations (LR, RF, XGBoost,
  pondération, SMOTE), validation croisée, comparaison de lift, calibrage du seuil par
  capacité opérationnelle, scénarios, SHAP, analyse d'équité.
- `modele_economique.py` — modèle économique de la Partie 4 du mémoire : CAPEX/OPEX,
  projections à 5 ans (établissement pilote et groupe), analyse de sensibilité, seuils
  critiques. Tous les paramètres sont explicités en tête de script.
- `resultats/` — tableaux exportés par le notebook (benchmark, scénarios, comparaison
  de lift, importances SHAP, équité).

## Reproduire les résultats

1. Télécharger le dataset : https://archive.ics.uci.edu/dataset/296/ (fichier `diabetic_data.csv`,
   à placer à la racine ou adapter le chemin en section 1 du notebook).
2. `pip install -r requirements.txt`
3. Exécuter le notebook de haut en bas (graine aléatoire fixée à 42 — résultats reproductibles).
4. `python modele_economique.py` pour les tableaux économiques.

## Avertissement

Travail académique de validation méthodologique sur données publiques. Les hypothèses
économiques sont paramétriques (référentiels publics ATIH/ENC) et non issues de données
internes de Ramsay Santé. Aucune donnée patient réelle n'est utilisée.

# pré-traitement des données pour un affichage plus rapide dans heroku
from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen
import pandas as pd
import pickle as pkl
import numpy as np

# resp = urlopen(
#     "https://www.insee.fr/fr/statistiques/fichier/2540004/nat2024_csv.zip")
# zipfile = ZipFile(BytesIO(resp.read()))
# df_nat = pd.read_csv(zipfile.open(zipfile.namelist()[0]), ';')

df_nat = pd.read_parquet("/Users/eliebondu/Downloads/prenoms-2024.parquet")
# On ne garde que les lignes au niveau france pour l'instant
df_nat = df_nat[df_nat.niveau_geographique == "FRANCE"]
# Changement du type annais pour qu'il soit entier , et mise à Nan des 'XXXX'
df_nat['periode'] = pd.to_numeric(df_nat.periode, errors='coerce')
df_nat['sexe'] = pd.to_numeric(df_nat.sexe, errors='coerce')
# Ajout d'une colonne pour simplifier la recherche et l'affichage des prénoms mixtes
df_nat['prénoms_s'] = [str(df_nat.prenom.loc[i])+' - ♂' if df_nat.sexe.loc[i]
                       == 1 else str(df_nat.prenom.loc[i])+' - ♀' for i in df_nat.index]

# Ajout du rang du prénom :
df_nat["rangs"] = 1
# Suppression des années NaN 
df_nat = df_nat[df_nat.periode.notna()]
df_nat.reset_index(drop=True,inplace=True)

for année in df_nat.periode.unique():
    for sexe in [1, 2]:
        masque_sexe = df_nat['sexe'] == sexe
        masque_année = df_nat['periode'] == année
        df_année = df_nat[masque_année & masque_sexe]
        rangs = df_année.valeur.rank(method='min', ascending=False)
        df_nat.loc[masque_année & masque_sexe, 'rangs'] = rangs

#df_nat[["annais","nombre","rangs"]]=df_nat[["annais","nombre","rangs"]].astype(np.float32)
df_léger = df_nat.drop(columns=['sexe', 'prenom'])

df_léger.to_feather('data/df_nat.feather')

dict_prénoms = [dict(label=prénom, value=prénom)
                for prénom in df_nat.prénoms_s.unique() if prénom[:-4] != '_PRENOMS_RARES']
pkl.dump(dict_prénoms,  open('data/dict_prenoms.pkl', "wb"))

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from utils import yearly_pattern, weather_data

# Eingabeparameter

numerosity = 2  # number of buildings/floors to be simulated
year = 2022  # year to be simulated
building = 'Haus 34'
label_Hl = 'Haus_34'
Ta, GTN, GTO, GTH, GTS, GTW = weather_data()

#  Fensterflächen
f = 2.834  # einzelne Fensterfläche

AFN = np.array([21*f, 30*f])
AFO = np.array([4*f, 4*f])
AFS = np.array([17*f, 17*f])
AFW = np.array([0,0])
AFH = np.array([0, 0])
gF = 0.53  # g-Wert Fenster

# U-Werte
U_Wert_Wand = 0.28
U_Wert_Fenster = 1.28
U_Wert_Dach = 0.23
U_Wert_Boden = 0.36


# Gebäude:
Traufhoehe = np.array([3,3])
Grundflaeche = np.array([638.34, 638.34])
Gebaeudeumfang = np.array([147.6, 147.6])
Mantelflaeche_ges = Gebaeudeumfang * Traufhoehe

# Transmissionswärmeverluste
FB = 0.5  # Temperaturkorrekturfaktor Bodenplatte
HT_Wand = U_Wert_Wand * (Mantelflaeche_ges - (AFN + AFO + AFS + AFW)) + U_Wert_Fenster * (AFN + AFO + AFS + AFW)
HT_Dach = U_Wert_Dach * (Grundflaeche - AFH) + U_Wert_Fenster * AFH
HT_Boden = U_Wert_Boden * FB * Grundflaeche
HT_ges = HT_Wand + HT_Dach + HT_Boden

#  Lüftungswärmeverluste
Ve = Grundflaeche * Traufhoehe  # beheiztes Volumen in m^3
V_L = Ve * 0.9  # Luftvolumen in m^3

# Luftwechselraten (Tag/Nacht)
n_LWT = np.full(numerosity, 0.5)
n_LWN = np.full(numerosity, 0.5)

TiT_wd = np.full(numerosity, 20)  # Soll-Innenraumtemperatur Tagsüber - Wochentage
TiT_we = np.full(numerosity, 15)  # Soll-Innenraumtemperatur Tagsüber - Wochenende
TiN = np.full(numerosity, 15)  # Soll-Innenraumtemperatur bei Nachtabsenkung
THG = np.full(numerosity, 15) # Heizgrenztemperaturen
THV = 45  # Vorlauftemperatur Heizkreis  # Spreizung Vorlauf/Rücklauf THV / THR = 45 / 30
dTN = 15  # Rücklauftemperatur Heizkreis
THR = THV - dTN

Ti_soll = np.zeros((8760, numerosity))
for i in range(0, numerosity):
    for j in range(len(yearly_pattern(year))):
        if yearly_pattern(year)[j] == 0.0:  # wochentage
            Ti_soll[:, i][j] = TiT_wd[i]
        elif yearly_pattern(year)[j] == 2.0:  # wochenende
            Ti_soll[:, i][j] = TiT_we[i]
        else:
            Ti_soll[:, i][j] = TiN[i]  # Nächte (von 22 bis 6 Uhr)

# %% Berechnung der Lasten

Qs = np.zeros((8760, numerosity))  # Solare Wärmegewinne durch tranparente Bauteile (Fenster) [kW]
n_LW = np.zeros((8760, numerosity))  # Lüftungswechselrate [kW]
HV = np.zeros((8760, numerosity))
QV = np.zeros((8760, numerosity))  # Wärmeverlust [kW]
QT = np.zeros((8760, numerosity))  # Transmissionswärmeverluste [kW]
Qh = np.zeros((8760, numerosity))  # Heizlast
COP = np.zeros((8760, numerosity))  # COP der Luft-Wasser-Wärmepumpe

# Stromlast wird zu je 50% als innere Wärmequelle in den Hallen 03 und 04 berücksichtigt
Qi = np.zeros((8760, numerosity)) # innere Wärmegewinne durch elektrische Verbraucher

#Stromlast = pd.read_csv('Stromlastprofil.csv')

#Qi[:, 0] = Stromlast['EG'].to_numpy()
#Qi[:, 1] = Stromlast['OG'].to_numpy()
#Qi[:, 2] = Stromlast['DG'].to_numpy()

for i in range(0, numerosity):
    Qs[:, i] = 0.567 * gF * (
                AFW[i] * GTW + AFO[i] * GTO + AFS[i] * GTS + AFN[i] * GTN + AFH[i] * GTH)
    delta_nLWT_nLWN = n_LWT - n_LWN
    n_LW[:, i] = delta_nLWT_nLWN[i] + n_LWN[i]
    HV[:, i] = np.multiply(n_LW[:, i], 0.34 * V_L[i])
    QV[:, i] = np.multiply(HV[:, i], (Ti_soll[:, i] - Ta) / 1000)
    QT[:, i] = np.multiply(HT_ges[i], (Ti_soll[:, i] - Ta) / 1000)

    for j in range(0, 8759):
        if Ta[j] < THG[i]:
            Qh[:, i][j] = np.maximum(0, QT[:, i][j] + QV[:, i][j] - Qs[:, i][j] - Qi[:, i][j])
        else:
            Qh[:, i][j] = 0

    nuH = 0.36  # Güte der Wärmepumpe
    COP[:, i] = np.minimum(10, nuH * (THV + 273.15) / (THV - Ta))

Summe_heizlast = sum((Qh) / 1000, 0)
print('Summe Heizlast = ' + str((sum(Qh) / 1000, 0)) + ' MWh')
print(f'Summe Heizlast {building} = ' + str(Summe_heizlast.sum()) + ' MWh')
print('Maximale Heizlast EG = ' + str((np.amax(Qh[:, 0]))) + ' kW')
print('Maximale Heizlast OG = ' + str((np.amax(Qh[:, 1]))) + ' kW')
#print('Maximale Heizlast DG = ' + str((np.amax(Qh[:, 2]))) + ' kW')
print('Maximale Heizlast Summe = ' + str((np.amax(Qh[:, 0]) + np.amax(Qh[:, 1]) )) + ' kW')


# %% Abbildungen
Heizlast = pd.DataFrame({'Stunden_array': np.arange(8760),
                         'EG': Qh[:, 0],
                         'OG': Qh[:, 1]
                         #'DG': Qh[:, 2]
                         }).set_index('Stunden_array')


plt.rcParams["figure.figsize"] = (10,6)
plt.stackplot(Heizlast.index, Heizlast.values.T, colors=['gold', 'limegreen', 'coral'], labels=['Erdgeschoss',
                                                                                'Obergeschoss', 'Dachgeschoss'])
plt.ylim(0, None)
plt.xlim(0, 8761)
plt.xlabel(2022, fontdict={'fontsize': 20})
plt.title(f'Heizlast {building}', fontdict={'fontsize': 30})
plt.ylabel('Leistung in kW', fontdict={'fontsize': 20})
plt.xticks([0, 744, 1416, 2160, 2880, 3624, 4344, 5088, 5832, 6552, 7296, 8016],
           ['Jan', 'Feb', 'März', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez'], fontdict={'fontsize': 12})
plt.legend()
plt.savefig(f'output/Heizlast_{label_Hl}')
plt.show()

#Jahresdauerline plotten
Heizlast['Heizlast'] = Heizlast[list(Heizlast.columns)].sum(axis=1)
Heizlast_array = Heizlast['Heizlast'].values
Stunden_array = np.arange(8760, dtype=int)
Last_data = {'Stunden': Stunden_array, 'Heizlast': Heizlast_array}
Last_df = pd.DataFrame(Last_data)

sns.set(rc={"figure.figsize":(10, 6)})
p = sns.lineplot(x = "Stunden", y = "Heizlast", data = Last_df)
plt.ylim(0, None)
plt.xlim(0, 8761)
p.set_title(f"Heizlast {building}", fontsize = 30)
p.set_xlabel("Stunden", fontsize = 20)
p.set_ylabel("Leistung (KW)", fontsize = 20)
plt.savefig(f'output/Heizlast_2_{label_Hl}')
plt.show()

Last_df['interval'] = 1
Last_df_sorted = Last_df.sort_values(by=['Heizlast'], ascending=False)
Last_df_sorted['Dauer'] = Last_df_sorted['interval'].cumsum()
Last_df_sorted['Percentage'] = Last_df_sorted['Dauer']*100/8760

p = sns.lineplot(x = "Dauer", y = "Heizlast", data = Last_df_sorted)
plt.ylim(0, None)
plt.xlim(0, 8761)
p.set_title(f"Jahresdauerlinie Heizlast {building}", fontsize = 30)
p.set_xlabel("Stunden", fontsize = 20)
p.set_ylabel("Leistung (KW)", fontsize = 20)
plt.savefig(f'output/JDL_HL_{building}')
plt.show()

# Export von Daten
csv_data_Heizlast = pd.DataFrame({'EG': Qh[:, 0],
                                    'OG': Qh[:, 1],
                                    #'DG': Qh[:, 2],
                                    'Heizlast_gesamt': Qh[:, 1] + Qh[:, 0]
                                  })
csv_data_Heizlast.to_csv(f'output/Heizlast_{building}.csv', index=False, sep=';')



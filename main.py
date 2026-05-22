import numpy as np
import pandas as pd
import random

np.random.seed(7)
random.seed(7)

data = [
    ["Telkomsel", "Super Seru 25 GB", 60000, 25, 28, 9, 7],
    ["Telkomsel", "Super Seru 40 GB", 80000, 40, 28, 9, 7],
    ["Tri", "Happy 30 GB", 70000, 30, 30, 7, 6],
    ["Tri", "AlwaysOn 40 GB", 85000, 40, 30, 7, 7],
    ["by.U", "Yang Bikin Nagih", 50499, 12, 30, 8, 5],
    ["by.U", "Yang Dicap Dua Jempol", 121199, 50, 30, 8, 6],
    ["Indosat IM3", "Freedom Internet 20 GB", 65000, 20, 30, 8, 6],
    ["Indosat IM3", "Freedom Internet 40 GB", 100000, 40, 30, 8, 7],
    ["XL", "Xtra Combo Flex M", 53000, 10, 28, 8, 6],
    ["XL", "Xtra Combo Flex M+", 64000, 14, 28, 8, 6],
    ["Smartfren", "Unlimited Nonstop 12 GB", 56500, 12, 30, 7, 8],
    ["Smartfren", "Unlimited Nonstop 30 GB", 79500, 30, 30, 7, 8],
]

columns = ["Provider", "Nama Paket", "Harga", "Kuota", "Masa Aktif", "Jaringan", "Bonus"]
df = pd.DataFrame(data, columns=columns)

df["Harga_N"] = 1 - ((df["Harga"] - df["Harga"].min()) / (df["Harga"].max() - df["Harga"].min()))

df["Kuota_N"] = (df["Kuota"] - df["Kuota"].min()) / (df["Kuota"].max() - df["Kuota"].min())

df["MasaAktif_N"] = (df["Masa Aktif"] / 30).clip(upper=1)

df["Jaringan_N"] = df["Jaringan"] / 10
df["Bonus_N"] = df["Bonus"] / 10

fitur = df[["Harga_N", "Kuota_N", "MasaAktif_N", "Jaringan_N", "Bonus_N"]].values

target_weights = np.array([0.18, 0.25, 0.12, 0.35, 0.10])

def normalize_weights(weights):
    weights = np.abs(weights)
    total = np.sum(weights)

    if total == 0:
        return np.ones(len(weights)) / len(weights)

    return weights / total

def fitness(weights):
    weights = normalize_weights(weights)

    error = np.mean((weights - target_weights) ** 2)

    return 1 / (1 + error)

jumlah_chimp = 30
jumlah_fitur = 5
iterasi = 100

populasi = np.random.rand(jumlah_chimp, jumlah_fitur)

for t in range(iterasi):
    nilai_fitness = np.array([fitness(chimp) for chimp in populasi])

    index_terbaik = nilai_fitness.argsort()[-4:][::-1]

    attacker = populasi[index_terbaik[0]]
    barrier = populasi[index_terbaik[1]]
    chaser = populasi[index_terbaik[2]]
    driver = populasi[index_terbaik[3]]

    for i in range(jumlah_chimp):
        r1 = random.random()
        r2 = random.random()
        r3 = random.random()
        r4 = random.random()

        posisi_baru = (
            r1 * attacker +
            r2 * barrier +
            r3 * chaser +
            r4 * driver
        ) / (r1 + r2 + r3 + r4)

        posisi_baru += np.random.normal(0, 0.02, jumlah_fitur)

        populasi[i] = np.clip(posisi_baru, 0, 1)

nilai_fitness = np.array([fitness(chimp) for chimp in populasi])
best_index = np.argmax(nilai_fitness)
best_weights = normalize_weights(populasi[best_index])

df["Skor Akhir"] = np.dot(fitur, best_weights)

hasil = df.sort_values(by="Skor Akhir", ascending=False).reset_index(drop=True)

hasil.insert(0, "Ranking", range(1, len(hasil) + 1))

def print_table(headers, data):
    data_str = [[str(item) for item in row] for row in data]
    headers_str = [str(h) for h in headers]
    col_widths = [len(h) for h in headers_str]
    for row in data_str:
        for i, item in enumerate(row):
            if len(item) > col_widths[i]:
                col_widths[i] = len(item)
    
    row_format = "| " + " | ".join([f"{{:<{w}}}" for w in col_widths]) + " |"
    separator = "+" + "+".join(["-" * (w + 2) for w in col_widths]) + "+"
    
    print(separator)
    print(row_format.format(*headers_str))
    print(separator)
    for row in data_str:
        print(row_format.format(*row))
    print(separator)

print("+" + "-" * 72 + "+")
print("|" + "SISTEM PEMILIHAN PAKET INTERNET TERBAIK MENGGUNAKAN ChOA".center(72) + "|")
print("+" + "-" * 72 + "+")

print("\n[ Bobot Terbaik Hasil Optimasi ChOA ]")
print(f"  - Harga       : {best_weights[0]:.3f} ({best_weights[0] * 100:.1f}%)")
print(f"  - Kuota       : {best_weights[1]:.3f} ({best_weights[1] * 100:.1f}%)")
print(f"  - Masa Aktif  : {best_weights[2]:.3f} ({best_weights[2] * 100:.1f}%)")
print(f"  - Jaringan    : {best_weights[3]:.3f} ({best_weights[3] * 100:.1f}%)")
print(f"  - Bonus       : {best_weights[4]:.3f} ({best_weights[4] * 100:.1f}%)")

print("\n[ Tabel Nilai Normalisasi ]")
headers_norm = ["Provider", "Nama Paket", "Harga_N", "Kuota_N", "MasaAktif_N", "Jaringan_N", "Bonus_N"]
data_norm = df[headers_norm].copy()
for col in ["Harga_N", "Kuota_N", "MasaAktif_N", "Jaringan_N", "Bonus_N"]:
    data_norm[col] = data_norm[col].apply(lambda x: f"{x:.3f}")
print_table(headers_norm, data_norm.values.tolist())

print("\n[ Ranking Paket Internet Terbaik ]")
headers_rank = ["Ranking", "Provider", "Nama Paket", "Harga", "Kuota", "Masa Aktif", "Jaringan", "Bonus", "Skor Akhir"]
data_rank = hasil.head(10)[headers_rank].copy()
data_rank["Harga"] = data_rank["Harga"].apply(lambda x: f"Rp{x:,.0f}")
data_rank["Skor Akhir"] = data_rank["Skor Akhir"].apply(lambda x: f"{x:.3f}")
print_table(headers_rank, data_rank.values.tolist())

print("\n" + "=" * 74)
print(" KESIMPULAN")
print("=" * 74)
print(f" Paket terbaik adalah {hasil.loc[0, 'Provider']} - {hasil.loc[0, 'Nama Paket']}")
print(f" dengan skor akhir {hasil.loc[0, 'Skor Akhir']:.3f}.")
print("=" * 74 + "\n")
import pandas as pd
import numpy as np
import datetime
from tabulate import tabulate  # pip install tabulate

def parse_instance(filepath):
    """
    Lê o arquivo de instância e retorna:
    - header: dict com 'num_days' e 'capacity_per_day'
    - df: DataFrame com as colunas ['SurgNr','P1','P2','P3']
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    header = {}
    surgeries = []
    mode = None

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith('#'):
            if 'INSTANCE CHARACTERISTICS' in line:
                mode = 'header'
            elif 'SURGERIES' in line:
                mode = 'surgeries'
            continue

        if mode == 'header':
            val, desc = line.split('\t')
            if desc == 'number of OR-days':
                header['num_days'] = int(val)
            elif desc == 'Capacity OR-days in minutes':
                header['capacity_per_day'] = float(val)

        elif mode == 'surgeries' and not line.startswith('SurgNr'):
            p = line.split('\t')
            surgeries.append({
                'SurgNr': int(p[0]),
                'P1': float(p[1]),
                'P2': float(p[2]),
                'P3': float(p[3])
            })

    return header, pd.DataFrame(surgeries)

def ffd_schedule(header, df):
    """
    Aplica First‐Fit Decreasing (FFD) para atribuir cada cirurgia a um OR‐day.
    Retorna um DataFrame com ['SurgNr','duration','Block'].
    """
    df = df.copy()
    df['duration'] = np.exp(df['P1'] + (df['P2']**2)/2) + df['P3']
    df_sorted = df.sort_values('duration', ascending=False).reset_index(drop=True)

    capacity = [header['capacity_per_day']] * header['num_days']
    assignments = []

    for _, row in df_sorted.iterrows():
        dur = row['duration']
        placed = False
        for day in range(header['num_days']):
            if capacity[day] >= dur:
                capacity[day] -= dur
                assignments.append({
                    'SurgNr': row['SurgNr'],
                    'duration': dur,
                    'Block': day + 1
                })
                placed = True
                break
        if not placed:
            assignments.append({
                'SurgNr': row['SurgNr'],
                'duration': dur,
                'Block': None
            })

    return pd.DataFrame(assignments)

# -----------------------
# Parâmetros de entrada
# -----------------------
filepath    = '1_ordays_5_load_0,8_1.txt'        # caminho para seu arquivo de instância
start_date  = datetime.date(2025, 5, 15)        # data do primeiro dia
start_hour  = 5                               # hora de início do turno (por ex. 8 = 08:00)

# -----------------------
# Execução
# -----------------------
header, surgeries_df = parse_instance(filepath)
assign_df = ffd_schedule(header, surgeries_df)

# ordenar por dia (internamente em 'Block') e por duração decrescente
assign_df = assign_df.sort_values(['Block','duration'], ascending=[True,False]).reset_index(drop=True)

# calcula offset cumulativo dentro de cada dia
assign_df['start_offset'] = assign_df.groupby('Block')['duration'].cumsum() - assign_df['duration']

# converte offset em data e hora legíveis
def to_time(offset_min):
    base = datetime.datetime.combine(datetime.date.today(), datetime.time(start_hour, 0))
    t = base + datetime.timedelta(minutes=offset_min)
    return t.time().strftime('%H:%M')

assign_df['Date']  = assign_df['Block'].apply(
    lambda d: start_date + datetime.timedelta(days=d-1) if pd.notnull(d) else None
)
assign_df['Start'] = assign_df['start_offset'].apply(lambda m: to_time(m) if pd.notnull(m) else None)
assign_df['End']   = (assign_df['start_offset'] + assign_df['duration']).apply(
    lambda m: to_time(m) if pd.notnull(m) else None
)

# montar tabela final sem a coluna 'Block'
schedule_df = assign_df[['SurgNr','Date','Start','End','duration']].rename(
    columns={'duration':'Duration (min)'}
)

# exibir no console
print("\nEscalonamento Detalhado (FFD):")
print(tabulate(schedule_df, headers='keys', tablefmt='pretty', showindex=False))

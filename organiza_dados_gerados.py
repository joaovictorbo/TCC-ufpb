import pandas as pd
import random
from datetime import datetime, date, time, timedelta

def schedule_surgeries(
    input_csv: str,
    output_csv: str,
    num_rooms: int = 5,
    work_start: time = time(7, 0),
    work_end: time = time(22, 0)
):
    """
    Lê um CSV com colunas ['surgery_id', 'duration_minutes', 'cleaning_minutes'],
    e gera um cronograma de cirurgias a partir de amanhã, alocando-as em `num_rooms`
    salas entre work_start e work_end. Usa um algoritmo guloso (LPT + list scheduling).
    Salva em CSV com colunas:
      ['surgery_id', 'room_id', 'start', 'end', 'cleaning_end']
    """
    # 1) Carrega os dados
    df = pd.read_csv(input_csv)
    # Total de processamento (cirurgia + limpeza)
    df['total_minutes'] = df['duration_minutes'] + df['cleaning_minutes']
    # 2) Heurística LPT: maior processamento primeiro
    df = df.sort_values('total_minutes', ascending=False).reset_index(drop=True)
    
    # 3) Inicializa disponibilidade de cada sala para amanhã às work_start
    today = date.today()
    start_date = today + timedelta(days=1)
    avail = {
        room: datetime.combine(start_date, work_start)
        for room in range(1, num_rooms + 1)
    }
    
    schedule = []
    for _, row in df.iterrows():
        # Escolhe a sala que fica livre primeiro
        room = min(avail, key=lambda r: avail[r])
        t_avail = avail[room]
        
        # Ajusta t_avail para cair num horário válido de cirurgia
        while True:
            # Se já passou do horário de funcionamento, vai pro próximo dia
            if t_avail.time() > work_end:
                t_avail = datetime.combine(t_avail.date() + timedelta(days=1), work_start)
                continue
            # Se a cirurgia não cabe até work_end, pula pro próximo dia
            if (t_avail + timedelta(minutes=int(row['duration_minutes']))).time() > work_end:
                t_avail = datetime.combine(t_avail.date() + timedelta(days=1), work_start)
                continue
            break
        
        # Agenda início e fim da cirurgia
        start_dt = t_avail
        end_dt = start_dt + timedelta(minutes=int(row['duration_minutes']))
        # Agenda fim da limpeza (impede próxima cirurgia nessa sala antes disso)
        cleaning_end_dt = end_dt + timedelta(minutes=int(row['cleaning_minutes']))
        
        # Atualiza disponibilidade da sala
        avail[room] = cleaning_end_dt
        
        # Grava no cronograma
        schedule.append({
            'surgery_id':      int(row['surgery_id']),
            'room_id':         room,
            'start':           start_dt.strftime('%Y-%m-%d %H:%M'),
            'end':             end_dt.strftime('%Y-%m-%d %H:%M'),
            'cleaning_end':    cleaning_end_dt.strftime('%Y-%m-%d %H:%M'),
        })
    
    # 4) Salva o cronograma em CSV
    sched_df = pd.DataFrame(schedule)
    sched_df.to_csv(output_csv, index=False)
    print(f'Cronograma salvo em: {output_csv}')


if __name__ == '__main__':
    # Exemplo de uso:
    schedule_surgeries(
        input_csv='surgeries_with_cleaning.csv',
        output_csv='scheduled_surgeries.csv',
        num_rooms=5
    )

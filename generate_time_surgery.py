import pandas as pd
import random

def generate_surgery_schedule_csv(
    output_path: str = 'surgeries.csv',
    num_surgeries: int = 20,
    min_duration: int = 30,
    max_duration: int = 240,
    min_cleaning: int = 10,
    max_cleaning: int = 60
):
    """
    Gera um CSV contendo tempos de cirurgia e tempos de limpeza de salas.

    Parâmetros:
    - output_path: caminho do arquivo CSV a ser gerado
    - num_surgeries: número de registros (cirurgias) a gerar
    - min_duration, max_duration: intervalo (em minutos) para duração das cirurgias
    - min_cleaning, max_cleaning: intervalo (em minutos) para limpeza das salas
    """
    # Gera listas de tempos aleatórios
    durations = [random.randint(min_duration, max_duration) for _ in range(num_surgeries)]
    cleanings = [random.randint(min_cleaning, max_cleaning) for _ in range(num_surgeries)]
    
    # Monta o DataFrame
    df = pd.DataFrame({
        'surgery_id': range(1, num_surgeries + 1),
        'duration_minutes': durations,
        'cleaning_minutes': cleanings
    })
    
    # Salva em CSV
    df.to_csv(output_path, index=False)
    print(f'CSV gerado: {output_path}')

if __name__ == '__main__':
    # Exemplo de uso
    generate_surgery_schedule_csv(
        output_path='surgeries_with_cleaning.csv',
        num_surgeries=20,
        min_duration=30,
        max_duration=240,
        min_cleaning=10,
        max_cleaning=60
    )

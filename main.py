from ortools.linear_solver import pywraplp

# Dados de exemplo com médicos e enfermeiros necessários por cirurgia
cirurgias = [
    {'id': 1, 'duracao': 2, 'equipamentos': ['Bisturi'], 'medicos': 1, 'enfermeiros': 1},
    {'id': 2, 'duracao': 1.5, 'equipamentos': ['Espatula'], 'medicos': 1, 'enfermeiros': 1},
    {'id': 3, 'duracao': 3, 'equipamentos': ['Bisturi'], 'medicos': 2, 'enfermeiros': 1},
]

# Salas com médicos e enfermeiros disponíveis
salas = [
    {'id': 1, 'equipamentos': ['Bisturi'], 'capacidade': 1, 'medicos_max': 2, 'enfermeiros_max': 2},
    {'id': 2, 'equipamentos': ['Espatula'], 'capacidade': 1, 'medicos_max': 1, 'enfermeiros_max': 1},
    {'id': 3, 'equipamentos': ['Bisturi'], 'capacidade': 2, 'medicos_max': 3, 'enfermeiros_max': 2},
]

# Horas de operação
horas_dia = 12

# Criando o solver
solver = pywraplp.Solver.CreateSolver('SCIP')

# Variáveis de decisão: alocação das cirurgias (1 se cirurgia i for na sala j, 0 caso contrário)
x = {}
for i in range(len(cirurgias)):
    for j in range(len(salas)):
        x[i, j] = solver.BoolVar(f'x_{i}_{j}')

# Variáveis para alocar médicos e enfermeiros às salas
medicos_alocados = {}
enfermeiros_alocados = {}

for i in range(len(cirurgias)):
    for j in range(len(salas)):
        medicos_alocados[i, j] = solver.IntVar(0, 100, f'medicos_{i}_{j}')
        enfermeiros_alocados[i, j] = solver.IntVar(0, 100, f'enfermeiros_{i}_{j}')

# Função objetivo: Minimizar o tempo total de uso das salas
solver.Minimize(solver.Sum(cirurgias[i]['duracao'] * x[i, j] for i in range(len(cirurgias)) for j in range(len(salas))))

# Restrições

# 1. Cada cirurgia deve ser alocada a exatamente uma sala
for i in range(len(cirurgias)):
    solver.Add(solver.Sum(x[i, j] for j in range(len(salas))) == 1)

# 2. Cada sala pode ter no máximo uma cirurgia por vez
for j in range(len(salas)):
    solver.Add(solver.Sum(x[i, j] for i in range(len(cirurgias))) <= salas[j]['capacidade'])

# 3. A sala deve ter os equipamentos necessários para a cirurgia
for i in range(len(cirurgias)):
    for j in range(len(salas)):
        if not all(equip in salas[j]['equipamentos'] for equip in cirurgias[i]['equipamentos']):
            solver.Add(x[i, j] == 0)

# 4. A sala não pode ultrapassar a capacidade de médicos e enfermeiros
for j in range(len(salas)):
    solver.Add(solver.Sum(medicos_alocados[i, j] for i in range(len(cirurgias))) <= salas[j]['medicos_max'])
    solver.Add(solver.Sum(enfermeiros_alocados[i, j] for i in range(len(cirurgias))) <= salas[j]['enfermeiros_max'])

    for i in range(len(cirurgias)):
        solver.Add(medicos_alocados[i, j] >= cirurgias[i]['medicos'] * x[i, j])
        solver.Add(enfermeiros_alocados[i, j] >= cirurgias[i]['enfermeiros'] * x[i, j])

# 5. Tempo total de uso das salas não pode ultrapassar as horas do dia
for j in range(len(salas)):
    solver.Add(solver.Sum(cirurgias[i]['duracao'] * x[i, j] for i in range(len(cirurgias))) <= horas_dia)

# Resolver o modelo
status = solver.Solve()

# Exibir a solução
if status == pywraplp.Solver.OPTIMAL:
    print("Solução ótima encontrada:")
    for i in range(len(cirurgias)):
        for j in range(len(salas)):
            if x[i, j].solution_value() >= 0.99:  # Se a variável de decisão for 1
                print(f"Cirurgia {cirurgias[i]['id']} alocada na Sala {salas[j]['id']} (Duração: {cirurgias[i]['duracao']} horas)")
else:
    print("Nenhuma solução ótima encontrada.")

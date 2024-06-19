import simpy  # Importa la biblioteca simpy para la simulación de eventos discretos
import random  # Importa la biblioteca random para generar valores aleatorios
import numpy as np  # Importa la biblioteca numpy para cálculos numéricos
import matplotlib.pyplot as plt  # Importa matplotlib para la creación de gráficos

# Parámetros iniciales
lambda_ = 2/1  # Tasa de llegada de clientes (clientes por minuto)
mu1 = 3/1    # Tasa de servicio de degustación (clientes por minuto)
mu2 = 4/1    # Tasa de servicio de encuestas (clientes por minuto)
c1 = 1       # Número de estaciones de degustación
c2 = 1       # Número de computadoras/tablets

# Variables para almacenar resultados
num_clients_degustation = []      # Número de clientes en la cola de degustación en cada instante
num_clients_survey = []           # Número de clientes en la cola de encuestas en cada instante
waiting_times_degustation = []    # Tiempo de espera de cada cliente en la cola de degustación
waiting_times_survey = []         # Tiempo de espera de cada cliente en la cola de encuestas
total_times_system = []           # Tiempo total de cada cliente en el sistema

# Clase que representa el sistema de degustación y encuestas
class Galletitas:
    def __init__(self, env, c1, c2, mu1, mu2):
        self.env = env
        self.degustation_station = simpy.Resource(env, capacity=c1)  # Estaciones de degustación
        self.survey_station = simpy.Resource(env, capacity=c2)       # Computadoras/tablets para encuestas
        self.mu1 = mu1  # Tasa de servicio de degustación
        self.mu2 = mu2  # Tasa de servicio de encuestas

    # Proceso de degustación
    def degustation(self, client):
        yield self.env.timeout(random.expovariate(self.mu1))  # Tiempo de servicio de degustación

    # Proceso de encuestas
    def survey(self, client):
        yield self.env.timeout(random.expovariate(self.mu2))  # Tiempo de servicio de encuesta

# Proceso de llegada y servicio de clientes
def client(env, name, galletitas):
    arrival_time = env.now  # Tiempo de llegada del cliente

    # Proceso de degustación
    with galletitas.degustation_station.request() as request:
        yield request
        start_service_degustation = env.now
        num_clients_degustation.append(len(galletitas.degustation_station.queue))
        yield env.process(galletitas.degustation(name))
        waiting_times_degustation.append(env.now - start_service_degustation)

    # Proceso de encuestas
    with galletitas.survey_station.request() as request:
        yield request
        start_service_survey = env.now
        num_clients_survey.append(len(galletitas.survey_station.queue))
        yield env.process(galletitas.survey(name))
        waiting_times_survey.append(env.now - start_service_survey)

    # Tiempo total en el sistema
    total_times_system.append(env.now - arrival_time)   # Registrar tiempo total en el sistema

# Función para generar llegadas de clientes
def setup(env, lambda_, galletitas, num_clients):
    for i in range(num_clients):    # Iterar sobre el número de clientes
        yield env.timeout(random.expovariate(lambda_))  # Tiempo entre llegadas de clientes, usa la distribución Exponencial
        env.process(client(env, f'Cliente {i+1}', galletitas))  # Procesar un nuevo cliente

# Inicialización del entorno de simulación
num_clients = 50  # Número de clientes a simular
env = simpy.Environment()  # Crear un entorno de simulación
galletitas = Galletitas(env, c1, c2, mu1, mu2)  # Crear una instancia del sistema de degustación y encuestas

# Ejecutar la simulación
env.process(setup(env, lambda_, galletitas, num_clients))   # Generar llegadas de clientes
env.run(until=30)   # Ejecutar la simulación durante 30 minutos

# Cálculos de desempeño para la degustación
avg_num_clients_degustation = np.mean(num_clients_degustation)  # Número promedio de clientes en la cola de degustación
avg_waiting_time_degustation = np.mean(waiting_times_degustation)  # Tiempo promedio de espera en la cola de degustación
utilization_degustation = lambda_ / mu1  # Factor de utilización del servicio de degustación
avg_clients_in_system_degustation = lambda_ / (mu1 - lambda_)  # Número promedio de clientes en el sistema de degustación
avg_time_in_system_degustation = 1 / (mu1 - lambda_)  # Tiempo promedio en el sistema por cliente en degustación

# Cálculos de desempeño para la encuesta
avg_num_clients_survey = np.mean(num_clients_survey)  # Número promedio de clientes en la cola de encuestas
avg_waiting_time_survey = np.mean(waiting_times_survey)  # Tiempo promedio de espera en la cola de encuestas
utilization_survey = lambda_ / mu2  # Factor de utilización del servicio de encuestas
avg_clients_in_system_survey = lambda_ / (mu2 - lambda_)  # Número promedio de clientes en el sistema de encuestas
avg_time_in_system_survey = 1 / (mu2 - lambda_)  # Tiempo promedio en el sistema por cliente en encuestas

# Estadísticas totales del sistema
avg_num_clients_system = avg_clients_in_system_degustation + avg_clients_in_system_survey  # Número promedio de clientes en el sistema total
avg_time_in_system = avg_time_in_system_degustation + avg_time_in_system_survey  # Tiempo promedio en el sistema total

# Función para formatear números según las especificaciones
def format_number(number):
    return f"{number:.2f}"

# Imprimir resultados con formato
print("\nDegustación:")
print("Número PROMEDIO de clientes en el sistema:", format_number(avg_clients_in_system_degustation))
print("Tiempo PROMEDIO en el sistema por cliente:", format_number(avg_time_in_system_degustation), "Minutos")
print("Número PROMEDIO de clientes esperando en la cola:", format_number((lambda_**2) / (mu1 * (mu1 - lambda_))))
print("Factor de utilización del área de degustación:", format_number(utilization_degustation))

print("\nEncuestas:")
print("Número PROMEDIO de clientes en el sistema:", format_number(avg_clients_in_system_survey))
print("Tiempo PROMEDIO en el sistema por cliente:", format_number(avg_time_in_system_survey), "Minutos")
print("Número PROMEDIO de clientes esperando en la cola:", format_number((lambda_**2) / (mu2 * (mu2 - lambda_))))
print("Factor de utilización del área de encuesta:", format_number(utilization_survey))

print("\nTotales del sistema:")
print("Número PROMEDIO de clientes en el sistema:", format_number(avg_num_clients_system))
print("Tiempo PROMEDIO en el sistema por cliente:", format_number(avg_time_in_system), "Minutos")
print("Factor de utilización del sistema:", format_number((utilization_survey + utilization_degustation) / 2) )

# Gráficos
plt.figure(figsize=(10, 8))

# Gráfico de cantidad de clientes en la cola de degustación
plt.subplot(3, 1, 1)
plt.plot(np.arange(len(num_clients_degustation)), num_clients_degustation, label='Cola de degustación')
plt.xlabel('Tiempo (clientes atendidos)')
plt.ylabel('Número de clientes')
plt.title('Cantidad de clientes en la cola de degustación')
plt.legend()

# Gráfico de cantidad de clientes en la cola de encuestas
plt.subplot(3, 1, 2)
plt.plot(np.arange(len(num_clients_survey)), num_clients_survey, label='Cola de encuestas')
plt.xlabel('Tiempo (clientes atendidos)')
plt.ylabel('Número de clientes')
plt.title('Cantidad de clientes en la cola de encuestas')
plt.legend()

# Gráfico de tiempo total en el sistema por cliente
plt.subplot(3, 1, 3)
plt.plot(np.arange(len(total_times_system)), total_times_system, label='Tiempo en el sistema por cliente')
plt.xlabel('Cliente')
plt.ylabel('Tiempo en el sistema (minutos)')
plt.title('Tiempo en el sistema por cliente')
plt.legend()

plt.tight_layout()
plt.show()

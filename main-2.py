import simpy  # Importa la biblioteca simpy para la simulación de eventos discretos
import random  # Importa la biblioteca random para generar valores aleatorios
import numpy as np  # Importa la biblioteca numpy para cálculos numéricos
import matplotlib.pyplot as plt  # Importa matplotlib para la creación de gráficos

# se inicialisan variables
lambda_ = 1  # Tasa de llegada de clientes (clientes por minuto)
mu1 = 5/3    # Tasa de servicio de degustación (clientes por minuto)
mu2 = 6/4    # Tasa de servicio de encuestas (clientes por minuto)
c1 = 1       # Número de estaciones de degustación
c2 = 1       # Número de computadoras/tablets

# Variables de estado
num_clients_degustation = []      # Número de clientes en la cola de degustación en cada instante
num_clients_survey = []           # Número de clientes en la cola de encuestas en cada instante
waiting_times_degustation = []    # Tiempo de espera de cada cliente en la cola de degustación
waiting_times_survey = []         # Tiempo de espera de cada cliente en la cola de encuestas
total_times_system = []           # Tiempo total de cada cliente en el sistema
time_points_degustation = []      # Puntos de tiempo para el gráfico de degustación
time_points_survey = []           # Puntos de tiempo para el gráfico de encuestas

# Clase que representa el sistema de análisis sensorial
# Se guardan y obtiene los tiempos de servicio con la distribucion exponencial
class Galletitas:
    def __init__(self, env, c1, c2, mu1, mu2):
        self.env = env
        self.degustation_station = simpy.Resource(env, capacity=c1)  # Estaciones de degustación
        self.survey_station = simpy.Resource(env, capacity=c2)       # Computadoras/tablets para encuestas
        self.mu1 = mu1  # Tasa de servicio de degustación
        self.mu2 = mu2  # Tasa de servicio de encuestas

    # Proceso de degustación, aca se aplica la distribucion exponencial para tener el tiempo de servicio
    def degustation(self, client):
        yield self.env.timeout(random.expovariate(self.mu1))  # Tiempo de servicio de degustación, usa la distribución Exponencial

    # Proceso de llenado de encuesta, aca se aplica la distribucion exponencial para tener el tiempo de servicio
    def survey(self, client):
        yield self.env.timeout(random.expovariate(self.mu2))  # Tiempo de servicio de encuesta, usa la distribución Exponencial

# Función que simula la llegada y procesamiento de un cliente
def client(env, name, galletitas):
    arrival_time = env.now  # Tiempo de llegada del cliente

    # Cola de degustación simula desde la llegada del cliente
    with galletitas.degustation_station.request() as request:
        yield request  # Esperar hasta que una estación de degustación esté disponible
        start_service_degustation = env.now  # Tiempo en que el servicio de degustación comienza
        num_clients_degustation.append(len(galletitas.degustation_station.queue))  # Registrar número de clientes en la cola de degustación
        time_points_degustation.append(env.now)  # Registrar el tiempo actual
        yield env.process(galletitas.degustation(name))  # Tiempo de servicio de degustación
        waiting_times_degustation.append(env.now - start_service_degustation)  # Registrar tiempo de espera en la cola de degustación

    # Cola de encuestas
    with galletitas.survey_station.request() as request:
        yield request  # Esperar hasta que una computadora/tablet esté disponible
        start_service_survey = env.now  # Tiempo en que el servicio de encuesta comienza
        num_clients_survey.append(len(galletitas.survey_station.queue))  # Registrar número de clientes en la cola de encuestas
        time_points_survey.append(env.now)  # Registrar el tiempo actual
        yield env.process(galletitas.survey(name))  # Tiempo de servicio de encuesta
        waiting_times_survey.append(env.now - start_service_survey)  # Registrar tiempo de espera en la cola de encuestas

    # Tiempo total en el sistema
    total_times_system.append(env.now - arrival_time)  # Registrar tiempo total en el sistema

# Función que genera llegadas de clientes
def setup(env, lambda_, galletitas, num_clients):
    for i in range(num_clients):  # Iterar sobre el número de clientes
        yield env.timeout(random.expovariate(lambda_))  # Tiempo entre llegadas de clientes, usa la distribución Exponencial
        env.process(client(env, f'Cliente {i+1}', galletitas))  # Procesar un nuevo cliente

# Inicialización del entorno de simulación
num_clients = 100  # Número de clientes a simular
env = simpy.Environment()  # Crear un entorno de simulación
galletitas = Galletitas(env, c1, c2, mu1, mu2)  # Crear una instancia del sistema de análisis sensorial

# Ejecutar la simulación
env.process(setup(env, lambda_, galletitas, num_clients))  # Generar llegadas de clientes
env.run(until=150)  # Tiempo de simulación (en minutos)

# Calcular medidas de desempeño
avg_waiting_time_degustation = np.mean(waiting_times_degustation)  # Tiempo promedio de espera en la cola de degustación
avg_waiting_time_survey = np.mean(waiting_times_survey)  # Tiempo promedio de espera en la cola de la encuesta
avg_total_time_system = np.mean(total_times_system)  # Tiempo promedio en el sistema
avg_num_clients_degustation = np.mean(num_clients_degustation)  # Número promedio de clientes en la cola de degustación
avg_num_clients_survey = np.mean(num_clients_survey)  # Número promedio de clientes en la cola de encuestas

# Imprimir resultados
print("\nTiempo PROMEDIO de espera en la cola de degustación:", avg_waiting_time_degustation)
print("Tiempo PROMEDIO de espera en la cola de la encuesta:", avg_waiting_time_survey)
print("Tiempo PROMEDIO en el sistema:", avg_total_time_system)
print("Número PROMEDIO de clientes en la cola de degustación:", avg_num_clients_degustation)
print("Número PROMEDIO de clientes en la cola de encuestas:", avg_num_clients_survey)

# Graficar resultados
plt.figure(figsize=(14, 6))  # Crear una figura de tamaño 14x6 pulgadas

# Gráfico de cantidad de personas en la cola de degustación
plt.subplot(2, 1, 1)  # Crear un subplot 2x1, posición 1
plt.plot(time_points_degustation, num_clients_degustation, label='Cola de degustación')  # Graficar datos de la cola de degustación
plt.xlabel('Tiempo (minutos)')  # Etiqueta del eje X
plt.ylabel('Número de clientes')  # Etiqueta del eje Y
plt.title('Cantidad de personas en la cola de degustación')  # Título del gráfico
plt.legend()  # Mostrar leyenda

# Gráfico de cantidad de personas en la cola de encuestas
plt.subplot(2, 1, 2)  # Crear un subplot 2x1, posición 2
plt.plot(time_points_survey, num_clients_survey, label='Cola de encuestas')  # Graficar datos de la cola de encuestas
plt.xlabel('Tiempo (minutos)')  # Etiqueta del eje X
plt.ylabel('Número de clientes')  # Etiqueta del eje Y
plt.title('Cantidad de personas en la cola para acceder a la encuesta')  # Título del gráfico
plt.legend()  # Mostrar leyenda

plt.tight_layout()  # Ajustar el diseño para que no se superpongan los elementos
plt.show()  # Mostrar los gráficos

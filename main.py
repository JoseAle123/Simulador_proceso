from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGraphicsView, QGraphicsScene, QLabel, \
    QPushButton
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QColor, QBrush, QPen
import random
import psutil


class Process:
    def __init__(self, name, duration, color, arrival_time):
        self.name = name
        self.duration = duration
        self.remaining_time = duration
        self.time_slices = []  # Intervalos de tiempo asignados
        self.color = color  # Color aleatorio del proceso
        self.arrival_time = arrival_time  # Tiempo de llegada del proceso


class CPUPlanner:
    def __init__(self, quantum=None):
        self.queue = []
        self.pending_processes = []  # Procesos que aún no han llegado
        self.quantum = quantum
        self.time_slice = 0
        self.current_time = 0

    def add_process(self, process):
        self.pending_processes.append(process)

    def update_ready_queue(self):
        # Mover procesos de la cola previa a la cola principal según el tiempo de llegada
        for process in list(self.pending_processes):
            if process.arrival_time <= self.current_time:
                self.queue.append(process)
                self.pending_processes.remove(process)

    def execute_fcfs(self):
        self.update_ready_queue()

        if self.queue:
            process = self.queue[0]
            process.time_slices.append(self.current_time)
            process.remaining_time -= 1
            self.current_time += 1

            if process.remaining_time == 0:
                self.queue.pop(0)
        else:
            # Avanzar el tiempo si no hay procesos listos
            self.current_time += 1

    def execute_rr(self):
        self.update_ready_queue()

        if self.queue:
            process = self.queue[0]
            process.time_slices.append(self.current_time)
            process.remaining_time -= 1
            self.time_slice += 1
            self.current_time += 1

            if process.remaining_time == 0 or self.time_slice == self.quantum:
                if process.remaining_time == 0:
                    self.queue.pop(0)
                else:
                    self.queue.pop(0)
                    self.queue.append(process)
                self.time_slice = 0
        else:
            # Avanzar el tiempo si no hay procesos listos
            self.current_time += 1

    def execute_sjf(self):
        self.update_ready_queue()

        if self.queue:
            # Ordenar la cola de procesos por el tiempo de duración restante (menor a mayor)
            self.queue.sort(key=lambda p: p.remaining_time)

            # Obtener el proceso con el menor tiempo de duración restante
            process = self.queue[0]
            process.time_slices.append(self.current_time)
            process.remaining_time -= 1
            self.current_time += 1

            if process.remaining_time == 0:
                self.queue.pop(0)
        else:
            # Avanzar el tiempo si no hay procesos listos
            self.current_time += 1


class GanttVisualizer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Diagrama Gantt - FCFS y Round Robin y SJF")
        self.setGeometry(100, 100, 1200, 600)

        self.fcfs_planner = CPUPlanner()
        self.rr_planner = CPUPlanner(quantum=2)
        self.sjf_planner = CPUPlanner()

        self.scene_fcfs = QGraphicsScene()
        self.scene_rr = QGraphicsScene()
        self.scene_sjf = QGraphicsScene()
        self.scene_cpu_mastro = QGraphicsScene()  # Nueva escena para CPU Mastro

        self.view_fcfs = QGraphicsView(self.scene_fcfs)
        self.view_rr = QGraphicsView(self.scene_rr)
        self.view_sjf = QGraphicsView(self.scene_sjf)
        self.view_cpu_mastro = QGraphicsView(self.scene_cpu_mastro)  # Nueva vista para CPU Mastro

        self.label_fcfs = QLabel("FCFS")
        self.label_rr = QLabel("Round Robin")
        self.label_sjf = QLabel("Shortest job First")
        self.label_cpu_mastro = QLabel("CPU Mastro")  # Nueva etiqueta para CPU Mastro

        self.layout = QVBoxLayout()
        self.layout_fcfs = QVBoxLayout()
        self.layout_rr = QVBoxLayout()
        self.layout_sjf = QVBoxLayout()
        self.layout_cpu_mastro = QVBoxLayout()  # Nuevo layout para CPU Mastro
        self.control_layout = QHBoxLayout()

        self.layout_fcfs.addWidget(self.label_fcfs)
        self.layout_fcfs.addWidget(self.view_fcfs)
        self.layout_rr.addWidget(self.label_rr)
        self.layout_rr.addWidget(self.view_rr)
        self.layout_sjf.addWidget(self.label_sjf)
        self.layout_sjf.addWidget(self.view_sjf)
        self.layout_cpu_mastro.addWidget(self.label_cpu_mastro)
        self.layout_cpu_mastro.addWidget(self.view_cpu_mastro)  # Agregar la vista de CPU Mastro al layout

        self.cpu_layout = QHBoxLayout()
        self.cpu_layout.addLayout(self.layout_fcfs)
        self.cpu_layout.addLayout(self.layout_rr)
        self.cpu_layout.addLayout(self.layout_sjf)
        self.cpu_layout.addLayout(self.layout_cpu_mastro)  # Agregar el nuevo layout al layout principal

        self.start_button = QPushButton("Iniciar Simulación")
        self.random_button = QPushButton("Añadir Proceso Aleatorio")
        self.remove_button = QPushButton("Eliminar Último Proceso")
        self.proceso_add = QPushButton("Agregar Proceso CPU")

        self.control_layout.addWidget(self.start_button)
        self.control_layout.addWidget(self.random_button)
        self.control_layout.addWidget(self.remove_button)
        self.control_layout.addWidget(self.proceso_add)

        self.layout.addLayout(self.cpu_layout)
        self.layout.addLayout(self.control_layout)
        self.setLayout(self.layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_gantt)
        self.time = 0

        self.grid_width = 40
        self.grid_height = 20
        self.fcfs_processes = []
        self.rr_processes = []
        self.sjf_processes = []
        self.cpu_mastro_processes = []  # Lista para los procesos en CPU Mastro

        self.start_button.clicked.connect(self.start_simulation)
        self.random_button.clicked.connect(self.add_random_process)
        self.remove_button.clicked.connect(self.remove_last_process)
        self.proceso_add.clicked.connect(self.procesos_cpu)

        # Procesos predefinidos

    def random_color(self):
        """Genera un color aleatorio."""
        return QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    def add_process_to_fcfs(self, name, duration, arrival_time):
        color = self.random_color()
        process = Process(name, duration, color, arrival_time)
        self.fcfs_planner.add_process(process)
        self.fcfs_processes.append(process)


    def add_process_to_rr(self, name, duration, arrival_time):
        color = self.random_color()
        process = Process(name, duration, color, arrival_time)
        self.rr_planner.add_process(process)
        self.rr_processes.append(process)

    def add_process_to_sjf(self,name,duration,arrival_time):
        color = self.random_color()
        process = Process(name, duration, color, arrival_time)
        self.sjf_planner.add_process(process)
        self.sjf_processes.append(process)

    def add_random_process(self):
        """Añade un proceso con datos aleatorios al planificador con menos procesos."""
        # Generar datos aleatorios para el proceso
        name = f"P{len(self.cpu_mastro_processes) + 1}"
        duration = random.randint(1, 10)
        arrival_time = random.randint(0, 20)


        # Contar el número de procesos en cada planificador
        fcfs_count = len(self.fcfs_processes)
        rr_count = len(self.rr_processes)
        sjf_count = len(self.sjf_processes)

        # Determinar cuál planificador tiene menos procesos
        if fcfs_count <= rr_count and fcfs_count <= sjf_count:
            self.add_process_to_fcfs(name, duration, arrival_time)
        elif rr_count <= fcfs_count and rr_count <= sjf_count:
            self.add_process_to_rr(name, duration, arrival_time)
        else:
            self.add_process_to_sjf(name, duration, arrival_time)

        self.cpu_mastro_processes.append((name, duration, arrival_time))
        self.update_cpu_mastro_view()

    def procesos_cpu(self):
        """Escanea los procesos actuales en la CPU y los añade a las colas y a la vista de CPU Mastro."""
        processes = []  # Lista para almacenar procesos escaneados
        counter = 0
        for proc in psutil.process_iter(['pid', 'name', 'cpu_times']):
            try:
                # Obtener datos del proceso
                pid = proc.info['pid']
                name = proc.info['name']
                user_time = proc.info['cpu_times'].user  # Tiempo en modo usuario
                arrival_time = int(user_time)  # Usamos el tiempo de CPU como proxy de llegada
                duration = random.randint(1, 5)  # Generar una duración ficticia

                # Crear y almacenar el proceso
                processes.append((name, duration, arrival_time))
                if counter % 3 == 0:
                    # Agregar proceso al planificador FCFS
                    self.add_process_to_fcfs(str(pid), duration, arrival_time)
                elif counter % 3 == 1:
                    # Agregar proceso al planificador RR
                    self.add_process_to_rr(str(pid), duration, arrival_time)
                else:
                    # Agregar proceso al planificador SJF
                    self.add_process_to_sjf(str(pid), duration, arrival_time)

                # Agregar proceso al CPU Mastro
                self.cpu_mastro_processes.append((name, duration, arrival_time))

                # Opcional: imprimir detalles del proceso escaneado
                print(f"Proceso detectado: PID={pid}, Nombre={name}, Tiempo Usuario={user_time}")

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # Manejar excepciones si el proceso ya no está disponible
                continue
            counter += 1


        print(f"Se añadieron {len(processes)} procesos de la CPU a las colas de planificación.")

        # Llamar a la función que actualiza la vista de "CPU Mastro" después de agregar los procesos
        self.update_cpu_mastro_view()

    def update_cpu_mastro_view(self):
        """Actualiza la vista de CPU Mastro con los procesos actuales."""
        self.scene_cpu_mastro.clear()  # Limpiar la escena antes de dibujar
        y_offset = 0

        # Calcular el tiempo máximo para la vista de CPU Mastro
        max_time = 0
        for process in self.cpu_mastro_processes:
            max_time = max(max_time, process[2])  # Usamos arrival_time como tiempo máximo

        # Dibujar cuadrícula con base en el tiempo máximo
        self.draw_grid(self.scene_cpu_mastro, len(self.cpu_mastro_processes), max_time)

        # Dibujar los procesos en la nueva vista
        for process in self.cpu_mastro_processes:
            x_pos = 0  # Usar arrival_time como posición en 0
            block = self.scene_cpu_mastro.addRect(x_pos, y_offset, self.grid_width, self.grid_height,
                                                  QPen(QColor(0, 0, 0)), QBrush(self.random_color()))
            label = self.scene_cpu_mastro.addText(process[0])  # El nombre del proceso
            label.setPos(x_pos + 5, y_offset)  # Posicionar la etiqueta
            y_offset += self.grid_height

    def remove_last_process(self):
        """Elimina el último proceso de ambas listas y de los planificadores."""
        if self.fcfs_processes:
            last_fcfs = self.fcfs_processes.pop()
            self.fcfs_planner.pending_processes = [p for p in self.fcfs_planner.pending_processes if p != last_fcfs]

        if self.rr_processes:
            last_rr = self.rr_processes.pop()
            self.rr_planner.pending_processes = [p for p in self.rr_planner.pending_processes if p != last_rr]

        if self.sjf_processes:
            last_sjf = self.sjf_processes.pop()
            self.sjf_planner.pending_processes = [p for p in self.rr_planner.pending_processes if p != last_sjf]

    def start_simulation(self):
        # Limpiar los procesos antes de iniciar la simulación

        self.cpu_mastro_processes.clear()
        self.update_cpu_mastro_view()

        self.timer.start(10)

    def update_gantt(self):
        # Ejecutar FCFS
        self.fcfs_planner.execute_fcfs()
        self.draw_gantt(self.scene_fcfs, self.fcfs_processes)

        # Ejecutar Round Robin
        self.rr_planner.execute_rr()
        self.draw_gantt(self.scene_rr, self.rr_processes)

        #Ejecutar SJF
        self.sjf_planner.execute_rr()
        self.draw_gantt(self.scene_sjf, self.sjf_processes)

         # Verificar si todos los procesos han finalizado
        if not self.fcfs_planner.queue and not self.fcfs_planner.pending_processes and \
                not self.rr_planner.queue and not self.rr_planner.pending_processes and \
                not self.sjf_planner.queue and not self.sjf_planner.pending_processes:
            self.timer.stop()

    def draw_gantt(self, scene, processes):
        scene.clear()
        y_offset = 0

        # Calcular el tiempo máximo
        max_time = 0
        for process in processes:
            for time_slice in process.time_slices:
                max_time = max(max_time, time_slice)  # Tomamos el máximo tiempo alcanzado

        # Dibujar cuadrícula con base en el tiempo máximo
        self.draw_grid(scene, len(processes), max_time)

        for process in processes:
            for time_slice in process.time_slices:
                x_pos = time_slice * self.grid_width
                block = scene.addRect(x_pos, y_offset, self.grid_width, self.grid_height,
                                      QPen(QColor(0, 0, 0)), QBrush(process.color))
                label = scene.addText(process.name)
                label.setPos(x_pos + 5, y_offset)
            y_offset += self.grid_height

    def draw_grid(self, scene, num_processes, max_time):
        """Dibuja una cuadrícula sobre el gráfico con base en el número de procesos y el tiempo máximo."""
        # Dibujar líneas verticales (tiempo)
        for i in range(max_time + 2):  # Desde 0 hasta max_time
            x_pos = i * self.grid_width
            scene.addLine(x_pos, 0, x_pos, num_processes * self.grid_height, QPen(QColor(200, 200, 200)))

        # Dibujar líneas horizontales (procesos)
        for j in range(num_processes + 1):  # Número de procesos más 1 para la última línea
            y_pos = j * self.grid_height
            scene.addLine(0, y_pos, max_time * self.grid_width, y_pos, QPen(QColor(200, 200, 200)))


if __name__ == "__main__":
    app = QApplication([])
    window = GanttVisualizer()
    window.show()
    app.exec_()

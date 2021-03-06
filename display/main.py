__author__ = 'maicol'

import pygame
from components.label import Label
from components.button import Button
from components.cursor import Cursor
from components.chronometer import Chronometer
from components.timer import Timer
from instances.nxt import Nxt
from instances.butia import Butia

class Main():
    def __init__(self):
        # -- Inicio modulos
        pygame.init()
        # -- Obtencion de info del hardware
        self._info = pygame.display.Info()
        # -- Se crea un display utilizando la info
        self._display = pygame.display.set_mode([self._info.current_w, self._info.current_h], pygame.FULLSCREEN | pygame.HWSURFACE)
        # -- Se definen los controles
        self._fuente_top_label = pygame.font.Font(None, 48)
        self._fuente_board = pygame.font.Font(None, 30)
        self._top_label = Label(self._fuente_top_label, "Butia Control Dashboard v1.0", (255, 255, 255), (0, 0, 0))
        self._boton = Button(Label(self._fuente_top_label, "Salir", (255, 255, 255), (0, 0, 0)), Label(self._fuente_top_label, "Salir", (0, 0, 0), (255, 255, 255)))
        self._boton_pausar = Button(Label(self._fuente_top_label, "Pausar", (255, 255, 255), (0, 0, 0)), Label(self._fuente_top_label, "Pausar", (0, 0, 0), (255, 255, 255)))
        self._boton.set_rect(self._info.current_w/2 - self._boton.get_rect().width / 2, self._info.current_h - (self._boton.get_rect().height + 10))
        self._boton_pausar.set_rect(self._info.current_w/2 - self._boton_pausar.get_rect().width / 2, self._info.current_h / 4 * 3 - (self._boton_pausar.get_rect().height / 2))
        self._label_estado = Label(self._fuente_board, "Estado:", (255, 255, 255), (0, 0, 0))
        self._label_estado_informacion = Label(self._fuente_board, "", (255, 255, 255), (0, 0, 0))
        self._label_tarea = Label(self._fuente_board, "Tarea:", (255, 255, 255), (0, 0, 0))
        self._label_tarea_informacion = Label(self._fuente_board, "", (255, 255, 255), (0, 0, 0))
        self._label_error_butia = Label(self._fuente_board, "Revise la conexion con el butia (!)", (255, 255, 255), (0, 0, 0))
        self._label_error_nxt = Label(self._fuente_board, "Revise la conexion con el nxt (!)", (255, 255, 255), (0, 0, 0))
        self._cursor = Cursor()
        # -- Se definen las variables
        self._butia_error = True
        self._nxt_error = True
        self._salir = False
        self._reloj = pygame.time.Clock()
        self._chronometer = Chronometer(1)
        self._timer = None
        self._ready = True
        self._times = 0
        self._pause = False
        # -- Se crean las instancias de butia y nxt
        self._butia = Butia()
        self._nxt = Nxt()
        # -- Se definen los sensores nxt

    # -- DEFINICION DEL GAMELOOP
    def update(self):
        # -- Se actualizan los parametros
        # -- Deteccion de eventos
        for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    self._salir = True
                if event.type == pygame.MOUSEBUTTONDOWN:
                    btn1, btn2, btn3 = pygame.mouse.get_pressed()
                    if btn1:
                        if self._boton.on_click(self._cursor):
                            self._salir = True
                        if self._boton_pausar.on_click(self._cursor):
                            if self._pause:
                                self._pause = False
                            elif not self._pause:
                                self._pause = True
        # -- Obtencion del info del entorno
        # -- Comprobacion de conexiones
        if self._butia.get_butia().getFirmwareVersion() == -1:
            self._butia_error = True
        else:
            self._butia_error = False
        if not self._nxt.get_nxt():
            self._nxt_error = True
        else:
            self._nxt_error = False
        # -- Se corre el seguidor solo si la conexion funciona
        if not self._pause:
            if not self._butia_error and not self._nxt_error:
                if self._butia.get_butia().getGray(5) < 14000 and self._butia.get_butia().getGray(2) < 40000:
                        self._butia.get_butia().set2MotorSpeed(1, 600, 1, 600)
                elif self._butia.get_butia().getGray(5) < 14000 and self._butia.get_butia().getGray(2) > 40000:
                        self._butia.get_butia().set2MotorSpeed(1, 600, 0, 600)
                elif self._butia.get_butia().getGray(5) > 14000 and self._butia.get_butia().getGray(2) < 40000:
                        self._butia.get_butia().set2MotorSpeed(0, 600, 1, 600)
                if self._nxt.get_nxt().get_port(1).getSample() < 20:
                    if self._ready:
                        self._label_tarea_informacion.set_text("Recogiendo muestras")
                        self._label_tarea_informacion.update(self._display, self._info.current_w/4 + self._label_estado.get_rect().width + 20, self._info.current_h/3 + 10 + self._label_estado_informacion.get_rect().height)
                        self.accionar_mecanismo()
                self._label_tarea_informacion.set_text("Recorriendo el mundo")
            self._label_tarea_informacion.set_text("Ninguna")
        else:
            self._label_tarea_informacion.set_text("Pausado")
            self._butia.get_butia().set2MotorSpeed(0, 0, 0, 0)

    def accionar_mecanismo(self):
        # -- Secuencia que realiza la pala
        # -- Ajustar valores de rotacion para alcanzar la medida exacta
        self._ready = False
        self._butia.get_butia().set2MotorSpeed(0, 0, 0, 0)
        self._nxt.get_nxt().get_port("a").turn(-20, 160)
        self._nxt.get_nxt().get_port("b").turn(20, 640)
        try:
            self._nxt.get_nxt().get_port("a").turn(20, 220)
        except Exception:
            self._nxt.get_nxt().get_port("b").turn(-20, 10)
            self._nxt.get_nxt().get_port("a").turn(20, 110)
        self._nxt.get_nxt().get_port("b").turn(-20, 320)
        self._nxt.get_nxt().get_port("a").turn(-20, 110)
        self._nxt.get_nxt().get_port("b").turn(-20, 320)
        #self.motorA.turn(-20, 110)
        self._nxt.get_nxt().get_port("a").turn(20, 90)
        self._times += 1
        if self._times < 3:
            self.motorC.turn(-20, 450)
        else:
            self._nxt.get_nxt("a").turn(-20, 50)
            self._nxt.get_nxt("c").turn(20, 450*2)
            self._nxt.get_nxt("a").turn(20, 50)
            self._times = 0
            self._timer = Timer(5)

    def render(self):
        # -- Se redibuja la pantalla con las actualizaciones pertinentes
        self._display.fill((0, 0, 0))
        self._boton.on_collide(self._display, self._cursor)
        self._boton_pausar.on_collide(self._display, self._cursor)
        self._cursor.update()
        self._top_label.update(self._display, self._info.current_w/2 - self._top_label.get_rect().width/2, 10)
        self._label_estado.update(self._display, self._info.current_w/4, self._info.current_h/3)
        self._label_estado_informacion.update(self._display, self._info.current_w/4 + self._label_estado.get_rect().width + 20, self._info.current_h/3)
        self._label_tarea.update(self._display, self._info.current_w/4, self._info.current_h/3  + 10 + self._label_estado.get_rect().height)
        self._label_tarea_informacion.update(self._display, self._info.current_w/4 + self._label_estado.get_rect().width + 20, self._info.current_h/3 + 10 + self._label_estado_informacion.get_rect().height)
        if not self._butia_error and not self._nxt_error:
            self._label_estado_informacion.set_text("Activo")
        if self._butia_error and self._chronometer.get_value():
            self._label_error_butia.update(self._display, self._info.current_w/5 * 3, self._info.current_h/3)
            self._label_estado_informacion.set_text("Error")
        if self._nxt_error and self._chronometer.get_value():
            self._label_error_nxt.update(self._display, self._info.current_w/5 * 3, self._info.current_h/3 + 10 + self._label_error_nxt.get_rect().height)
            self._label_estado_informacion.set_text("Error")
        pygame.display.flip()

    def sleep(self):
        # -- Se espera
        self._reloj.tick(100)

    def run(self):
        while not self._salir:
            self.update()
            self.render()
            self.sleep()

    def set_ready(self):
        self._ready = True

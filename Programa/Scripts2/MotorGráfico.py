import pygame as pg
import moderngl as mgl
import sys
from Geometria2 import *
from camara import Camara

class MotorGrafico:
    def __init__(self, tamaño_ventana=(1600,900)):
        # inicializamos los módulos de pygame
        pg.init()
        
        self.TAM_VENT = tamaño_ventana
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
        
        # creamos un contexto de opengl
        pg.display.set_mode(self.TAM_VENT, flags=pg.OPENGL | pg.DOUBLEBUF)
        
        # detectar y usar un contexto existente
        self.ctx = mgl.create_context()
        
        # creamos un objeto para contar el tiempo
        self.reloj = pg.time.Clock()
        
        self.camara = Camara(self)
        
        self.scene = poliedro(*importarOBJ("Modelos/cubo.obj"),1,np.array([1,1,1]),np.array([1,1,1]),np.array([0,0,0]),0,np.array([0,0,0]),np.array([0,0,0]),True,self)
        
    ## Esta función sirve para comprobar eventos del tipo cerrar la ventana
    def comprobar_eventos(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                self.scene.destruir()
                pg.quit()
                sys.exit()
    
    def renderizar(self):
        ## limpiamos el primer buffer
        self.ctx.clear(color=(0.08, 0.16, 0.18))
        
        self.scene.renderizar()
        
        ## Intercambiamos el buffer de coloreado por el buffer de disposición
        pg.display.flip()
        
        
    def ejecutar(self):
        while True:
            self.comprobar_eventos()
            self.renderizar()
            self.reloj.tick(60)
            
app = MotorGrafico()
app.ejecutar()
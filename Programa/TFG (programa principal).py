## DETECCIÃ“N DE COLISIONES USANDO TEOREMA DEL EJE SEPARADOR ##

import numpy as np
import time
from qpsolvers import solve_qp

import pygame as pg
import moderngl as mgl
import sys
import glm

from Scripts2 import camara
from Scripts2 import iluminacion

from Scripts2 import Geometria as geo ## Módulo que incluye las clases y funciones necesarias para la creación y el movimiento de los polígonos.
from Scripts2 import ColisionesSAT as SAT ## Módulo que incluye todas las funciones encargadas de la detección de colisiones a través del teorema del eje separador (SAT)
from Scripts2 import RecorteSH as SH ## Módulo que incluye las funciones encargadas de la obtención del collision manifold por medio del algoritmo de recorte de Sutherland-Hodgeman


## PARÁMETROS DE LA SIMULACIÓN ##

T = 20 ## segundos
dt = 0.01
t = np.arange(0,T,dt)


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
        
        # Esconder el ratón
        pg.event.set_grab(True)
        pg.mouse.set_visible(False)
        
        # detectar y usar un contexto existente
        self.ctx = mgl.create_context()
        self.ctx.enable(flags=mgl.DEPTH_TEST)
        
        # creamos un objeto para contar el tiempo
        self.reloj = pg.time.Clock()
        self.time = 0
        self.delta_time = 0
        
        ## iluminacion
        self.light = iluminacion.Light()
        
        ## camara
        self.camara = camara.Camara(self)
        
        ## lista de objetos
        self.scene = []
        
        self.skybox = None
        
    ## Esta función sirve para comprobar eventos del tipo cerrar la ventana
    def comprobar_eventos(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                for i in range(len(self.scene)):
                    self.scene[i].destruir()
                pg.quit()
                sys.exit()
    
    def renderizar(self):
        ## limpiamos el primer buffer
        self.ctx.clear(color=(0.08, 0.16, 0.18))
        
        for i in range(len(self.scene)):
            self.scene[i].renderizar()
        self.skybox.renderizar()
        ## Intercambiamos el buffer de coloreado por el buffer de disposición
        pg.display.flip()
        
    def getTiempo(self):
        return pg.time.get_ticks() * 0.001
        
        
    def ejecutar(self):
        dt = 0.025
        cooldown = 0.5
        t = 0
        t2 = 0
        while True:
            self.comprobar_eventos()
            self.camara.update()
            self.renderizar()
            self.delta_time = self.reloj.tick(60)
            Update(dt)
            t += dt
            
            state = pg.mouse.get_pressed()   
            if state[0] == True:
                dt = 0.0025
            else:
                dt = 0.020
            if state[2] == True and t > (t2 + cooldown):
                disparar(self.camara.position,self.camara.forward)
                t2 = t
            
                
            
app = MotorGrafico()
app.skybox = geo.skyBox(app,"skybox1\\")


## CREACIÓN DE OBJETOS ##

def addObject(Malla3D,Masa,Escala,Posicion,EjeRot,AnguloRot,Velocidad,VelocidadAngular,Estatico,Textura,Ntextura):
    app.scene.append(geo.poliedro(*geo.importarOBJ(Malla3D),Masa,Escala,Posicion,EjeRot,AnguloRot*(np.pi/180),Velocidad,VelocidadAngular,Estatico,app,glm.vec3(1,0,0),Textura,Ntextura)) ## Añadimos un nuevo elemento a la lista de objetos
    
    
def disparar(pos, forward):
    
    v = 30 
    
    addObject(Malla3D           =   "Modelos/cubo.obj",
          Masa              =   10,
          Escala            =   np.array([1,1,1],dtype=float),
          Posicion          =   np.array([pos[0],pos[1],pos[2]],dtype=float),
          EjeRot            =   np.array([3,3,3],dtype=float), 
          AnguloRot         =   0,
          Velocidad         =   np.array([forward[0]*v,forward[1]*v,forward[2]*v],dtype=float),
          VelocidadAngular  =   np.array([1,1,1],dtype=float),
          Estatico          =   False,
          Textura           =   "azul.jpg",
          Ntextura          =   1)           

# Ejemplo suelo

addObject(Malla3D           =   "Modelos/cubo.obj",
          Masa              =   10,
          Escala            =   np.array([1,1,1],dtype=float),
          Posicion          =   np.array([30,1,0],dtype=float),
          EjeRot            =   np.array([3,3,3],dtype=float), 
          AnguloRot         =   0,
          Velocidad         =   np.array([0,0,0],dtype=float),
          VelocidadAngular  =   np.array([0,0,0],dtype=float),
          Estatico          =   False,
          Textura           =   "caja.jpg",
          Ntextura          =   1)            


addObject(Malla3D           =   "Modelos/cubo.obj",
          Masa              =   10,
          Escala            =   np.array([1,1,1],dtype=float),
          Posicion          =   np.array([30,3,0],dtype=float),
          EjeRot            =   np.array([3,3,3],dtype=float), 
          AnguloRot         =   0,
          Velocidad         =   np.array([0,0,0],dtype=float),
          VelocidadAngular  =   np.array([0,0,0],dtype=float),
          Estatico          =   False,
          Textura           =   "caja.jpg",
          Ntextura          =   1)         

addObject(Malla3D           =   "Modelos/cubo.obj",
          Masa              =   10,
          Escala            =   np.array([1,1,1],dtype=float),
          Posicion          =   np.array([30,6,0],dtype=float),
          EjeRot            =   np.array([3,3,3],dtype=float), 
          AnguloRot         =   0,
          Velocidad         =   np.array([0,0,0],dtype=float),
          VelocidadAngular  =   np.array([0,0,0],dtype=float),
          Estatico          =   False,
          Textura           =   "caja.jpg",
          Ntextura          =   1)         

addObject(Malla3D           =   "Modelos/convexo.obj",
          Masa              =   40,
          Escala            =   np.array([1,1,1],dtype=float),
          Posicion          =   np.array([70,7,0],dtype=float),
          EjeRot            =   np.array([3,3,3],dtype=float), 
          AnguloRot         =   0,
          Velocidad         =   np.array([-30,0,0],dtype=float),
          VelocidadAngular  =   np.array([0,0,0],dtype=float),
          Estatico          =   False,
          Textura           =   "azul.jpg",
          Ntextura          =   1)          


## Suelo (Estático True y masa muy elevada para que no lo muevan las colisiones)
addObject(Malla3D           =   "Modelos/cubo.obj",
          Masa              =   999999999999999,
          Escala            =   np.array([100,1,100],dtype=float),
          Posicion          =   np.array([40,-3,0],dtype=float),
          EjeRot            =   np.array([1,1,0],dtype=float),
          AnguloRot         =   0,
          Velocidad         =   np.array([0,0,0],dtype=float),
          VelocidadAngular  =   np.array([0,0,0],dtype=float),
          Estatico          =   True,
          Textura           =   "hormigon.jpg",
          Ntextura          =   5)            


#EJEMPLO SIN GRAVEDAD
"""
addObject(Malla3D           =   "Modelos/cubo.obj",
          Masa              =   10,
          Escala            =   np.array([1,1,1],dtype=float),
          Posicion          =   np.array([0,1,30],dtype=float),
          EjeRot            =   np.array([3,3,3],dtype=float), 
          AnguloRot         =   0,
          Velocidad         =   np.array([0,0,-30],dtype=float),
          VelocidadAngular  =   np.array([0,0,0],dtype=float),
          Estatico          =   True,
          Textura           =   "caja.jpg",
          Ntextura          =   1)   

addObject(Malla3D           =   "Modelos/cubo.obj",
          Masa              =   10,
          Escala            =   np.array([1,1,1],dtype=float),
          Posicion          =   np.array([0,30,0],dtype=float),
          EjeRot            =   np.array([3,3,3],dtype=float), 
          AnguloRot         =   0,
          Velocidad         =   np.array([0,-30,0],dtype=float),
          VelocidadAngular  =   np.array([0,0,0],dtype=float),
          Estatico          =   True,
          Textura           =   "caja.jpg",
          Ntextura          =   1)    

addObject(Malla3D           =   "Modelos/cubo.obj",
          Masa              =   10,
          Escala            =   np.array([1,1,1],dtype=float),
          Posicion          =   np.array([30,1,0],dtype=float),
          EjeRot            =   np.array([3,3,3],dtype=float), 
          AnguloRot         =   0,
          Velocidad         =   np.array([-30,0,0],dtype=float),
          VelocidadAngular  =   np.array([0,0,0],dtype=float),
          Estatico          =   True,
          Textura           =   "hormigon.jpg",
          Ntextura          =   1)    

addObject(Malla3D           =   "Modelos/convexo.obj",
          Masa              =   100,
          Escala            =   np.array([1,1,1],dtype=float),
          Posicion          =   np.array([0,0,2],dtype=float),
          EjeRot            =   np.array([0,0,0],dtype=float),
          AnguloRot         =   0,
          Velocidad         =   np.array([0,0,0],dtype=float),
          VelocidadAngular  =   np.array([0,0,0],dtype=float),
          Estatico          =   True,
          Textura           =   "caja.jpg",
          Ntextura          =   1)   
"""

# EJEMPLO DE MURO QUE CAE ENTRE CUATRO PIRÁMIDES

"""
addObject(Malla3D           =   "Modelos/Piramide.obj",
          Masa              =   10,
          Escala            =   np.array([1,1,1],dtype=float),
          Posicion          =   np.array([5,-1.5,0],dtype=float),
          EjeRot            =   np.array([1,0,0],dtype=float), 
          AnguloRot         =   -90,
          Velocidad         =   np.array([0,0,0],dtype=float),
          VelocidadAngular  =   np.array([0,0,0],dtype=float),
          Estatico          =   False,
          Textura           =   "caja.jpg",
          Ntextura          =   1)   
addObject(Malla3D           =   "Modelos/Piramide.obj",
          Masa              =   10,
          Escala            =   np.array([1,1,1],dtype=float),
          Posicion          =   np.array([7.5,-1.5,0],dtype=float),
          EjeRot            =   np.array([1,0,0],dtype=float), 
          AnguloRot         =   -90,
          Velocidad         =   np.array([0,0,0],dtype=float),
          VelocidadAngular  =   np.array([0,0,0],dtype=float),
          Estatico          =   False,
          Textura           =   "caja.jpg",
          Ntextura          =   1)   
addObject(Malla3D           =   "Modelos/Piramide.obj",
          Masa              =   10,
          Escala            =   np.array([1,1,1],dtype=float),
          Posicion          =   np.array([5,-1.5,2.5],dtype=float),
          EjeRot            =   np.array([1,0,0],dtype=float), 
          AnguloRot         =   -90,
          Velocidad         =   np.array([0,0,0],dtype=float),
          VelocidadAngular  =   np.array([0,0,0],dtype=float),
          Estatico          =   False,
          Textura           =   "caja.jpg",
          Ntextura          =   1)   
addObject(Malla3D           =   "Modelos/Piramide.obj",
          Masa              =   10,
          Escala            =   np.array([1,1,1],dtype=float),
          Posicion          =   np.array([7.5,-1.5,2.5],dtype=float),
          EjeRot            =   np.array([1,0,0],dtype=float), 
          AnguloRot         =   -90,
          Velocidad         =   np.array([0,0,0],dtype=float),
          VelocidadAngular  =   np.array([0,0,0],dtype=float),
          Estatico          =   False,
          Textura           =   "caja.jpg",
          Ntextura          =   1)   

addObject(Malla3D           =   "Modelos/cubo.obj",
          Masa              =   10,
          Escala            =   np.array([3,1,3],dtype=float),
          Posicion          =   np.array([6.25,6,1.25],dtype=float),
          EjeRot            =   np.array([1,0,0],dtype=float), 
          AnguloRot         =   -90,
          Velocidad         =   np.array([0,0,0],dtype=float),
          VelocidadAngular  =   np.array([0,0,0],dtype=float),
          Estatico          =   False,
          Textura           =   "caja.jpg",
          Ntextura          =   1)   

addObject(Malla3D           =   "Modelos/cubo.obj",
          Masa              =   999999999999999,
          Escala            =   np.array([100,1,100],dtype=float),
          Posicion          =   np.array([40,-3,0],dtype=float),
          EjeRot            =   np.array([1,1,0],dtype=float),
          AnguloRot         =   0,
          Velocidad         =   np.array([0,0,0],dtype=float),
          VelocidadAngular  =   np.array([0,0,0],dtype=float),
          Estatico          =   True,
          Textura           =   "hormigon.jpg",
          Ntextura          =   5)     
"""

# EJEMPLO DE BALDOSA QUE CAE ENTRE CUATRO PIRÁMIDES

"""
addObject(Malla3D           =   "Modelos/Piramide.obj",
          Masa              =   10,
          Escala            =   np.array([1,1,1],dtype=float),
          Posicion          =   np.array([5,-1.5,0],dtype=float),
          EjeRot            =   np.array([1,0,0],dtype=float), 
          AnguloRot         =   -90,
          Velocidad         =   np.array([0,0,0],dtype=float),
          VelocidadAngular  =   np.array([0,0,0],dtype=float),
          Estatico          =   False,
          Textura           =   "caja.jpg",
          Ntextura          =   1)   
addObject(Malla3D           =   "Modelos/Piramide.obj",
          Masa              =   10,
          Escala            =   np.array([1,1,1],dtype=float),
          Posicion          =   np.array([7.5,-1.5,0],dtype=float),
          EjeRot            =   np.array([1,0,0],dtype=float), 
          AnguloRot         =   -90,
          Velocidad         =   np.array([0,0,0],dtype=float),
          VelocidadAngular  =   np.array([0,0,0],dtype=float),
          Estatico          =   False,
          Textura           =   "caja.jpg",
          Ntextura          =   1)   
addObject(Malla3D           =   "Modelos/Piramide.obj",
          Masa              =   10,
          Escala            =   np.array([1,1,1],dtype=float),
          Posicion          =   np.array([5,-1.5,2.5],dtype=float),
          EjeRot            =   np.array([1,0,0],dtype=float), 
          AnguloRot         =   -90,
          Velocidad         =   np.array([0,0,0],dtype=float),
          VelocidadAngular  =   np.array([0,0,0],dtype=float),
          Estatico          =   False,
          Textura           =   "caja.jpg",
          Ntextura          =   1)   
addObject(Malla3D           =   "Modelos/Piramide.obj",
          Masa              =   10,
          Escala            =   np.array([1,1,1],dtype=float),
          Posicion          =   np.array([7.5,-1.5,2.5],dtype=float),
          EjeRot            =   np.array([1,0,0],dtype=float), 
          AnguloRot         =   -90,
          Velocidad         =   np.array([0,0,0],dtype=float),
          VelocidadAngular  =   np.array([0,0,0],dtype=float),
          Estatico          =   False,
          Textura           =   "caja.jpg",
          Ntextura          =   1)   

addObject(Malla3D           =   "Modelos/cubo.obj",
          Masa              =   10,
          Escala            =   np.array([3,3,1],dtype=float),
          Posicion          =   np.array([6.25,6,1.25],dtype=float),
          EjeRot            =   np.array([1,0,0],dtype=float), 
          AnguloRot         =   -90,
          Velocidad         =   np.array([0,0,0],dtype=float),
          VelocidadAngular  =   np.array([0,0,0],dtype=float),
          Estatico          =   False,
          Textura           =   "caja.jpg",
          Ntextura          =   1)   

addObject(Malla3D           =   "Modelos/cubo.obj",
          Masa              =   999999999999999,
          Escala            =   np.array([100,1,100],dtype=float),
          Posicion          =   np.array([40,-3,0],dtype=float),
          EjeRot            =   np.array([1,1,0],dtype=float),
          AnguloRot         =   0,
          Velocidad         =   np.array([0,0,0],dtype=float),
          VelocidadAngular  =   np.array([0,0,0],dtype=float),
          Estatico          =   True,
          Textura           =   "hormigon.jpg",
          Ntextura          =   5)    
"""
# EJEMPLO CAJAS ENCIMA DE CAJAS (Este ejemplo demuestra las limitaciones que tiene este simulador: los objetos que se amontonan unos encima de otros no son estables)
"""
addObject(Malla3D           =   "Modelos/cubo.obj",
          Masa              =   10,
          Escala            =   np.array([1,1,1],dtype=float),
          Posicion          =   np.array([30,1,0],dtype=float),
          EjeRot            =   np.array([3,3,3],dtype=float), 
          AnguloRot         =   0,
          Velocidad         =   np.array([0,0,0],dtype=float),
          VelocidadAngular  =   np.array([0,0,0],dtype=float),
          Estatico          =   False,
          Textura           =   "caja.jpg",
          Ntextura          =   1)             

addObject(Malla3D           =   "Modelos/cubo.obj",
          Masa              =   10,
          Escala            =   np.array([1,1,1],dtype=float),
          Posicion          =   np.array([30,5,0],dtype=float),
          EjeRot            =   np.array([3,3,3],dtype=float), 
          AnguloRot         =   0,
          Velocidad         =   np.array([0,0,0],dtype=float),
          VelocidadAngular  =   np.array([0,0,0],dtype=float),
          Estatico          =   False,
          Textura           =   "caja.jpg",
          Ntextura          =   1)        

addObject(Malla3D           =   "Modelos/cubo.obj",
          Masa              =   10,
          Escala            =   np.array([1,1,1],dtype=float),
          Posicion          =   np.array([30,8,0],dtype=float),
          EjeRot            =   np.array([3,3,3],dtype=float), 
          AnguloRot         =   0,
          Velocidad         =   np.array([0,0,0],dtype=float),
          VelocidadAngular  =   np.array([0,0,0],dtype=float),
          Estatico          =   False,
          Textura           =   "caja.jpg",
          Ntextura          =   1)           

addObject(Malla3D           =   "Modelos/cubo.obj",
          Masa              =   9999999999999999999,
          Escala            =   np.array([100,1,100],dtype=float),
          Posicion          =   np.array([0,-3,-20],dtype=float),
          EjeRot            =   np.array([1,1,0],dtype=float),
          AnguloRot         =   0,
          Velocidad         =   np.array([0,0,0],dtype=float),
          VelocidadAngular  =   np.array([0,0,0],dtype=float),
          Estatico          =   True,
          Textura           =   "hormigon.jpg",
          Ntextura          =   5)            
"""





## INTEGRACIÓN Y DETECCIÓN DE COLISIONES ##

tiempo = time.time()

Ecin = np.zeros(len(t))
Epot = np.zeros(len(t))


def Update(dt):
    
    Nobjetos = len(app.scene)
    ## ACTUALIZACIÓN DE POSICIONES
    for j in range(Nobjetos):
        obj = app.scene[j]
        
        wmod = np.linalg.norm(obj.w)
        if wmod == 0:
            wmod = 1
        
        if obj.estatico == False and obj.colisionando == False:
            Traslacion = np.array([obj.v[0]*dt,-(1/2)*9.8*dt**2+obj.v[1]*dt,obj.v[2]*dt])
            obj.colisionando = False
        else:
            Traslacion = np.array([obj.v[0]*dt,obj.v[1]*dt,obj.v[2]*dt])
        
        theta = wmod*dt
        
        if obj.estatico == False:
            obj.v -= np.array([0,9.8,0])*dt
        obj.actualizarVertices(Traslacion, obj.w,theta)
        obj.actualizarCM(Traslacion)
        
    
        if np.linalg.norm(obj.v) > 0: ## Como no hay fricción programada, para que los objetos no se muevan infinitamente incluyo una "pseudofricción", que simplemente disminuye a lo largo del tiempo la magnitud de las velocidades
            obj.v -= obj.v*dt*0.3
            obj.w -= obj.w*dt*0.3
            
        
        obj.actualizarBoundingBox() # Actualizamos las bounding boxes de todos los objetos
    
    ## BÚSQUEDA DE COLISIONES Y COLISION MANIFOLDS
    
    DatosColision = [] ## Aquí almacenaremos CADA PUNTO de colisión, incluyendo el caso de varios puntos de colisión por objeto. Cada punto de colisión llevará consigo además una referencia a los objetos chocantes y la normal del choque
    
    for j in range(Nobjetos):
        for k in range(Nobjetos):
            if k > j: ## Condición necesaria para no repetir pares de objetos
                colisionData = SAT.BuscarColision(app.scene[j],app.scene[k])
                if colisionData[0] == True: ## Si se detecta colisión entre j y k, hacemos el cálculo de puntos / áreas de impacto
                    if colisionData[1] == "cara": ## Si es de tipo cara, usamos las librerias de RecorteSH para obtener el colision manifold:
                        indiceRef = j if colisionData[2][0] == 0 else k
                        indiceInc = j if colisionData[3][0] == 0 else k
                        caraRef = app.scene[indiceRef].getCara(colisionData[2][1])
                        caraIn  = app.scene[indiceInc].getCara(colisionData[3][1])
                        
                        colisionData2 = SH.RecorteSH(caraRef,caraIn) ## Obtenemos la porción de cara incidente encerrada bajo la cara referente
                        vN = geo.NormalPlano(caraRef[0], caraRef[1], caraRef[2]) ## Calculamos el vector normal a la cara referente
                        alturasVectores = np.dot(colisionData2,vN) ## Calculamos la profundidad de penetración de cada vector perteneciente a la cara encerrada incidente (colisionData2)
                        
                        minV = min(alturasVectores) ## Obtenemos el mínimo valor de altura (máxima penetración)
                        colisionManifold = []
                        
                        for l in range(len(alturasVectores)): ## Recorremos todos los vectores de la cara incidente encerrada por el clipping SH
                            if alturasVectores[l] <= minV + 1e-1:
                                colisionManifold.append(colisionData2[l]) ## El collision manifold estará compuesto por el/los vectores mínimos y el resto de vectores que estén cierto margen de error encima de este.
                                DatosColision.append([colisionData2[l],indiceRef,indiceInc,colisionData[-1]])
                        
                        ## Como resultado, hemos obtenido un collision manifold que puede ser o bien un punto, o bien un segmento, o bien un polígono entero.
                        ## Ahora, para el caso de que obtengamos o bien un segmento o bien un polígono, calculamos su "centro de masas":
                        ## Bueno no se, tiene pinta que va a ser mejor aplicar el impulso a varios puntos simultáneamente. Simplemente la cantidad de
                        ## impulso por punto para N puntos será j/N.
                        
                        
                        
                        
                        
                    elif colisionData[1] == "arista-arista":
                        indiceRef = j if colisionData[3] == 0 else  k
                        indiceInc = j if colisionData[4] == 0 else  k
                        arista1 = app.scene[j].getArista(colisionData[2][0])
                        arista2 = app.scene[k].getArista(colisionData[2][1])
                        corte = SH.minSepAristas(arista1,arista2)
                        DatosColision.append([corte[0],indiceRef,indiceInc,colisionData[-1]])
                        
                    app.scene[indiceRef].colisionando = True
                    app.scene[indiceInc].colisionando = True
                    
                    
    if len(DatosColision)>0:
        j = respuestaColision(DatosColision)
        for i in range(len(DatosColision)):
            p, Ref, Inc, N = DatosColision[i]
            jRef = -j[i]*N ## El objeto de referencia tiene que rebotar en sentido opuesto a la normal
            jInc = j[i]*N ## Mismo módulo pero sentido opuesto
            app.scene[Ref].addImpulso(p,jRef)
            app.scene[Inc].addImpulso(p,jInc)


## RESPUESTA A COLISIONES ##

def velPunto(obj,p):
    r = p - obj.pos
    vAng = np.cross(obj.w,r)
    return obj.v + vAng

def respuestaColision(DatosColision): ##Como convenio usare vrel = vref - vin
    N = len(DatosColision) ## Número de colisiones
    A = np.zeros((N,N))
    dpre = np.zeros(N)
    b = np.zeros(N)
    c = np.zeros(N)
    
    e = 0.85 ## coef. restitución
    
    for i in range(N):
        puntoi = DatosColision[i][0] ## Punto de colisión i-ésimo
        ref = DatosColision[i][1]
        inc = DatosColision[i][2]
        Ni = DatosColision[i][3] ## Normal al punto de colisión i
        objRef = app.scene[ref]
        objInc = app.scene[inc]
        
        riInc = puntoi - objInc.pos
        riRef = puntoi - objRef.pos
        
        ## OBTENEMOS LOS TENSORES DE INERCIA EN LA REFERENCIA GLOBAL (MULTIPLICAMOS LA INERCIA LOCAL POR LA INVERSA DE LA ROTACIÓN DEL OBJETO)
        
        Rrefinv = np.linalg.inv(objRef.estadoRotacion) ## obtenemos la matriz de rotación que devuelve a cada objeto a su estado sin rotar (estado rotacional donde hemos calculado originalmente el tensor de inercia)
        Rincinv = np.linalg.inv(objInc.estadoRotacion)
        Iref = np.matmul(Rrefinv,np.matmul(objRef.I,np.transpose(Rrefinv)))
        Iinc = np.matmul(Rincinv,np.matmul(objInc.I,np.transpose(Rincinv)))
        invIref = np.linalg.inv(Iref)
        invIinc = np.linalg.inv(Iinc)
        dpre[i] = np.dot(Ni,velPunto(objInc,puntoi) - velPunto(objRef,puntoi)) ## Definimos el vector velocidades pre-impulso
        b[i] = 0 if dpre[i] >= 0 else 2*dpre[i] ## Definimos el vector b
        c[i] = abs(dpre[i]) ## Definimos el vector c
        
        for j in range(i,N): ## Recorremos solo el triángulo superior porque la matriz A es simétrica
            puntoj = DatosColision[j][0]
            o1 = DatosColision[j][1]
            o2 = DatosColision[j][2]
            Nj = DatosColision[j][3] ## Normal al punto de colisión j
            
            rjInc = puntoj - objInc.pos
            rjRef = puntoj - objRef.pos
            
            if o1 == inc or o2 == inc:
                sumandoInc = (1/objInc.m)*np.dot(Ni,Nj) + np.dot(np.cross(riInc,Ni),np.matmul(invIinc,np.cross(rjInc,Nj)))
            else: ## Si el punto de colisión j no pertenece al objeto inc, entonces el sumandoInc es 0
                sumandoInc = 0
                
            if o1 == ref or o2 == ref:
                sumandoRef = (1/objRef.m)*np.dot(Ni,Nj) + np.dot(np.cross(riRef,Ni),np.matmul(invIref,np.cross(rjRef,Nj)))
            else: ## Si el punto de colisión j no pertenece al objeto inc, entonces el sumandoInc es 0
                sumandoRef = 0 
                
            A[i,j] = sumandoInc + sumandoRef
            A[j,i] = A[i,j] ## A es simétrica
    
    
    ## Por último vamos a construir la matriz de restricciónes usando bloques:
    I = np.eye(N)
    B = np.block([
        [-I],
        [-A],
        [A]
    ])
    k = np.block([ ## Como dato, numpy usa una notación de vectores inversa a la habitual. Osea un vector que de normal se representaría de pie, numpy lo considera tumbado y viceversa
        [np.zeros(N),b,c-b]
    ])
    
    Q = np.matmul(A.transpose(),A)*2
    q = np.dot(b,A)*2
    
    j = solve_qp(Q,q,B,k,A=None,b=None,solver = "gurobi")
    

    if type(j) == type(None):   
        j = np.zeros(N)
        B = np.block([
            [-I],
            [-A]
        ])
        k = np.block([ ## Como dato, numpy usa una notación de vectores inversa a la habitual. Osea un vector que de normal se representaría de pie, numpy lo considera tumbado y viceversa
            [np.zeros(N),b]
        ])
        
        j = solve_qp(Q,q,B,k,A=None,b=None,solver = "gurobi")
    
    """print(DatosColision)
    print(dpre)"""

    j*=e
    
    return j
    
print(time.time()-tiempo)
app.ejecutar()



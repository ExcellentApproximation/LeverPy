import glm
import pygame as pg

FOV = 50
NEAR = 0.1
FAR = 500
SPEED = 0.01
SENSITIVITY = 0.05

class Camara:
    def __init__(self,app, position = (30,10,30), yaw = 230, pitch = 0):
        self.app = app
        self.aspect_ratio = app.TAM_VENT[0] / app.TAM_VENT[1]
        self.position = glm.vec3(position)
        self.up = glm.vec3(0,1,0)
        self.right = glm.vec3(1,0,0)
        self.forward = glm.vec3(0,0,-1)
        self.yaw = yaw
        self.pitch = pitch
        # matriz de visión
        self.m_view = self.obtener_matriz_vision()
        # matriz de proyección
        self.m_proj = self.obtener_matriz_proyeccion()
    
    def rotar(self):
        rel_x,rel_y = pg.mouse.get_rel()
        self.yaw += rel_x * SENSITIVITY
        self.pitch -= rel_y * SENSITIVITY
        self.pitch = max(-89, min(89, self.pitch))
    
    def actualizar_vectores_camara(self):
        yaw, pitch = glm.radians(self.yaw), glm.radians(self.pitch)
        
        self.forward.x = glm.cos(yaw) * glm.cos(pitch)
        self.forward.y = glm.sin(pitch)
        self.forward.z = glm.sin(yaw) * glm.cos(pitch)
        
        self.forward = glm.normalize(self.forward)
        self.right = glm.normalize(glm.cross(self.forward,glm.vec3(0,1,0)))
    
    def update(self):
        self.mover()
        self.rotar()
        self.actualizar_vectores_camara()
        self.m_view = self.obtener_matriz_vision()
    
    def mover(self):
        velocidad = SPEED * self.app.delta_time
        keys = pg.key.get_pressed()
        if keys[pg.K_LSHIFT]:
            velocidad *= 5
        if keys[pg.K_w]:
            self.position += self.forward * velocidad
        if keys[pg.K_s]:
            self.position -= self.forward * velocidad
        if keys[pg.K_a]:
            self.position -= self.right * velocidad
        if keys[pg.K_d]:
            self.position += self.right * velocidad
        if keys[pg.K_q]:
            self.position += self.up * velocidad
        if keys[pg.K_e]:
            self.position -= self.up * velocidad
            
            
    
    def obtener_matriz_vision(self):
        return glm.lookAt(self.position,self.position + self.forward,self.up)
    
    def obtener_matriz_proyeccion(self):
        return glm.perspective(glm.radians(FOV), self.aspect_ratio, NEAR, FAR)
        
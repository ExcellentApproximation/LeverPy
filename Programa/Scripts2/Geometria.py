import numpy as np
import glm
import pygame as pg
from . import PropiedadesMasa as pm

## Funcion que borra los elementos duplicados de una lista de listas, teniendo en cuenta que [1,0] = [0,1]
def borrarDuplicados(lista):
    k = [sorted(i) for i in lista]
    listaOrdenada = sorted(k)
    listaFinal = [np.array(listaOrdenada[i]) for i in range(len(listaOrdenada)) if listaOrdenada[i] != listaOrdenada[i-1] or i == 0]
    return listaFinal

## Definimos la una funcion que usa una matriz de rotacion para rotar una lista de vectores theta grados entorno al vector e.
def Rotacion(v,e,theta):
    cos = 1-np.cos(theta)
    sen = np.sin(theta)
    
    ## Definimos la matriz de rotacion generalizada
    
    R = np.zeros((3,3))
    R[0,0] = np.cos(theta) + (e[0]**2)*cos
    R[0,1] = e[0]*e[1]*cos - e[2]*sen
    R[0,2] = e[0]*e[2]*cos + e[1]*sen
    
    R[1,0] = e[1]*e[0]*cos + e[2]*sen
    R[1,1] = np.cos(theta) + (e[1]**2)*cos
    R[1,2] = e[1]*e[2]*cos - e[0]*sen
    
    R[2,0] = e[2]*e[0]*cos - e[1]*sen
    R[2,1] = e[2]*e[1]*cos + e[0]*sen
    R[2,2] = np.cos(theta) + (e[2]**2)*cos
    
    ## Multiplicamos el array de vectores enteros por la matriz. Multiplicamos los vectores por la izquierda, y si te fijas para que tenga que sentido hay que transponer la matriz de rotaciÃ³n:
    
    vRot = np.dot(v,np.transpose(R))
    
    return vRot, R

def Rodriges(v,e,theta): ## La he dejado definida, pero al darme cuenta que con la matriz de rotaciÃ³n generalizada puedo computar todos los vÃ©rtices simultÃ¡neamente, la fÃ³rmula de Rodriges ya no me sirve
    return np.cos(theta)*v + np.sin(theta)*np.cross(e,v) + (1-np.cos(theta))*np.dot(e,v)*e 

class poliedro():
    
    def actualizarVertices(self,traslacion,u,theta):

        if np.linalg.norm(u) != 0:
            eje = u /np.linalg.norm(u)
            verticesCM = self.vertices-self.pos ## verticesCM son las posiciones de los vertices respecto del centro de masas
            rot = Rotacion(verticesCM,eje,theta) ## Aplicamos la matriz de rotacion
            verticesCM = rot[0]
            self.estadoRotacion = np.matmul(rot[1],self.estadoRotacion)
            self.vertices = verticesCM + self.pos ## Volvemos a pasar los vertices al sistema de referencia global
        self.vertices += traslacion ## Por ultimo, sumamos la traslacion, que es exactamente igual para todos los vertices y es independiente de la rotacion.
    
    def actualizarCM(self,traslacion):
        self.pos += traslacion
    
    def __init__(self, vertices, caras, m, escala, pos, e, theta, v, w, estatico, app, color, textura, Ntextura):
        
        self.color = color
        self.estatico = estatico
        
        ## Aplicamos la escalada del objeto ----------------------------------
        verticesEscalados = vertices
        verticesEscalados[:,0] *= escala[0]
        verticesEscalados[:,1] *= escala[1]
        verticesEscalados[:,2] *= escala[2]
        
        self.vertices = verticesEscalados + np.array([0,0,0])
        ## -------------------------------------------------------------------
        
        self.caras = caras
        
        """
        Inicialmente, los vértices aparecen en la posición especificada por el .obj. Lo que vamos a hacer va a ser inicializar el objeto en el centro
        y ya luego aplicaremos la traslación y rotación introducida en el constructor de clase. Para eso, seguimos estos pasos:
        
            1. Realizar la integración volumétrica del objeto, lo que nos proporcionará los valores de posición del centro de masas y el tensor de inercia.
            2. Trasladar el centro de masas al origen global, aplicando a los vértices exactamente la misma traslación.
            3. Finalmente, aplicamos la traslación y rotación deseada al CM y a los vértices.
        
        """
        
        self.m = m
        posCM, I, Volumen, Densidad = pm.IntegracionVolumetrica(self)
        self.I = I
        self.Volumen = Volumen
        self.Densidad = Densidad
    
        

        ## El desplazamiento que hay que aplicar al CM es precisamente -posCM. Aplicamos dicha traslación a los vértices:
            
        self.actualizarVertices(-posCM,0,0)
        
        ## Y ahora sencillamente decimos que la posición del centro de masas está en el origen:
            
        self.pos = np.zeros(3)
        
        ## Por último, aplicaremos la posición y rotación proporcionada por el constructor de clase:
            
        self.estadoRotacion = np.eye(3) ## Inicialmente, el objeto no presenta rotación, por lo que su matriz de rotación inicial es una identidad        
        self.actualizarVertices(pos,e,theta)
        self.actualizarCM(pos)
        
        ## Obtenemos la lista de aristas a partir de las caras, borrando los elementos duplicados en el proceso
        aristas = []
        for cara in self.caras:
            aristas.append([cara[-1],cara[0]])
            for i in range(len(cara)-1):
                aristas.append([cara[i],cara[i+1]])
        aristas = borrarDuplicados(aristas)
        self.aristas = np.array(aristas)
        
        self.v = v
        self.w = w
        
        ## Para mejorar el rendimiento, creamos cajas con ejes paralelos a los ejes cartesianos x, y, z, que servirán para hacer comprobaciones a priori y descartar pares colisionantes de objetos.
        self.boundingBox = np.zeros((3,2))
        self.actualizarBoundingBox()
        """
        Vvertices = []
        for i in self.vertices:
            Vvertices.append(np.linalg.norm(i-self.pos))
        self.boundingSphere = max(Vvertices)
            """
        
        ## Comprobamos qué aristas del objeto son paralelas. Servirá para optimizar enormemente la detección de colisiones SAT:
        
        iaristas = np.arange(len(self.aristas)).tolist()
        self.iaristasLI = []
        self.iaristasLIaux = []
        
        i = 0
        j = 0

        while i < len(iaristas):
            self.iaristasLI.append([i])
            self.iaristasLIaux.append(i)
            j = i+1
            while j < len(iaristas):
                vecArista1 = self.getArista(iaristas[i])[1] - self.getArista(iaristas[i])[0]
                vecArista2 = self.getArista(iaristas[j])[1] - self.getArista(iaristas[j])[0]
                if np.linalg.norm(np.cross(vecArista1,vecArista2)) <= 1e-2:
                    self.iaristasLI[i].append(iaristas[j])
                    iaristas.pop(j)
                else:
                    j += 1
            i += 1
        
        self.iaristasLIaux = np.array(self.iaristasLIaux)
        
        self.colisionando = False
        
        ## CÓDIGO PARA IMPLEMENTACIÓN DEL OBJETO EN OPENGL --------------------------------------------------------------------------------------------------------------------------
        
        ## Triangulamos las caras porque OpenGl lo requiere
        
        self.renderIndices = []
        self.textIndices = []
        self.text_coord = [[0,0],[Ntextura,0],[Ntextura,Ntextura],[0,Ntextura]]
        
        for i in self.caras:
            if len(i) <= 3:
                self.renderIndices.append(i)
                self.textIndices.append((0,2,3))
            elif len(i) == 4:
                self.renderIndices.append(i[0:3])
                self.textIndices.append((0,1,2))
                self.renderIndices.append(i.tolist()[2:4]+i.tolist()[0:1])
                self.textIndices.append((2,3,0))
            else:
                for j in range(len(i)):
                    caraTemp = i.tolist()
                    caraTemp = caraTemp+caraTemp
                    self.renderIndices.append(caraTemp[j:j+3])
                    self.textIndices.append((0,2,3))
                    
        self.renderIndices = np.array(self.renderIndices)
        self.textIndices = np.array(self.textIndices)
        
        self.normales = []
        
        for i in range(len(self.renderIndices)):
            cara = self.getCaraTrianguladas(i)
            normaltemp = NormalPlano(cara[0],cara[1],cara[2])
            for j in cara:
                self.normales.append(normaltemp)
        self.normales = np.array(self.normales,dtype="f4")
        
        self.app = app
        self.ctx = app.ctx
        self.vbo = self.get_vbo()
        self.shader_program = self.get_shader_program("default")
        self.vao = self.get_vao()
        self.program = self.vao.program
        

        
        self.RutaTextura = textura
        
        self.on_init()
        
    def actualizarBoundingBox(self):
        proyX = np.dot(self.vertices,np.array([1,0,0]))
        proyY = np.dot(self.vertices,np.array([0,1,0]))
        proyZ = np.dot(self.vertices,np.array([0,0,1]))
        
        self.boundingBox[0] = np.array([min(proyX),max(proyX)])
        self.boundingBox[1] = np.array([min(proyY),max(proyY)])
        self.boundingBox[2] = np.array([min(proyZ),max(proyZ)])
        
    def addImpulso(self,r,j):
        Rinv = np.linalg.inv(self.estadoRotacion) ## obtenemos la matriz de rotación que devuelve a cada objeto a su estado sin rotar (estado rotacional donde hemos calculado originalmente el tensor de inercia)
        IGlobal = np.matmul(Rinv,np.matmul(self.I,np.transpose(Rinv)))
        invIGlobal = np.linalg.inv(IGlobal)
        
        rRel = r - self.pos
        
        self.v += j/self.m
        self.w += np.dot(invIGlobal,np.cross(rRel,j))
        
    
    def getArista(self,iArista):
        iVertices = self.aristas[iArista]
        arista = np.zeros((2,3))
        arista[0] = self.vertices[iVertices[0]]
        arista[1] = self.vertices[iVertices[1]]
        return arista
    
    def getCara(self,iCara):
        iVertices = self.caras[iCara]
        nVertices = len(iVertices)
        cara = np.zeros((nVertices,3))
        for i in range(nVertices):
            cara[i] = self.vertices[iVertices[i]]
        return cara
    
    def getCaraTrianguladas(self,iCara):
        iVertices = self.renderIndices[iCara]
        nVertices = len(iVertices)
        cara = np.zeros((nVertices,3))
        for i in range(nVertices):
            cara[i] = self.vertices[iVertices[i]]
        return cara
    
    
    ## FUNCIONES NECESARIAS PARA VISUALIZACIÓN EN OPENGL
    
    
    def update(self):
        self.texture.use()
        self.vbo = self.get_vbo()
        self.vao = self.get_vao()
        self.program["m_view"].write(self.app.camara.m_view)
        self.program["camPos"].write(self.app.camara.position)
        
    def get_texture(self,path):
        texture = pg.image.load(path).convert()
        texture = self.ctx.texture(size=texture.get_size(), components = 3, data = pg.image.tostring(texture,"RGB"))
        return texture
    
    def change_texture(self,path):
        self.RutaTextura = path
        self.texture = self.get_texture(path = ("Texturas/" + self.RutaTextura))
        self.program["u_texture_0"] = 0
        
    def on_init(self):

        ## iluminacion
        self.program["light.position"].write(self.app.light.position)
        self.program["light.Ia"].write(self.app.light.Ia)
        self.program["light.Id"].write(self.app.light.Id)
        self.program["light.Is"].write(self.app.light.Is)
        
        ## texturas
        self.texture = self.get_texture(path = ("Texturas/" + self.RutaTextura))
        self.program["u_texture_0"] = 0
        self.texture.use()
        
        self.program["m_proj"].write(self.app.camara.m_proj)
        self.program["m_view"].write(self.app.camara.m_view)
        #self.shader_program["color"].write(self.color)
    
    def get_datosRender(self,vertices,indices):
        datos = [vertices[ind] for triangulo in indices for ind in triangulo]
        return np.array(datos, dtype="f4")
    
    def renderizar(self):
        self.update()
        self.vao.render()
        
    def destruir(self):
        self.vbo.release()
        self.shader_program.release()
        self.vao.release()
    
    def get_vao(self):
        vao = self.ctx.vertex_array(self.shader_program, [(self.vbo, "2f 3f 3f", "in_texcoord_0", "in_normal", "in_position")])
        return vao
    
    def get_vertex_data(self):
        vertex_data = self.get_datosRender(self.vertices,self.renderIndices)
        tex_coord_data = self.get_datosRender(self.text_coord, self.textIndices)
        
        normales = np.matmul(self.normales,np.transpose(self.estadoRotacion))
        normales = np.array(normales,dtype="f4")
        
        vertex_data = np.hstack([normales,vertex_data])
        vertex_data = np.hstack([tex_coord_data,vertex_data])
        return vertex_data
    
    def get_vbo(self):
        vertex_data = self.get_vertex_data()
        vbo = self.ctx.buffer(vertex_data)
        return vbo
    
    def get_shader_program(self,nombre_shader):
        with open(f"Scripts2/shaders/{nombre_shader}.vert") as file:
            vertex_shader = file.read()
        with open(f"Scripts2/shaders/{nombre_shader}.frag") as file:
            fragment_shader = file.read()
            
        program = self.ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)
        return program

def importarOBJ(archivo): ## Importamos un poliedro en formato .obj
    objeto = open(archivo,"r")
    vertices = []
    caras = []
    for x in objeto:
        if x[:2] == "v ": ## Las líneas que empiezan por "v " son las que contienen la coordenada de un vértice
            vertices.append(np.array([float(i) for i in x[2:].split()])) #Separamos el resto de la línea en trozos, y cada trozo es una de las tres coordenadas del vértice
        if x[:2] == "f ": ## Las líneas que empiezan por "f " son las que contienen los vértices que constituyen una cara
            caras.append(np.array([int(i) for i in [j.split("/")[0] for j in x[2:].split()]]))#Separamos el resto de la línea en trozos. Cada trozo contiene la referencia a un vértice y otros datos como el vector normal. Lo único que nos interesa es la referencia al vértice porque la normal la calcularemos nosotros, así que dividimos los trozos en más trozos usando "/" como separador y nos quedamos con el primer elemento de la separación, que es la referencia a los vértices.
            
    vertices = np.array(vertices)
    caras = np.array(caras)-1 ## Restamos 1 para que los índices empiecen en el 0.

    ### Rotamos 90º respecto del eje x porque al pasar de blender a python rotan los objetos -90º
    
    rotacion = np.zeros((3,3))
    rotacion[1,2] = -1
    rotacion[0,0] = rotacion[2,1] = 1
    
    vertices = np.matmul(vertices,np.transpose(rotacion)) ## Transpongo la rotacion porque la matriz sin transponer estÃ¡ pensada para ser multiplicada por un vector. Si los piensas al transponerla sirve para multiplicarle por la izquierda una matriz donde cada fila representa un vector, para tener asÃ­ como resultado otra matriz donde cada fila representa cada vector rotado
    
    return vertices, caras


class skyBox():
    def __init__(self,app,textura):
        self.app = app
        self.ctx = app.ctx
        self.vbo = self.get_vbo()
        self.shader_program = self.get_shader_program("skybox")
        self.vao = self.get_vao()
        self.program = self.vao.program
        self.textura = textura
        
        self.on_init()
        
    def get_datosRender(self,vertices,indices):
        data = [vertices[ind] for triangle in indices for ind in triangle]
        return np.array(data, dtype="f4")
    
    def get_vertex_data(self):
        vertices = [(-1, -1, 1), ( 1, -1,  1), (1,  1,  1), (-1, 1,  1),
                    (-1, 1, -1), (-1, -1, -1), (1, -1, -1), ( 1, 1, -1)]

        indices = [(0, 2, 3), (0, 1, 2),
                   (1, 7, 2), (1, 6, 7),
                   (6, 5, 4), (4, 7, 6),
                   (3, 4, 5), (3, 5, 0),
                   (3, 7, 4), (3, 2, 7),
                   (0, 6, 1), (0, 5, 6)]
        vertex_data = self.get_datosRender(vertices, indices)
        vertex_data = np.flip(vertex_data,1).copy(order="C")
        return vertex_data
    
    def get_texture(self, path, ext='png'):
        faces = ['right', 'left', 'top', 'bottom'] + ['front', 'back'][::-1]
        # textures = [pg.image.load(dir_path + f'{face}.{ext}').convert() for face in faces]
        textures = []
        for face in faces:
            texture = pg.image.load(path + f'{face}.{ext}').convert()
            if face in ['right', 'left', 'front', 'back']:
                texture = pg.transform.flip(texture, flip_x=True, flip_y=False)
            else:
                texture = pg.transform.flip(texture, flip_x=False, flip_y=True)
            textures.append(texture)

        size = textures[0].get_size()
        texture_cube = self.ctx.texture_cube(size=size, components=3, data=None)

        for i in range(6):
            texture_data = pg.image.tostring(textures[i], 'RGB')
            texture_cube.write(face=i, data=texture_data)

        return texture_cube
    
    def update(self):
        self.texture.use()
        self.vbo = self.get_vbo()
        self.vao = self.get_vao()
        self.program["m_view"].write(glm.mat4(glm.mat3(self.app.camara.m_view)))
        
    def on_init(self):

        ## texturas
        self.texture = self.get_texture(path = ("Texturas\\" + self.textura))
        self.program["u_texture_skybox"] = 0
        self.texture.use()
        
        self.program["m_proj"].write(self.app.camara.m_proj)
        self.program["m_view"].write(glm.mat4(glm.mat3(self.app.camara.m_view)))
        #self.shader_program["color"].write(self.color)
    
    def renderizar(self):
        self.update()
        self.vao.render()
        
    def destruir(self):
        self.vbo.release()
        self.shader_program.release()
        self.vao.release()
    
    def get_vao(self):
        vao = self.ctx.vertex_array(self.shader_program, [(self.vbo, "3f", "in_position")])
        return vao
    
    def get_vbo(self):
        vertex_data = self.get_vertex_data()
        vbo = self.ctx.buffer(vertex_data)
        return vbo
    
    def get_shader_program(self,nombre_shader):
        with open(f"Scripts2/shaders/{nombre_shader}.vert") as file:
            vertex_shader = file.read()
        with open(f"Scripts2/shaders/{nombre_shader}.frag") as file:
            fragment_shader = file.read()
            
        program = self.ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)
        return program












## IMPORTANTE: Esta funciÃ³n solo da la orientaciÃ³n correcta para caras convexas. Si la cara es cÃ³ncava, la orientaciÃ³n podrÃ­a salir al revÃ©s.
def NormalPlano(p1, p2, p3):
    v1 = p2-p1
    v2 = p3-p1
    
    vectorN = np.cross(v1, v2)
    vectorN = vectorN/np.linalg.norm(vectorN)
    
    return vectorN

def NormalAristas(ar1,ar2):
    vectorN = np.cross(ar1,ar2)
    mod = np.linalg.norm(vectorN)
    
    if mod != 0:
        return vectorN/mod
    else: ## Si el módulo de vectorN es 0 significa que las aristas son paralelas. En este caso devolvemos un array de ceros para evitar división entre cero
        return np.zeros(3)
    
def ecRecta(recta):
    p1,p2 = recta
    v = p2-p1
    return v,p1

def ecPlano(plano):
    p1,p2,p3 = plano[:3]
    n = NormalPlano(p1,p2,p3)
    D = -np.dot(n,p1)
    return n,D


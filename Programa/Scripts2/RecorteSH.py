import numpy as np
from . import Geometria as geo

"""
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

## CREACIÓN DE LOS PLANOS

planoRef = np.zeros((3,3))
planoIn = np.zeros((3,3))

planoRef[0] = np.array([1,0,0])
planoRef[1] = np.array([-0.5,2,-0.4])
planoRef[2] = np.array([-0.5,-1,0])

planoIn[0] = np.array([5,0,0.3])
planoIn[1] = np.array([-0.5,1,0.5])
planoIn[2] = np.array([-0.3,-0.5,-0.5])
"""
## OBTENCIÓN DE LAS ARISTAS Y RECTAS INCIDENTES Y DE LOS PLANOS REFERENTES


## Aristas y ecuaciones de recta incidentes

def obtenerAristasyRectas(plano):
    nrectas = len(plano)
    aristasIn = []
    rectasIn = []
    for i in range(nrectas-1):
        aristasIn.append([plano[i],plano[i+1]])
        rectasIn.append(geo.ecRecta(aristasIn[i]))
    aristasIn.append([plano[nrectas-1],plano[0]])
    rectasIn.append(geo.ecRecta(aristasIn[-1]))
    return aristasIn,rectasIn


## Planos perpendiculares al de referencai

def obtenerPlanosPerpendiculares(plano):
    NplanoRef = geo.NormalPlano(plano[0],plano[1],plano[2])
    nplanos = len(plano)
    planos = []
    for i in range(nplanos):
        if i < nplanos-1:
            vrecta = plano[i+1]-plano[i]
        else:
            vrecta = plano[0]-plano[i]
        n = np.cross(vrecta,NplanoRef)
        planos.append([n,plano[i]])
    planos.append([NplanoRef,plano[0]])
    return planos



## IMPLEMENTACIÓN DEL ALGORITMO

def corteRectaPlano(recta,plano):
    v,pr = recta
    n,pp = plano
    
    if np.dot(v,n) != 0:
        return np.dot((pp-pr),n)/np.dot(v,n)
    elif np.dot((pp-pr),n) == 0:
        return "coincidentes"
    else:
        return None
    
def puntoEncerrado(punto,planos):
    puntoInterior = True
    for i in range(len(planos)):
        plano = planos[i]
        A,B,C = plano[0]
        D = np.dot(plano[0],plano[1])
        if not (A*punto[0]+B*punto[1]+C*punto[2]-D) <= 1e-8:
            puntoInterior = False
            break
    return puntoInterior
    
    
def RecorteSH(caraReferente,caraIncidente):
    
    aristasIn,rectasIn = obtenerAristasyRectas(caraIncidente)
    aristasRef,rectasRef = obtenerAristasyRectas(caraReferente)
    planosPerpendiculares = obtenerPlanosPerpendiculares(caraReferente)
    nrectas = len(rectasIn)
    nrectas2 = len(rectasRef)
    nplanos = len(planosPerpendiculares)
    
    t = [] ## Aquí almacenamos los parámetros t correspondientes a los puntos de corte pertenecientes a las rectas parametrizadas. (Cortes de rectas incidentes con planos perpendiculares referentes)
    for i in range(nrectas):
        t.append([])
        for j in range(nplanos):
            recta = rectasIn[i]
            plano = planosPerpendiculares[j]
            tj = corteRectaPlano(recta, plano)
            if tj != None and tj != "coincidentes":
                t[i].append(tj)
                
    t2 = [] ## Igual que t pero para los cortes de las rectas referentes con el plano incidente.
    for i in range(nrectas2):
        recta = rectasRef[i]
        planoIn = [geo.NormalPlano(caraIncidente[0],caraIncidente[1],caraIncidente[2]),caraIncidente[0]]
        tj = corteRectaPlano(recta, planoIn)
        if tj != None and tj != "coincidentes":
                t2.append(tj)

    puntosCorteTotales = []
    puntosCorteTotales2 = []

    ## Aplicamos las ecuaciones de recta parametrizadas a los parámetros t y t2 calculados anteriormente. Obtenemos así las coordenadas exactas de cada potencial punto de corte
    for i in range(len(t)):
        puntosCorteTotales.append([])
        for j in range(len(t[i])):
            recta = rectasIn[i]
            puntosCorteTotales[i].append(recta[1]+t[i][j]*recta[0])
    
    for i in range(len(t2)):
        recta = rectasRef[i]
        puntosCorteTotales2.append(recta[1]+t2[i]*recta[0])

    ## Ahora creamos estas nuevas listas donde almacenaremos los puntos de corte finales, es decir, vamos a quitar aquellos puntos de corte que se salgan del volumen referente.
    puntosCorte = []
    puntosCorte2 = []
    
    for i in range(nrectas):
        cortesRecta = puntosCorteTotales[i]
        for j in range(len(cortesRecta)):
            punto = cortesRecta[j]
            if not 0 <= t[i][j] <= 1: ## Comprobamos si el el punto de corte j-ésimo de la recta i-ésima pertenece a la arista i-ésima
                continue
            if puntoEncerrado(punto,planosPerpendiculares): ## En caso de que el punto de corte haya cumplido la condición superior, comprobamos si se encuentra encerrado en el volumen referente.
                puntosCorte.append(punto) ## Si el punto de corte supera ambas pruebas, es añadido a la lista final de puntos de corte
                
    for i in range(len(puntosCorteTotales2)):
        punto = puntosCorteTotales2[i]
        if not 0 <= t2[i] <= 1: ## Hacemos las misma comprobación que antes para los puntosCorteTotales2
            continue
        if puntoEncerrado(punto,obtenerPlanosPerpendiculares(caraIncidente)): ## En este caso, estamos comprobando si el punto de corte de la arista referente está dentro de la cara incidente. Lo hacemos considerando un "volumen incidente", que es lo mismo que el volumen referente (planos perpendiculares) pero para la cara que incide.
            puntosCorte2.append(punto)
    
    verticesInteriores = []
    
    for i in range(len(caraIncidente)):
        if puntoEncerrado(caraIncidente[i],planosPerpendiculares):
            verticesInteriores.append(caraIncidente[i])
    
    ## Combinamos las dos listas de puntos de corte en una sola y la convertimos a array. Devolvemos el array como salida de la función, el cual nos dirá qué porción de cara incidente está encerrada en el volumen referente.
    puntosCorte = puntosCorte + puntosCorte2 + verticesInteriores
    puntosCorte = np.array(puntosCorte)
    return puntosCorte


##----------------------------------------------- ## FUNCIONES PARA LA COMPUTACIÓN DEL CASO ARISTA-ARISTA ## -------------------------------------------------------------------------------------------------------------

def PuntosCercanosRectasQueCruzan(recta1,recta2): # Devuelve los puntos de menor separación entre dos rectas que se cruzan.
    
    v1,p1 = recta1
    v2,p2 = recta2

    # Calculamos las constantes que aparecerán en el sistema de ecuaciones
    a = np.dot(v1,v1)
    b = np.dot(v1,v2)
    c = np.dot(v2,v2)
    d = np.dot(p1-p2,v1)
    f = np.dot(p1-p2,v2)

    # Resolviendo el sistema de ecuaciones analíticamente llegamos a:
    t1 = (b*f-c*d)/(a*c-b**2)
    t2 = (a*f-b*d)/(a*c-b**2)

    return t1,t2

def PuntoCercanoRectaPunto(recta,punto):
    
    v1,p1 = recta
    u = punto-p1
    
    t = np.dot(u,v1)/np.dot(v1,v1)
    d = np.linalg.norm(p1+t*v1-punto)
    return t,d

def SolapamientoSegmentosParalelos(segmento1,segmento2):
    
    v1,p1 = geo.ecRecta(segmento1)
    v2,p2 = geo.ecRecta(segmento2)
    
    tProy = []
    tProy.append()
    ## BAJO CONSTRUCCIÓN
    

def minSepAristas(arista1,arista2): ## Aunque esto no tenga que ver con el algoritmo Sutherland-Hodgeman, sí tiene que ver con la obtención del punto / manifold de colisión, por lo que lo incluyo en esta librería
    recta1 = geo.ecRecta(arista1)
    recta2 = geo.ecRecta(arista2)
    if np.dot(recta1[0],recta2[0]) != 0:
        t1,t2 = PuntosCercanosRectasQueCruzan(recta1, recta2)
        if 0<=t1<=1 and 0<=t2<=1: ## Si los puntos más cercanos entre las dos rectas pertenecen ambos a sus respectivos segmentos, entonces nos quedamos con estos puntos
            return (recta1[0]*t1+recta1[1]),t1,t2
        else:
            dists = []
            ts = []
            for i in range(2):
                t1,d = PuntoCercanoRectaPunto(recta1, arista2[i])
                t2 = i
                if 0<=t1<=1:
                    dists.append(d)
                    ts.append([t1,t2])
                else:
                    dists2 = []
                    ts2 = []
                    for j in range(2):
                        dists2.append(np.linalg.norm(arista1[j]-arista2[i]))
                        ts2.append([j,i])
                    dists.append(min(dists2))
                    ts.append(ts2[dists2.index(min(dists2))])
            for i in range(2):
                t2,d = PuntoCercanoRectaPunto(recta2, arista1[i])
                t1 = i
                if 0<=t2<=1:
                    dists.append(d)
                    ts.append([t1,t2])
                else:
                    dists2 = []
                    ts2 = []
                    for j in range(2):
                        dists2.append(np.linalg.norm(arista2[j]-arista1[i]))
                        ts2.append([i,j])
                    dists.append(min(dists2))
                    ts.append(ts2[dists2.index(min(dists2))])
            t1,t2 = ts[dists.index(min(dists))]
            return (recta1[0]*t1+recta1[1]),t1,t2
            
"""
puntosCorte = RecorteSH(planoRef,planoIn)



## REPRESENTACIÓN 3D

fig = plt.figure()
ax = plt.axes(projection='3d')
lim = 1.5
ax.set_xlim(-lim,lim)
ax.set_ylim(-lim,lim)
ax.set_zlim(-lim*3/4,lim*3/4)

ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_zlabel("z")

ax.add_collection3d(Poly3DCollection(planoRef,edgecolor="black"))
for i in range(len(planoRef)):
    pos = tuple(planoRef[i])
    ax.text(*pos,i)
    
ax.add_collection3d(Poly3DCollection(planoIn,edgecolor="black"))

ax.collections[0].set_facecolor("green")

for i in range(len(planoIn)):
    pos = tuple(planoIn[i])
    ax.text(*pos,i)
    
ax.add_collection3d(Poly3DCollection(puntosCorte,edgecolor="black"))
ax.collections[1].set_facecolor("red")
for i in range(len(puntosCorte)):
    pos = tuple(puntosCorte[i])
    ax.text(*pos,i)

ax.scatter(puntosCorte[:,0],puntosCorte[:,1],puntosCorte[:,2],color="red")
"""
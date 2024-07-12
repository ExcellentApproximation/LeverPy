import numpy as np
import time
import timeit
from . import Geometria as geo


def SATcheck(eje,obj1,obj2):
    V1 = obj1.vertices
    V2 = obj2.vertices
    
    ## eje es el vector director del SA. V1 y V2 son las colecciones de vÃ©rtices de los dos objetos poligonales que estamos comparando.
    proyeccionV1 = np.dot(V1,eje)
    proyeccionV2 = np.dot(V2,eje)
    
    V1max = max(proyeccionV1)
    V1min = min(proyeccionV1)
    
    V2max = max(proyeccionV2)
    V2min = min(proyeccionV2)
    
    
    if V1max >= V2min and V1min <= V2max:
        if V1max >= V2max:
            if V2min >= V1min: ## Objeto 2 dentro de objeto 1
                if V2max-V1min < V1max-V2min: ## Comparamos las dos posibles distancias de penetración y nos quedamos con la menor
                    return True , V2max-V1min
                else:
                    return True , V1max-V2min
                
            else: ## Ningún objeto contenido en el otro
                return True , V2max-V1min
        else:
            if V1min >= V2min: ## Objeto 1 dentro de objeto 2
                if V1max-V2min < V2max-V1min:## Comparamos las dos posibles distancias de penetración y nos quedamos con la menor
                    return True, V1max-V2min
                else:
                    return True, V2max-V1min
    
            else: ## Ningún objeto contenido en el otro
                return True , V1max-V2min 
    else:
        return False , None ## Si la proyecciones de los objetos sobre el eje son disjuntas, devolvemos falso
        

def SATcheckIntervalo(eje,obj1,obj2): ## Este SATcheck hace lo mismo que el anterior pero en vez de devolver verdadero/falso y la longitud de solapamiento, tansolo devuelve el intervalo de solapamiento.
    
    V1 = obj1.vertices
    V2 = obj2.vertices
    
    ## eje es el vector director del SA. V1 y V2 son las colecciones de vÃ©rtices de los dos objetos poligonales que estamos comparando.
    proyeccionV1 = np.dot(V1,eje)
    proyeccionV2 = np.dot(V2,eje)
    
    V1max = max(proyeccionV1)
    V1min = min(proyeccionV1)
    
    V2max = max(proyeccionV2)
    V2min = min(proyeccionV2)
    
    if V1max >= V2min and V1min <= V2max:
        if V1max >= V2max:
            if V2min >= V1min: ## Objeto 2 dentro de objeto 1
                if V2max-V1min < V1max-V2min: ## Comparamos las dos posibles distancias de penetración y nos quedamos con la menor
                    return V1min,V2max
                else:
                    return V2min,V1max
                
            else: ## Ningún objeto contenido en el otro
                return V1min,V2max
        else:
            if V1min >= V2min: ## Objeto 1 dentro de objeto 2
                if V1max-V2min < V2max-V1min:## Comparamos las dos posibles distancias de penetración y nos quedamos con la menor
                    return V2min,V1max
                else:
                    return V1min,V2max
    
            else: ## Ningún objeto contenido en el otro
                return V2min,V1max 


def BuscarColision(obj1,obj2):
    
    colision = True
    
    ## Antes de comprobar si los objetos colisionan, hacemos una rápida comparacion con bounding boxes para descartar gran parte de las postenciales colisiones
    error = 1e-1
    for i in range(3): ## Iteramos en los tres ejes: x, y, z
        ## Comprobamos si algún extremo del objeto 1 está dentro del objeto 2
        if not(obj1.boundingBox[i,0] + error > obj2.boundingBox[i,0] and obj1.boundingBox[i,0] < obj2.boundingBox[i,1] + error
            or obj1.boundingBox[i,1] + error > obj2.boundingBox[i,0] and obj1.boundingBox[i,1] < obj2.boundingBox[i,1] + error
            or obj2.boundingBox[i,0] + error > obj1.boundingBox[i,0] and obj2.boundingBox[i,0] < obj1.boundingBox[i,1] + error
            or obj2.boundingBox[i,1] + error > obj1.boundingBox[i,0] and obj2.boundingBox[i,1] < obj1.boundingBox[i,1] + error):
            
            colision = False
            return colision, None, None
    """
    VCM = np.linalg.norm(obj2.pos-obj1.pos)
    if VCM >= (obj1.boundingSphere + obj2.boundingSphere):
        colision = False
        return colision, None, None
"""
    ## SAT de eje normal a cara ----------------------------------------------------------------------------------------------------------------------------------------------
    
    ejesCarasObj1 = np.zeros(len(obj1.caras)) ## Estos arrays guardarán la distancia de superposición en los ejes correspondientes a las caras.
    ejesCarasObj2 = np.zeros(len(obj2.caras)) ## Harán falta para encontrar la mínima separación.
    
    for i in range(len(obj1.caras)): ## Recorremos primero las caras del primer objeto
        cara = obj1.getCara(i)
        vN = geo.NormalPlano(cara[0],cara[1],cara[2]) ## Obtenemos la normal a la cara i-ésima
        SAT = SATcheck(vN,obj1,obj2) ## Comprobamos si hay solapamiento en el eje dado por vN
        if SAT[0] == False: ## Si no hay solapamiento devolvemos Falso, pues no hay colisión
            colision = False
            return colision, None, None
        else: ## Si sí hay solapamiento, almacenamos la distancia de solapamiento.
            ejesCarasObj1[i] = SAT[1]
        
        
    for i in range(len(obj2.caras)): ## Lo mismo que el bucle superior pero para las caras del segundo objeto
        cara = obj2.getCara(i)
        vN = geo.NormalPlano(cara[0],cara[1],cara[2])
        SAT = SATcheck(vN,obj1,obj2)
        if SAT[0] == False:
            colision = False
            return colision, None, None
        else:
            ejesCarasObj2[i] = SAT[1]
    
    #minSolape = min([min(ejesCarasObj1),min[ejesCarasObj2]])
    
    ## SAT de eje dado por producto vectorial de dos aristas. ----------------------------------------------------------------------------------------------------------------------------------------------
    
        ## (Recorremos todas las aristas de obj1, y para cada una permutamos con todas las aristas de obj2)
    
    ejesAristas = np.zeros((len(obj1.iaristasLI),len(obj2.iaristasLI)))
    
    
    for i in range(len(obj1.iaristasLI)):
        
        arista1 = obj1.getArista(obj1.iaristasLI[i][0])
        ar1 = arista1[1] - arista1[0] ## La arista sera la resta de los dos vertices referenciados por obj1.aristas[i]
        
        
        for j in range(len(obj2.iaristasLI)):
            
            arista2 = obj2.getArista(obj2.iaristasLI[j][0])
            ar2 = arista2[1] - arista2[0] ## Lo mismo pero con obj2
            vN = geo.NormalAristas(ar1,ar2)
            if (vN == np.zeros(3)).all(): 
                ## Si NormalAristas devuelve un vector nulo, significa que las dos aristas son paralelas, por lo que su producto vectorial es nulo. En este caso tenemos que obtener el vector de mi­nima separacion entre las dos rectas que contienen las aristas.
                ## Para calcular el vector de distancia minima primero unimos dos puntos cualesquiera entre las dos aristas. Por simplicidad tomare vertices, ya que ya los tenemos definidos:
                    
                    p1 = arista1[0]
                    p2 = arista2[0]
                    
                    vectorUnion = p2-p1 ## Vector cualquiera que une las dos rectas
                    vN = vectorUnion - np.dot(vectorUnion,ar1)*ar1/(np.linalg.norm(ar1)**2) ## El vector de mi­nima separacion es ortogonal a las rectas, y es vectorUnion menos la proyeccion sobre la direccion de las rectas
                    if np.linalg.norm(vN) == 0:
                        ejesAristas[i,j] = 1e999 ## Si el vector vN es nulo, significa que las aristas son coincidentes. Este es un caso extremadamente improbable que suceda a no ser que lo pongas así a posta. Aun así, para evitar errores asigno a este par de aristas una distancia tan elevada que es imposible que salga como mínimo de solapamiento
                    else:
                        vN = vN/np.linalg.norm(vN)
            
            if np.linalg.norm(vN) != 0: ## Si vN es un vector no nulo (que es lo que pasará el 99.9999% de las veces), entonces comprobamos el solapamiento igual que en el caso de las caras
                SAT = SATcheck(vN,obj1,obj2)
                if SAT[0] == False:
                    colision = False
                    return colision , None, None
                else:
                    ejesAristas[i,j] = SAT[1]

    ### ------------------------------------------------------------------------------------------------------------------------------------------ ###
    ### -----------------------------------### A PARTIR DE AQUÍ BUSCAMOS CUÁL ES LA CARA/ARISTA DE REFERENCIA ### -------------------------------- ###
    ### ------------------------------------------------------------------------------------------------------------------------------------------ ###
    
    
    minListaCaras = np.array([min(ejesCarasObj1),min(ejesCarasObj2)]) ## Array de dos elementos. En el elemento izquierdo tenemos el mínimo solapamiento de tipo cara por parte del objeto 1, y en el elemento derecho tenemos lo mismo pero del objeto 2.
    
    ## Comprobamos si es una colisión de tipo cara o de tipo aristas:
    
    minLista = [min(minListaCaras),np.min(ejesAristas)] ## En esta lista tenemos a la izquierda el mínimo solapamiento de tipo cara y a la derecha el mínimo solapamiento de tipo arista.
    
    carasOaristas = minLista.index(min(minLista)) ## carasOaristas devolverá 0 si el mínimo solapamiento es de tipo cara y 1 si el mínimo solapamiento es de tipo arista. Vemos que como las caras están a la izquierda, estas tendrán prioridad en caso de que ambos mínimos sean exactamente iguales.
    
    if carasOaristas == 0: ## Si es 0, significa que los objetos están colisionando en el eje dado por alguna cara
        objGenerador = np.where(minListaCaras == min(minListaCaras))[0] ## objGenerador será [0] si el el objeto generador de la cara correspondiente al eje de mínimo solape es el primer objeto, [1] si es el segundo y [0,1] si son los dos simultáneamente.
        
        ## Hay dos posibilidades: que solo uno de los objetos esté generando el eje o que los dos objetos lo hagan simultáneamente (sucede si tienen caras paralelas)
        indicesCaras = [np.array([]),np.array([])] ## Aquí almacenaremos los índices de las caras que generan el eje de mínimo solapamiento. En el array izquierdo almacenamos las caras del objeto 1 y en el derecho las del objeto 2. Evidentemente, si solo un objeto es generador, uno de los arrays quedará vacío.
        for i in objGenerador:
            if i == 0:
                indicesCaras[0] = (np.where(np.round(ejesCarasObj1,5) == np.min(np.round(ejesCarasObj1,5))))[0] ## Añadimos los índices donde ejesCarasObj1 es mínimo para saber qué caras nos generan el eje de mínimo solapamiento. Elijo 5 cifras significativas porque a pesar de que matemáticamente las caras sean paralelas y generen exactamente el mismo eje, numéricamente la dirección del eje se puede desviar un poco entre distintas caras paralelas. Poniendo cierto margen de error evito confusiones en el programa.
            else: # i == 1
                indicesCaras[1] = (np.where(np.round(ejesCarasObj2,5) == np.min(np.round(ejesCarasObj2,5))))[0]         
                
        ## Ahora tenemos la lista indicesCaras, que nos dice todas las caras que generan el eje de mínimo solape, y también nos dice a qué objeto pertenecen dichas caras.
        ## Los índices guardados en indicesCaras[0] se corresponden con caras del objeto 1, mientras que los guardados en indicesCaras[1] son las del objeto 2.
        ## Ahora tenemos que comprobar de entre todas las posibles caras cuál es la adecuada para ser usada como cara de referencia en la colisión. El motivo por el que
        ## hay que tener en cuenta todas las posibilidades es porque en caso de que hayan caras paralelas, todas ellas generan exactamente el mismo eje, pero solo una será la que colisiona realmente
        
        ## Primero obtenemos el intervalo exacto de solape en el eje:
        
        if objGenerador[0] == 0: ## Simplemente tomo el primer plano listado, ya que todos generan el mismo eje (NOTA: no es 100% verdad porque por problemas numéricos distintos planos paralelos a veces se pueden torcer un poco y dejar de ser completamente paralelos. Aun así, como son CASI paralelos, cualquiera de los ejes que generan nos sirven perfectamente para las siguientes comprobaciones)
            cara = obj1.getCara(indicesCaras[0][0])
        else:
            cara = obj2.getCara(indicesCaras[1][0])
        
        eje = geo.NormalPlano(cara[0], cara[1], cara[2])
        
        IntervaloSolape = SATcheckIntervalo(eje, obj1, obj2)
        #print("Solape="+str(IntervaloSolape[0])+","+str(IntervaloSolape[1]))
        caraReferencia = None ## Aquí almacenaremos cuál será la cara de referencia
        
        ## Ahora, proyectaremos un vértice de cada cara guardada en indicesCaras. La primera cara cuya proyección de vértice caiga justamente en uno de los extremos del IntervaloSolape será considerada la cara de referencia.
        
        if indicesCaras[0].size > 0:
            for i in indicesCaras[0]:
                ## i es el indice que referencia la cara del obj1, y queremos un vértice cualquiera de esa cara, entonces:
                verticesCara = obj1.getCara(i)
                for verticeCara in verticesCara:
                    proyeccion = np.dot(verticeCara,eje)
                    #print(proyeccion)
                    if (proyeccion == IntervaloSolape[0]) or (proyeccion == IntervaloSolape[1]):
                        caraReferencia = [0,i] ## 0 para decir que es el obj1 y i para decir qué cara en concreto es
                        break
        if indicesCaras[1].size > 0:
            for i in indicesCaras[1]:
                ## i es el indice que referencia la cara del obj2, y queremos un vértice cualquiera de esa cara, entonces:
                verticesCara = obj2.getCara(i)      
                for verticeCara in verticesCara:
                    proyeccion = np.dot(verticeCara,eje)
                    #print(proyeccion)
                    if (proyeccion == IntervaloSolape[0]) or (proyeccion == IntervaloSolape[1]):
                        caraReferencia = [1,i] ## 1 para decir que es el obj2 y i para decir qué cara en concreto es
                        break
        
        if caraReferencia[0] == 0:
            dot = []
            caraReferente = obj1.getCara(caraReferencia[1])
            NormalReferente = geo.NormalPlano(caraReferente[0],caraReferente[1],caraReferente[2]) ## Obtenemos el vector normal a la cara referente
            for i in range(len(obj2.caras)):
                caraIncidente = obj2.getCara(i)
                NormalIncidente = geo.NormalPlano(caraIncidente[0],caraIncidente[1],caraIncidente[2]) 
                dot.append(np.dot(NormalReferente,NormalIncidente)) ## Para cada cara del objeto incidente, almacenamos el producto escalar de su normal por la normal de la cara referente
            caraIncidencia = [1,dot.index(min(dot))] ## El mínimo producto escalar, es decir, el producto que corresponde con la normal más antiparalela a la normal referente será el correspondiente con la cara incidente
        else:
            dot = []
            caraReferente = obj2.getCara(caraReferencia[1])
            NormalReferente = geo.NormalPlano(caraReferente[0],caraReferente[1],caraReferente[2]) ## Obtenemos el vector normal a la cara referente
            for i in range(len(obj1.caras)):
                caraIncidente = obj1.getCara(i)
                NormalIncidente = geo.NormalPlano(caraIncidente[0],caraIncidente[1],caraIncidente[2]) 
                dot.append(np.dot(NormalReferente,NormalIncidente)) ## Para cada cara del objeto incidente, almacenamos el producto escalar de su normal por la normal de la cara referente
            caraIncidencia = [0,dot.index(min(dot))] ## El mínimo producto escalar, es decir, el producto que corresponde con la normal más antiparalela a la normal referente será el correspondiente con la cara incidente
             
        return colision, "cara", caraReferencia, caraIncidencia, NormalReferente
                
    if carasOaristas == 1: ## si es 1 significa que la colisión es de tipo arista-arista
        indicesAristas = np.where(np.round(ejesAristas,5) == np.min(np.round(ejesAristas,5))) ## indicesAristas nos dice las posiciones en la matriz ejesAristas donde aparecen los mínimos valores de solapamiento
        
        ## Ahora el eje vendrá dado por el producto vectorial de un par de aristas. Obtenemos el eje a partir de cualquier par de aristas listados en indicesAristas: (Por problemas numéricos, los distintos ejes paralelos estarán un poco torcidos entre ellos, y por eso tuvimos antes que incluir un margen de error. Una vez conocemos el grupo de ejes casi paralelos entre ellos, ya no nos importa cual tomar, pues son casi idénticos y para las comprobaciones que vamos a hacer a continuación todos sirven por igual)
        arista1 = obj1.getArista(indicesAristas[0][0])
        arista2 = obj2.getArista(indicesAristas[1][0])
        ar1 = arista1[1] - arista1[0]
        ar2 = arista2[1] - arista2[0]
        
        eje = geo.NormalAristas(ar1,ar2)
        
        if (eje == np.zeros(3)).all(): 
                ## Si NormalAristas devuelve un vector nulo, significa que las dos aristas son paralelas, por lo que su producto vectorial es nulo. En este caso tenemos que obtener el vector de mÃ­nima separaciÃ³n entre las dos rectas que contienen las aristas.
                ## Para calcular el vector de distancia mÃ­nima primero unimos dos puntos cualesquiera entre las dos aristas. Por simplicidad tomarÃ© vÃ©rtices, ya que ya los tenemos definidos:
                    
            p1 = arista1[0]
            p2 = arista2[0]
            
            vectorUnion = p2-p1 ## Vector cualquiera que une las dos rectas
            eje = vectorUnion - np.dot(vectorUnion,ar1)*ar1/(np.linalg.norm(ar1)**2) ## El vector de mÃ­nima separaciÃ³n es ortogonal a las rectas, y es vectorUnion menos la proyecciÃ³n sobre la direcciÃ³n de las rectas
            eje = eje/np.linalg.norm(eje)
        
        ## Ahora ya tenemos el eje. Nos toca comprobar igual que en el caso de las caras cuál es el par de aristas que coincide con el intervalo de solapamiento.
        
        IntervaloSolape = SATcheckIntervalo(eje, obj1, obj2)
        
        #print("Solape = " + str(IntervaloSolape[0]) + "," + str(IntervaloSolape[1]))
        #print(indicesAristas)
        
        AristasChocantes = None
        
        
        for i in range(len(indicesAristas[0])):
            
            
            index1 = np.where(obj1.iaristasLIaux == indicesAristas[0][i])[0][0]
            for j in range(len(obj1.iaristasLI[index1])):
                index2 = np.where(obj2.iaristasLIaux == indicesAristas[1][i])[0][0]
                arista1 = obj1.getArista(obj1.iaristasLI[index1][j])
                proyeccion1 = [np.dot(arista1[0],eje),np.dot(arista1[1],eje)]
                
                for k in range(len(obj2.iaristasLI[index2])):    
                                
                    arista2 = obj2.getArista(obj2.iaristasLI[index2][k])
                    proyeccion2 = [np.dot(arista2[0],eje),np.dot(arista2[1],eje)]
            
                    #print("proyeccion = " + str(proyeccion1[0]) + "," + str(proyeccion1[1])+","+str(proyeccion2[0])+","+str(proyeccion2[1]))
                    
                    ## Debido a que los elementos paralelos no son completamente paralelos por problemas numéricos, no nos sirve con proyetar un solo vértice de arista, tenemos que proyectar ambos y ver si almenos uno de los dos coincide:
                    IntervaloSolape[0]+1e-5
                    if ((min(proyeccion1) <= (IntervaloSolape[0]+1e-5) and (min(proyeccion1) >= (IntervaloSolape[0]-1e-5))) and (max(proyeccion2) <= (IntervaloSolape[1]+1e-5) and max(proyeccion2) >= (IntervaloSolape[1]-1e-5))):
                        AristasChocantes = [obj1.iaristasLI[index1][j],obj2.iaristasLI[index2][k]]
                        ref = 1
                        inc = 0
                        break
                    elif ((max(proyeccion1) <= (IntervaloSolape[1]+1e-5) and (max(proyeccion1) >= (IntervaloSolape[1]-1e-5))) and (min(proyeccion2) <= (IntervaloSolape[0]+1e-5) and min(proyeccion2) >= (IntervaloSolape[0]-1e-5))):
                        AristasChocantes = [obj1.iaristasLI[index1][j],obj2.iaristasLI[index2][k]]
                        ref = 0
                        inc = 1
                        break
                
            
    return colision, "arista-arista", AristasChocantes, ref, inc, eje
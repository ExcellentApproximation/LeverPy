import numpy as np
import random
from . import Geometria as geo

def Sumatorio(f,N):
    suma = 0
    for i in range(N):
        suma+=f(i)
    return suma


def IntegracionVolumetrica(objeto):
    Ncaras = len(objeto.caras)
    integrales = np.zeros((Ncaras,12))
    vNcaras = np.zeros((Ncaras,3))
    
    for j in range(Ncaras):
        cara = objeto.getCara(j)
        plano = geo.ecPlano(cara)
        vNcaras[j] = plano[0]
        posGamma = np.where(abs(plano[0]) == max(abs(plano[0])))[0][0] + 1 ## En el máximo tenemos que colocar el gamma de las nuevas coordenadas.
        ## Ahora tenemos que reordenar las coordenadas de todos los vértices de la cara. Lo haremos con un np.roll()
        ## Si posGamma = 3, cara se queda igual. Si es 2, rolleamos 1 y si es 1 rolleamos 2
        roll = 3-posGamma
        cara = np.roll(cara,roll,axis=1) ## A partir de aquí ya estamos en coordenadas alfa,beta,gamma. Para deshacer el cambio más adelante simplemente
        ## hay que hacer que el programa recuerde la equivalencia xyz - alfabetagamma
        A,B,C = np.roll(plano[0],roll) ## Aplicamos el mismo roll a los coeficientes del plano.
        
        D = plano[1]
    
        a = np.zeros(len(cara)+1)
        b = np.zeros(len(cara)+1)
        
        a[:-1] = cara[:,0] ; b[:-1] = cara[:,1] ##alfa y beta. Los llamo a y b para que el código sea más limpio
        a[-1] = cara[0,0] ; b[-1] = cara[0,1] ## Añadimos al final de los arrays el elemento cero repetido. Así podremos hacer sumatorios cíclicos. Básicamente en las ecuaciones nos aparece el índice "e+1". Una vez e = len(cara)-1, e+1 tiene que ser igual al primer elemento (e = 0).
        
        ## CÁLCULO DE LAS INTEGRALES PI (Integrales de proyección de la cara) COMO LA SUMA DE INTEGRALES DE LINEA A TRAVÉS DEL TEOREMA DE GREEN
        
        sgnC = C/abs(C)
        
        pi_1 = (sgnC/2) * Sumatorio(lambda i : (b[i+1]-b[i]) * (a[i+1] + a[i]) , len(cara))
        
        pi_alfa = (sgnC/6) * Sumatorio(lambda i : (b[i+1]-b[i]) * (a[i+1]**2 + a[i+1]*a[i] + a[i]**2) , len(cara))
        
        pi_beta = -(sgnC/6) * Sumatorio(lambda i : (a[i+1]-a[i]) * (b[i+1]**2 + b[i+1]*b[i] + b[i]**2) , len(cara))
        
        pi_alfa2 = (sgnC/12) * Sumatorio(lambda i : (b[i+1]-b[i]) * (a[i+1]**3 + a[i+1]**2*a[i] + a[i+1]*a[i]**2 + a[i]**3) , len(cara))
        
        pi_alfabeta = (sgnC/24) * Sumatorio(lambda i : (b[i+1]-b[i]) * (b[i+1]*(3*a[i+1]**2 + 2*a[i+1]*a[i] + a[i]**2) + 
                                                                            b[i]*(a[i+1]**2 + 2*a[i]*a[i+1] + 3*a[i]**2)) , len(cara))        
        pi_beta2 = -(sgnC/12) * Sumatorio(lambda i : (a[i+1]-a[i]) * (b[i+1]**3 + b[i+1]**2*b[i] + b[i+1]*b[i]**2 + b[i]**3) , len(cara))
        
        pi_alfa3 = (sgnC/20) * Sumatorio(lambda i : (b[i+1]-b[i]) * (a[i+1]**4 + a[i+1]**3*a[i] + a[i+1]**2*a[i]**2 + a[i+1]*a[i]**3 + a[i]**4) , len(cara))
        
        pi_alfa2beta = (sgnC/60) * Sumatorio(lambda i : (b[i+1]-b[i]) * (b[i+1]*(4*a[i+1]**3 + 3*a[i+1]**2*a[i] + 2*a[i+1]*a[i]**2 + a[i]**3) +
                                                                             b[i]*(a[i+1]**3 + 2*a[i+1]**2*a[i] + 3*a[i+1]*a[i]**2 + 4*a[i]**3)) , len(cara))      
        pi_alfabeta2 = -(sgnC/60) * Sumatorio(lambda i : (a[i+1]-a[i]) * (a[i+1]*(4*b[i+1]**3 + 3*b[i+1]**2*b[i] + 2*b[i+1]*b[i]**2 + b[i]**3) +
                                                                             a[i]*(b[i+1]**3 + 2*b[i+1]**2*b[i] + 3*b[i+1]*b[i]**2 + 4*b[i]**3)), len(cara))    
        pi_beta3 = -(sgnC/20) * Sumatorio(lambda i : (a[i+1]-a[i]) * (b[i+1]**4 + b[i+1]**3*b[i] + b[i+1]**2*b[i]**2 + b[i+1]*b[i]**3 + b[i]**4) , len(cara))
        
        
        ## CÁLCULO DE LAS INTEGRALES DE CARA A PARTIR DE LAS INTEGRALES PI
        
        Cinv = 1/abs(C)
        
        integrales[j,0] = I_alfa = Cinv*pi_alfa 
        
        integrales[j,1] = I_beta = Cinv*pi_beta 
        
        integrales[j,2] = I_gamma = -Cinv*(1/C) * (A*pi_alfa + B*pi_beta + D*pi_1) 
        
        integrales[j,3] = I_alfa2 = Cinv*pi_alfa2 
        
        integrales[j,4] = I_beta2 = Cinv*pi_beta2
        
        integrales[j,5] = I_gamma2 = Cinv*(1/(C**2)) * (A**2*pi_alfa2 + 2*A*B*pi_alfabeta + B**2*pi_beta2 + 2*A*D*pi_alfa + 2*B*D*pi_beta + D**2*pi_1) 
        
        integrales[j,6] = I_alfa3 = Cinv*pi_alfa3 
        
        integrales[j,7] = I_beta3 = Cinv*pi_beta3 
        
        integrales[j,8] = I_gamma3 = -Cinv*(1/(C**3)) * (A**3*pi_alfa3 + 3*A**2*B*pi_alfa2beta + 3*A*B**2*pi_alfabeta2 + B**3*pi_beta3 + 3*A**2*D*pi_alfa2 +
                                       6*A*B*D*pi_alfabeta + 3*B**2*D*pi_beta2 + 3*A*D**2*pi_alfa + 3*B*D**2*pi_beta + D**3*pi_1)
        integrales[j,9] = I_alfa2beta = Cinv*pi_alfa2beta
        
        integrales[j,10] = I_beta2gamma = -Cinv*(1/C) * (A*pi_alfabeta2 + B*pi_beta3 + D*pi_beta2) 
        
        integrales[j,11] = I_gamma2alfa = Cinv*(1/(C**2)) * (A**2*pi_alfa3 + 2*A*B*pi_alfa2beta + B**2*pi_alfabeta2 + 2*A*D*pi_alfa2 + 2*B*D*pi_alfabeta + D**2*pi_alfa)
    
        
        ## Por último, tenemos que pasar estas integrales de nuevo al sistema xyz. Es simplemente cuestión de renombrarlas. Esto solo hace falta en caso de
        ## que roll sea igual a 1 o a 2. Si es 0 las dejamos así.
        
        if roll == 1: ## En este caso, alfa = z, beta = x, gamma = y
            integrales[j,0]  = I_beta  
            integrales[j,1]  = I_gamma 
            integrales[j,2]  = I_alfa
            integrales[j,3]  = I_beta2 
            integrales[j,4]  = I_gamma2
            integrales[j,5]  = I_alfa2 
            integrales[j,6]  = I_beta3
            integrales[j,7]  = I_gamma3
            integrales[j,8]  = I_alfa3  
            integrales[j,9]  = I_beta2gamma
            integrales[j,10] = I_gamma2alfa
            integrales[j,11] = I_alfa2beta
            
        elif roll == 2: ## En este caso, alfa = y, beta = z, gamma = x
            integrales[j,0]  = I_gamma       ## I_x
            integrales[j,1]  = I_alfa        ## I_y
            integrales[j,2]  = I_beta        ## I_z
            integrales[j,3]  = I_gamma2      ## I_x2
            integrales[j,4]  = I_alfa2       ## I_y2
            integrales[j,5]  = I_beta2       ## I_z2
            integrales[j,6]  = I_gamma3      ## I_x3
            integrales[j,7]  = I_alfa3       ## I_y3
            integrales[j,8]  = I_beta3       ## I_z3
            integrales[j,9]  = I_gamma2alfa  ## I_x2y
            integrales[j,10] = I_alfa2beta   ## I_y2z
            integrales[j,11] = I_beta2gamma  ## I_z2x
    
    
    ## CÁLCULO DE LAS INTEGRALES DE VOLUMEN COMO SUMA DE INTEGRALES DE CARA (TEOREMA DE LA DIVERGENCIA)
    
    nx = vNcaras[:,0] ; ny = vNcaras[:,1] ; nz = vNcaras[:,2]
    
    T_1  = Sumatorio(lambda i : integrales[i, 0]*nx[i],Ncaras)
    T_x  = Sumatorio(lambda i : integrales[i, 3]*nx[i],Ncaras)*(1/2)
    T_y  = Sumatorio(lambda i : integrales[i, 4]*ny[i],Ncaras)*(1/2)
    T_z  = Sumatorio(lambda i : integrales[i, 5]*nz[i],Ncaras)*(1/2)
    T_x2 = Sumatorio(lambda i : integrales[i, 6]*nx[i],Ncaras)*(1/3)
    T_y2 = Sumatorio(lambda i : integrales[i, 7]*ny[i],Ncaras)*(1/3)
    T_z2 = Sumatorio(lambda i : integrales[i, 8]*nz[i],Ncaras)*(1/3)
    T_xy = Sumatorio(lambda i : integrales[i, 9]*nx[i],Ncaras)*(1/2)
    T_yz = Sumatorio(lambda i : integrales[i,10]*ny[i],Ncaras)*(1/2)
    T_zx = Sumatorio(lambda i : integrales[i,11]*nz[i],Ncaras)*(1/2)
    
    ## El volumen total ocupado por el objeto viene dado por la integral de la función unidad en el dominio del volumen, es decir, el volumen es precisamente T_1
    ## Luego, la masa total del objeto será la densidad (que es considerada uniforme) multiplicada por T_1. Como yo quiero que el usuario introduzca la masa y
    ## no la densidad, lo voy a hacer al revés. Voy a obtener la densidad como m/T_1:
    
    m = objeto.m
        
    Volumen = T_1
    Densidad = m/Volumen
    PosicionCM = (1/m)*Densidad*np.array([T_x,T_y,T_z])
    
    ## Componentes tensor de inercia en la referencia global (Importante computar antes de rotar el objeto)
    Ip_xx = (T_y2 + T_z2) * Densidad
    Ip_yy = (T_z2 + T_x2) * Densidad
    Ip_zz = (T_x2 + T_y2) * Densidad
    
    Ip_xy = T_xy * Densidad
    Ip_yz = T_yz * Densidad
    Ip_zx = T_zx * Densidad
    
    ## Por último, pasamos el tensor de inercia a la referencia local centrada en el centro de masas:
        
    I_xx = Ip_xx - m * (PosicionCM[1]**2 + PosicionCM[2]**2)
    I_yy = Ip_yy - m * (PosicionCM[2]**2 + PosicionCM[0]**2)
    I_zz = Ip_zz - m * (PosicionCM[0]**2 + PosicionCM[1]**2)
    
    I_xy = Ip_xy - m * PosicionCM[0] * PosicionCM[1]
    I_yz = Ip_yz - m * PosicionCM[1] * PosicionCM[2]
    I_zx = Ip_zx - m * PosicionCM[2] * PosicionCM[0]
    
    ## Definimos y rellenamos el Tensor de Inercia
    
    I = np.zeros((3,3))
    
    I[0,0] = I_xx
    I[1,1] = I_yy
    I[2,2] = I_zz
    
    I[0,1] = I[1,0] = I_xy
    I[0,2] = I[2,0] = I_zx
    I[1,2] = I[2,1] = I_yz
    
    return PosicionCM, I, Volumen, Densidad
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
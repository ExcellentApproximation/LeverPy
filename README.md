# LeverPy
A simple and rudimentary physics engine created in Python as my final college degree work.

How to use LeverPy:

1. Install the required python libraries (numpy, moderngl, PyGLM, qpsolvers[gurobi], pygame)
2. Download the folder "Programa"
3. Open "TFG (programa principal).py"
4. After line 137 you can add any object you want to the scene by using the function addObject(). There is an explanation of all of the addObject() function parameters at the end of this readme.
5. Execute the program. A window will open where you can visualize the scene. You can move around with the keys WASD and move the camera with the mouse. Holding left click will activate slow motion mode and right clicking will shoot the object defined at the function "disparar()"

Now lets take a look at the addObject() parameters:

1. Malla3D: 3D mesh of the object in .obj format. You can add meshes to the "Modelos" folder. IMPORTANT!! 3D MESHES MUST BE CONVEX POLYHEDRA FOR THE PHYSICS ENGINE TO WORK CORRECTLY!! Also, meshes need to be non-triangulated, so for example, if you have an object with a square face, the face should not be divided into two triangles, instead it should be just one square face. Triangulating the faces might make the physics engine and the texturing engine malfunction.
2. Masa: Mass of the object
3. Escala: Scale of the 3D mesh
4. Posicion: Position of the center of mass of the object (center of mass is calculated automatically assuming a constant density of the object)
5. EjeRot: Axis for the initial rotation of the object
6. AnguloRot: Angle of initial rotation around the specified axis. Must be specified in degrees.
7. Velocidad: Initial linear velocity of the object
8. VelocidadAngular: Initial angular velocity of the object
9. Estatico: Boolean parameter. If true the object will be affected by gravity, if false it wont be affected by it.
10. Textura: Texture of the object. Textures are stored on the "Texturas" folder
11. NTextura: Number of times the texture appears on every face of the object. 


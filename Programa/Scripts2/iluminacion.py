import glm

class Light:
    def __init__(self, position = (20,3,3), color = (1,1,1)):
        self.position = glm.vec3(position)
        self.color = glm.vec3(color)
        #intensidades
        self.Ia = 0.3 * self.color
        self.Id = 1.0 * self.color
        self.Is = 1.0 * self.color
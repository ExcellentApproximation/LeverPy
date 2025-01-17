#version 330 core

layout (location = 0) out vec4 fragColor;

in vec2 uv_0;
in vec3 normal;
in vec3 fragPos;

struct Light
{
    vec3 position;
    vec3 Ia;
    vec3 Id;
    vec3 Is;
};

uniform Light light;
uniform sampler2D u_texture_0;
uniform vec3 camPos;

vec3 getLight(vec3 color)
{
    vec3 Normal = normalize(normal);
    
    // luz ambiental
    vec3 ambient = light.Ia;
    
    // luz difusa
    vec3 lightDir = normalize(light.position - fragPos);
    float diff = max(0, dot(lightDir, Normal));
    vec3 diffuse = diff * light.Id;
    
    // luz especular
    vec3 viewDir = normalize(camPos - fragPos);
    vec3 reflectDir = reflect(-lightDir, Normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0), 32);
    vec3 specular = spec * light.Is;
    
    return color * (ambient + diffuse + specular);
}

void main() 
    {
        vec3 color2 = texture(u_texture_0, uv_0).rgb;
        color2 = getLight(color2);
        fragColor = vec4(color2, 1.0);
    }
# version 330 core

layout (location = 0) in vec2 in_texcoord_0;
layout (location = 1) in vec3 in_normal;
layout (location = 2) in vec3 in_position;

out vec2 uv_0;
out vec3 normal;
out vec3 fragPos;

uniform mat4 m_proj;
uniform mat4 m_view;


void main()
    {
        uv_0 = in_texcoord_0;
        fragPos = in_position;
        normal = normalize(in_normal);
        gl_Position = m_proj * m_view * vec4(in_position,1.0);
    }
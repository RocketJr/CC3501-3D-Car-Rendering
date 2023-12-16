#version 330

in vec3 position;
in vec2 texCoord;

uniform vec3 u_color = vec3(1.0);

uniform mat4 u_model = mat4(1.0);
uniform mat4 u_view = mat4(1.0);
uniform mat4 u_projection = mat4(1.0);

out vec3 fragColor;
out vec2 fragTexCoord;

void main()
{
    fragColor = u_color;
    fragTexCoord = texCoord;
    
    gl_Position = u_projection * u_view * u_model * vec4(position, 1.0f);
}
import pyglet           # pip install pyglet
from OpenGL import GL   # pip install PyOpenGL
import numpy as np      # pip install numpy o conda install numpy

# Leonardo Rikhardsson

WIDTH = 640
HEIGHT = 640

class Controller(pyglet.window.Window):
    def __init__(self, title, *args, **kargs):
        super().__init__(*args, **kargs)
        self.set_minimum_size(240, 240) # Evita error cuando se redimensiona a 0
        self.set_caption(title)

    def update(self, dt):
        pass

if __name__ == "__main__":
    # Instancia del controller
    controller = Controller("Tarea 0 Leonardo R", width=WIDTH, height=HEIGHT, resizable=True)
    
    # Código del vertex shader
    # cada vértice tiene 3 atributos
    # posición (x, y)
    # color (r, g, b)
    # intensidad
    vertex_source_code = """
        #version 330

        in vec2 position;
        in vec3 color;
        in float intensity;

        out vec3 fragColor;
        out float fragIntensity;

        void main()
        {
            fragColor = color;
            fragIntensity = intensity;
            gl_Position = vec4(position, 0.0f, 1.0f);
        }
    """

    # Código del fragment shader
    # La salida es un vector de 4 componentes (r, g, b, a)
    # donde a es la transparencia (por ahora no nos importa, se deja en 1)
    # El color resultante de cada fragmento ("pixel") es el color del vértice multiplicado por su intensidad
    fragment_source_code = """
        #version 330

        in vec3 fragColor;
        in float fragIntensity;
        out vec4 outColor;

        void main()
        {
            outColor = fragIntensity * vec4(fragColor, 1.0f);
        }
    """

    # Compilación de shaders
    vert_shader = pyglet.graphics.shader.Shader(vertex_source_code, "vertex")
    frag_shader = pyglet.graphics.shader.Shader(fragment_source_code, "fragment")
    # Creación del pipeline
    pipeline = pyglet.graphics.shader.ShaderProgram(vert_shader, frag_shader)

    # Análogo al triángulo
    # Se define un cuadrado del tamaño de la pantalla
    quad_positions1 = np.array([
        -0.3, -0.3, # abajo izquierda
         0.3, -0.3, # abajo derecha
        -0.3,  0.3, # arriba izquierda
         0.3,  0.3  # arriba derecha
    ], dtype=np.float32)

    quad_colors1 = np.array([
        0, 1, 1,
        0, 1, 1,
        0, 1, 1,
        0, 1, 1
    ], dtype=np.float32)

    quad_intensities1 = np.array([0.7, 0.7, 0.7, 0.7], dtype=np.float32)

    # Índices de los vértices del cuadrado
    # 2 triángulos con 3 vértices cada uno (ver ppt del auxiliar 1, slide 13)
    quad_indices = np.array([
        0, 1, 2,
        1, 3, 2
    ], dtype=np.uint32)

    # Creación de los vértices del cuadrado para uso en gpu
    # A diferencia del triángulo, aquí se usan los índices definidos anteriormente
    gpu_quad1 = pipeline.vertex_list_indexed(4, GL.GL_TRIANGLES, quad_indices)
    gpu_quad1.position = quad_positions1
    gpu_quad1.color = quad_colors1
    gpu_quad1.intensity = quad_intensities1

    quad_positions2 = np.array([
        -0.3,  0.3, # abajo izquierda
         0.3,  0.3, # abajo derecha
         0,  0.6, # arriba izquierda
         0.6,  0.6  # arriba derecha
    ], dtype=np.float32)

    quad_colors2 = np.array([
        1, 0, 0,
        1, 0, 0,
        1, 0, 0,
        1, 0, 0
    ], dtype=np.float32)

    quad_intensities2 = np.array([0.7, 0.7, 0.3, 0.3], dtype=np.float32)

    gpu_quad2 = pipeline.vertex_list_indexed(4, GL.GL_TRIANGLES, quad_indices)
    gpu_quad2.position = quad_positions2
    gpu_quad2.color = quad_colors2
    gpu_quad2.intensity = quad_intensities2

    quad_positions3 = np.array([
        0.3, -0.3, # abajo izquierda
         0.6,  0, # abajo derecha
         0.3, 0.3, # arriba izquierda
         0.6,  0.6  # arriba derecha
    ], dtype=np.float32)

    quad_colors3 = np.array([
        1, 0, 1,
        1, 0, 1,
        1, 0, 1,
        1, 0, 1
    ], dtype=np.float32)

    quad_intensities3 = np.array([0.7, 0.3, 0.7, 0.3], dtype=np.float32)

    gpu_quad3 = pipeline.vertex_list_indexed(4, GL.GL_TRIANGLES, quad_indices)
    gpu_quad3.position = quad_positions3
    gpu_quad3.color = quad_colors3
    gpu_quad3.intensity = quad_intensities3

    # draw loop
    # la función on_draw se ejecuta cada vez que se quiere dibujar algo en pantalla
    @controller.event
    def on_draw():
        # color de fondo al limpiar un frame (0,0,0) es negro
        GL.glClearColor(0, 0, 0, 1.0)
        # si hay algo dibujado se limpia del frame
        controller.clear()
        # se le dice al pipeline que se va a usar
        pipeline.use()
         # se le entrega al pipeline los vértices del cuadrado
         # queremos que estos se dibujen (draw) como un triángulo (GL_TRIANGLES)
        gpu_quad1.draw(GL.GL_TRIANGLES)
        gpu_quad2.draw(GL.GL_TRIANGLES)
        gpu_quad3.draw(GL.GL_TRIANGLES)

    pyglet.clock.schedule_interval(controller.update, 1/60) # se ejecuta update del controller cada 1/60 segundos
    pyglet.app.run() # se ejecuta pyglet
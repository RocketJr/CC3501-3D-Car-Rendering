import pyglet
from OpenGL import GL
import numpy as np
import trimesh as tm
import networkx as nx
import os
import sys
from pathlib import Path
# No es necesaria la siguiente línea si el archivo está en el root del repositorio
# sys.path.append(os.path.dirname(os.path.dirname((os.path.abspath(__file__)))))
import grafica.transformations as tr
import auxiliares.utils.shapes as shapes

# Leonardo Rikhardsson

WIDTH = 640
HEIGHT = 640

class Controller(pyglet.window.Window):
    def __init__(self, title, *args, **kargs):
        super().__init__(*args, **kargs)
        self.set_minimum_size(240, 240) # Evita error cuando se redimensiona a 0
        self.set_caption(title)
        self.key_handler = pyglet.window.key.KeyStateHandler()
        self.push_handlers(self.key_handler)
        self.program_state = { "total_time": 0.0 }
        self.init()

    def init(self):
        GL.glClearColor(1, 1, 1, 1.0)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glCullFace(GL.GL_BACK)
        GL.glFrontFace(GL.GL_CCW)
        GL.glPolygonMode(GL.GL_FRONT_AND_BACK,GL.GL_LINE)

    def is_key_pressed(self, key):
        return self.key_handler[key]

class Model():
    def __init__(self, position_data, index_data=None):
        self.position_data = position_data

        self.index_data = index_data
        if index_data is not None:
            self.index_data = np.array(index_data, dtype=np.uint32)

        self.gpu_data = None

    def init_gpu_data(self, pipeline):
        self.pipeline = pipeline
        if self.index_data is not None:
            self.gpu_data = pipeline.vertex_list_indexed(len(self.position_data) // 3, GL.GL_TRIANGLES, self.index_data)
        else:
            self.gpu_data = pipeline.vertex_list(len(self.position_data) // 3, GL.GL_TRIANGLES)
        
        self.gpu_data.position[:] = self.position_data

    def draw(self, mode = GL.GL_TRIANGLES):
        self.gpu_data.draw(mode)

class Mesh(Model):
    def __init__(self, asset_path):
        mesh_data = tm.load(asset_path)
        mesh_scale = tr.uniformScale(2.0 / mesh_data.scale)
        mesh_translate = tr.translate(*-mesh_data.centroid)
        mesh_data.apply_transform( mesh_scale @ mesh_translate)
        vertex_data = tm.rendering.mesh_to_vertexlist(mesh_data)
        indices = vertex_data[3]
        positions = vertex_data[4][1]

        super().__init__(positions, indices)

class Camera():
    def __init__(self, camera_type = "perspective"):
        self.position = np.array([1, 0, 0], dtype=np.float32)
        self.focus = np.array([0, 0, 0], dtype=np.float32)
        self.type = camera_type
        self.width = WIDTH
        self.height = HEIGHT

    def update(self):
        pass

    def get_view(self):
        lookAt_matrix = tr.lookAt(self.position, self.focus, np.array([0, 1, 0], dtype=np.float32))
        return np.reshape(lookAt_matrix, (16, 1), order="F")

    def get_projection(self):
        if self.type == "perspective":
            perspective_matrix = tr.perspective(90, self.width / self.height, 0.01, 100)
        elif self.type == "orthographic":
            depth = self.position - self.focus
            depth = np.linalg.norm(depth)
            perspective_matrix = tr.ortho(-(self.width/self.height) * depth, (self.width/self.height) * depth, -1 * depth, 1 * depth, 0.01, 100)
        return np.reshape(perspective_matrix, (16, 1), order="F")
    
    def resize(self, width, height):
        self.width = width
        self.height = height

class OrbitCamera(Camera):
    def __init__(self, distance, camera_type = "perspective"):
        super().__init__(camera_type)
        self.distance = distance
        self.phi = 0
        self.theta = np.pi / 2
        self.update()

    def update(self):
        if self.theta > np.pi:
            self.theta = np.pi
        elif self.theta < 0:
            self.theta = 0.0001

        self.position[0] = self.distance * np.sin(self.theta) * np.sin(self.phi)
        self.position[1] = self.distance * np.cos(self.theta)
        self.position[2] = self.distance * np.sin(self.theta) * np.cos(self.phi)

class SceneGraph():
    def __init__(self, camera=None):
        self.graph = nx.DiGraph(root="root")
        self.add_node("root")
        self.camera = camera

    def add_node(self,
                 name,
                 attach_to=None,
                 mesh=None,
                 color=[1, 1, 1],
                 transform=tr.identity(),
                 position=[0, 0, 0],
                 rotation=[0, 0, 0],
                 scale=[1, 1, 1],
                 mode=GL.GL_TRIANGLES):
        self.graph.add_node(
            name, 
            mesh=mesh, 
            color=color,
            transform=transform,
            position=np.array(position, dtype=np.float32),
            rotation=np.array(rotation, dtype=np.float32),
            scale=np.array(scale, dtype=np.float32),
            mode=mode)
        if attach_to is None:
            attach_to = "root"
        
        self.graph.add_edge(attach_to, name)

    def __getitem__(self, name):
        if name not in self.graph.nodes:
            raise KeyError(f"Node {name} not in graph")

        return self.graph.nodes[name]
    
    def __setitem__(self, name, value):
        if name not in self.graph.nodes:
            raise KeyError(f"Node {name} not in graph")

        self.graph.nodes[name] = value
    
    def get_transform(self, node):
        node = self.graph.nodes[node]
        transform = node["transform"]
        translation_matrix = tr.translate(node["position"][0], node["position"][1], node["position"][2])
        rotation_matrix = tr.rotationX(node["rotation"][0]) @ tr.rotationY(node["rotation"][1]) @ tr.rotationZ(node["rotation"][2])
        scale_matrix = tr.scale(node["scale"][0], node["scale"][1], node["scale"][2])
        return transform @ translation_matrix @ rotation_matrix @ scale_matrix

    def draw(self):
        root_key = self.graph.graph["root"]
        edges = list(nx.edge_dfs(self.graph, source=root_key))
        transformations = {root_key: self.get_transform(root_key)}

        for src, dst in edges:
            current_node = self.graph.nodes[dst]

            if not dst in transformations:
                transformations[dst] = transformations[src] @ self.get_transform(dst)

            if current_node["mesh"] is not None:
                current_pipeline = current_node["mesh"].pipeline
                current_pipeline.use()

                if self.camera is not None:
                    if "u_view" in current_pipeline.uniforms:
                        current_pipeline["u_view"] = self.camera.get_view()

                    if "u_projection" in current_pipeline.uniforms:
                        current_pipeline["u_projection"] = self.camera.get_projection()

                current_pipeline["u_model"] = np.reshape(transformations[dst], (16, 1), order="F")

                if "u_color" in current_pipeline.uniforms:
                    current_pipeline["u_color"] = np.array(current_node["color"], dtype=np.float32)
                current_node["mesh"].draw(current_node["mode"])

class VehicleHangar():
    def __init__(self, hangar, floor, podium, chasis, wheel1, wheel2, wheel3, wheel4, camera):
        self.graph = SceneGraph(camera)
        self.graph.add_node("environment")
        self.graph.add_node("Hangar",
                             attach_to="environment",
                             mesh=hangar,
                             color=shapes.GRAY,
                             position=[0, 3.4, 0],
                             scale=[10, 10, 10]
                            )
        self.graph.add_node("Base",
                             attach_to="environment",
                             mesh=floor,
                             color=shapes.GRAY,
                             scale=[12, 0, 12]
                            )
        self.graph.add_node("Car_Podium")
        self.graph.add_node("Podium",
                             attach_to="Car_Podium",
                             mesh=podium,
                             color=shapes.BLUE,
                             position=[0, 0.1, 0],
                             scale=[4, 0.1, 4]
                            )
        self.graph.add_node("Car", attach_to="Car_Podium")
        self.graph.add_node("Chasis",
                            attach_to="Car",
                             mesh=chasis,
                             color=shapes.YELLOW,
                             position=[0, 0.6, 0],
                             scale=[2, 2, 2]
                            )
        self.graph.add_node("Wheel", attach_to="Car")
        self.graph.add_node("Right_Front_wheel",
                            attach_to="Wheel",
                             mesh=wheel1,
                             color=shapes.LIGHT_BLUE,
                             position=[-0.7, 0.4, 1.15],
                             scale=[0.4, 0.4, 0.4]
                            )
        self.graph.add_node("Left_Front_wheel",
                            attach_to="Wheel",
                             mesh=wheel2,
                             color=shapes.GREEN,
                             position=[0.7, 0.4, 1.15],
                             scale=[0.4, 0.4, 0.4]
                            )
        self.graph.add_node("Right_Back_wheel",
                            attach_to="Wheel",
                             mesh=wheel3,
                             color=shapes.RED,
                             position=[-0.7, 0.4, -1],
                             scale=[0.4, 0.4, 0.4]
                            )
        self.graph.add_node("Left_Back_wheel",
                            attach_to="Wheel",
                             mesh=wheel4,
                             color=shapes.CYAN,
                             position=[0.7, 0.4, -1],
                             scale=[0.4, 0.4, 0.4]
                            )
        
    def draw(self):
        self.graph.draw()

    def RotatingCar(self,dt):
        self.graph["Right_Front_wheel"]["rotation"][0] += 1/100
        self.graph["Left_Front_wheel"]["rotation"][0] += 1/100
        self.graph["Right_Back_wheel"]["rotation"][0] += 1/100
        self.graph["Left_Back_wheel"]["rotation"][0] += 1/100

        self.graph["Car_Podium"]["transform"] = tr.rotationY(dt/2)


if __name__ == "__main__":
    # Instancia del controller
    controller = Controller("Tarea 1 Por Leonardo Rikhardsson", width=WIDTH, height=HEIGHT, resizable=True)

    with open(Path(os.path.dirname(__file__)) / "auxiliares/shaders/transform.vert") as f:
        color_vertex_source_code = f.read()

    with open(Path(os.path.dirname(__file__)) / "auxiliares/shaders/color.frag") as f:
        color_fragment_source_code = f.read()

    color_pipeline = pyglet.graphics.shader.ShaderProgram(
        pyglet.graphics.shader.Shader(color_vertex_source_code, "vertex"),
        pyglet.graphics.shader.Shader(color_fragment_source_code, "fragment")
    )

    # Para mover la camara
    camera = OrbitCamera(4, "perspective")
    # Camara phi es para el angulo para los lados
    camera.phi = np.pi / 4
    # Camara theta es para el grado de inclinacion
    camera.theta = np.pi / 3

    axes = Model(shapes.Axes["position"])
    axes.init_gpu_data(color_pipeline)
    axes.gpu_data.color[:] = shapes.Axes["color"]


    with open(Path(os.path.dirname(__file__)) / "auxiliares/shaders/color_mesh.vert") as f:
        vertex_source_code = f.read()

    with open(Path(os.path.dirname(__file__)) / "auxiliares/shaders/color_mesh.frag") as f:
        fragment_source_code = f.read()

    mesh_pipeline = pyglet.graphics.shader.ShaderProgram(
        pyglet.graphics.shader.Shader(vertex_source_code, "vertex"),
        pyglet.graphics.shader.Shader(fragment_source_code, "fragment")
    )

    #axis_scene = SceneGraph(camera)
    #axis_scene.add_node("axes", attach_to="root", mesh=axes, mode=GL.GL_LINES)

    hangar = Mesh("assets/LeoHangar.stl")
    hangar.init_gpu_data(mesh_pipeline)

    hangarFloor = Mesh("assets/cube.off")
    hangarFloor.init_gpu_data(mesh_pipeline)

    platform = Mesh("assets/cylinder.off")
    platform.init_gpu_data(mesh_pipeline)

    car = Mesh("assets/alfa2.off")
    car.init_gpu_data(mesh_pipeline)

    r1 = Mesh("assets/llanta1.off")
    r1.init_gpu_data(mesh_pipeline)

    r2 = Mesh("assets/llanta2.off")
    r2.init_gpu_data(mesh_pipeline)

    r3 = Mesh("assets/llanta3.off")
    r3.init_gpu_data(mesh_pipeline)

    r4 = Mesh("assets/llanta4.off")
    r4.init_gpu_data(mesh_pipeline)
    
    Tarea1 = VehicleHangar(hangar, hangarFloor, platform, car, r1, r2, r3, r4, camera)
     
    # Como no quiero implementar que se pueda rotar las camaras, lo dejo asi.
    #print("Controles Cámara:\n\tWASD: Rotar\n\t Q/E: Acercar/Alejar\n\t1/2: Cambiar tipo")
    def update(dt):
        controller.program_state["total_time"] += dt

        #if controller.is_key_pressed(pyglet.window.key.A):
        #    camera.phi -= dt
        #if controller.is_key_pressed(pyglet.window.key.D):
        #    camera.phi += dt
        #if controller.is_key_pressed(pyglet.window.key.W):
        #    camera.theta -= dt
        #if controller.is_key_pressed(pyglet.window.key.S):
        #    camera.theta += dt
        #if controller.is_key_pressed(pyglet.window.key.Q):
        #    camera.distance += dt
        #if controller.is_key_pressed(pyglet.window.key.E):
        #    camera.distance -= dt
        #if controller.is_key_pressed(pyglet.window.key.Z):
        #    camera.type = "perspective"
        #if controller.is_key_pressed(pyglet.window.key.X):
        #    camera.type = "orthographic"

        # Aquí se seleccionan los nodos de cada grafo y se cambia su estado
        Tarea1.RotatingCar(controller.program_state["total_time"])
        
        camera.update()

    @controller.event
    def on_resize(width, height):
        camera.resize(width, height)

    # draw loop
    @controller.event
    def on_draw():
        controller.clear()
        # No tengo para que dibujar los ejes
        #axis_scene.draw()

        # Aquí se dibujan los grafos, descomentar según se necesite
        Tarea1.draw()

    pyglet.clock.schedule_interval(update, 1/60)
    pyglet.app.run()

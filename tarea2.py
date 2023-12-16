import pyglet
from OpenGL import GL
import numpy as np
import sys

# No es necesario este bloque de código si se ejecuta desde la carpeta raíz del repositorio
# v
if sys.path[0] != "":
    sys.path.insert(0, "")
sys.path.append('../../')
# ^
# No es necesario este bloque de código si se ejecuta desde la carpeta raíz del repositorio

import auxiliares.utils.shapes as shapes
from auxiliares.utils.camera import FreeCamera
from auxiliares.utils.scene_graph import SceneGraph
from auxiliares.utils.drawables import Model, Texture, DirectionalLight, PointLight, SpotLight, Material
from auxiliares.utils.helpers import init_axis, init_pipeline, mesh_from_file, get_path

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
        self.program_state = { "total_time": 0.0, "camera": None }
        self.init()

    def init(self):
        GL.glClearColor(1, 1, 1, 1.0)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glCullFace(GL.GL_BACK)
        GL.glFrontFace(GL.GL_CCW)
        #GL.glPolygonMode(GL.GL_FRONT_AND_BACK,GL.GL_LINE)

    def is_key_pressed(self, key):
        return self.key_handler[key]

if __name__ == "__main__":
    # Instancia del controller
    controller = Controller("Tarea 2 Por Leonardo Rikhardsson", width=WIDTH, height=HEIGHT, resizable=True)

    controller.program_state["camera"] = FreeCamera([1, 1, 1], "perspective")
    controller.program_state["camera"].yaw = -3* np.pi/ 4
    controller.program_state["camera"].pitch = -np.pi / 4
    
    #Esto lo puedo borrar
    axis_scene = init_axis(controller)

    color_mesh_pipeline = init_pipeline(
        get_path("auxiliares/shaders/color_mesh.vert"),
        get_path("auxiliares/shaders/color_mesh.frag"))
    
    textured_mesh_pipeline = init_pipeline(
        get_path("auxiliares/shaders/textured_mesh.vert"),
        get_path("auxiliares/shaders/textured_mesh.frag"))
    
    color_mesh_lit_pipeline = init_pipeline(
        get_path("auxiliares/shaders/color_mesh_lit.vert"),
        get_path("auxiliares/shaders/color_mesh_lit.frag"))
    
    textured_mesh_lit_pipeline = init_pipeline(
        get_path("auxiliares/shaders/textured_mesh_lit.vert"),
        get_path("auxiliares/shaders/textured_mesh_lit.frag"))
    
    floorHangar = Model(shapes.Square["position"], shapes.Square["uv"], shapes.Square["normal"], index_data=shapes.Square["indices"])
    hangar = mesh_from_file("assets/LeoHangar.stl")[0]["mesh"]
    cylinder = mesh_from_file("assets/cylinder.off")[0]["mesh"]
    chasis = mesh_from_file("assets/alfa2.off")
    r1 = mesh_from_file("assets/llanta1.off")[0]["mesh"]
    r2 = mesh_from_file("assets/llanta2.off")[0]["mesh"]
    r3 = mesh_from_file("assets/llanta3.off")[0]["mesh"]
    r4 = mesh_from_file("assets/llanta4.off")[0]["mesh"]
    arrow = mesh_from_file("assets/arrow.off")[0]["mesh"]

    road = Texture("assets/Road_001_basecolor.jpg")
    wall5 = Texture("assets/wall5.jpg")

    graph = SceneGraph(controller)

    BlackRubber = Material(diffuse = [0.01, 0.01, 0.01], specular = [0.4, 0.4, 0.4], ambient = [0.02, 0.02, 0.02], shininess = 32)
    WhiteRubber = Material(diffuse = [1, 1, 1], specular = [0.4, 0.4, 0.4], ambient = [0.02, 0.02, 0.02], shininess = 32)
    GreyRubber = Material(diffuse = [0.7, 0.7, 0.7], specular = [0.4, 0.4, 0.4], ambient = [0.02, 0.02, 0.02], shininess = 32)

    Chrome = Material(diffuse = [0.8, 0.8, 0.8], specular = [0.774597, 0.774597, 0.774597], ambient = [0.25, 0.25, 0.25], shininess = 32)
    Jade = Material(diffuse = [0.54, 0.89, 0.63], specular = [0.316228, 0.316228, 0.316228], ambient = [0.135, 0.2225, 0.1575], shininess = 12.8)
    Obsidian = Material(diffuse = [0.18275, 0.17, 0.22525], specular = [0.332741, 0.328634, 0.346435], ambient = [0.05375, 0.05, 0.06625], shininess = 38.4)

    graph.add_node("point_light1",
                    pipeline=[color_mesh_lit_pipeline, textured_mesh_lit_pipeline],
                    position=[-2, 2, -2],
                    light=PointLight(diffuse = [0.6, 0.6, 0.6], specular = [0.6, 0.6, 0.6], ambient = [0.15, 0.15, 0.15]))
    
    graph.add_node("point_light2",
                    pipeline=[color_mesh_lit_pipeline, textured_mesh_lit_pipeline],
                    position=[2, 2, 2],
                    light=PointLight(diffuse = [0.6, 0.6, 0.6], specular = [0.6, 0.6, 0.6], ambient = [0.15, 0.15, 0.15]))
    
    graph.add_node("spotlight",
                    pipeline=[color_mesh_lit_pipeline, textured_mesh_lit_pipeline],
                    position=[2, 2, -2],
                    rotation=[-3*np.pi/4, -np.pi/4, 0],
                    light=SpotLight(diffuse = [1, 1, 1],
                          specular = [1, 1, 1],
                          ambient = [0.15, 0.15, 0.15],
                          cutOff=0.91,
                          outerCutOff=0.82
                          )
                    )
    
    # No funciona
    #graph.add_node(hangar[0]["id"],
                #attach_to="root",
                #mesh=hangar[0]["mesh"],
                #pipeline=color_mesh_lit_pipeline,
                #position=[0, 1.7, 0],
                #scale=[5, 5, 5],
                #material=Material(),
                #cull_face=False)

    graph.add_node("Place",
                   mesh=hangar,
                   pipeline=color_mesh_lit_pipeline,
                   #pipeline = textured_mesh_lit_pipeline,
                   position=[0, 1.7, 0],
                   scale=[5, 5, 5],
                   # material = materialEnv
                   material = Material(
                          diffuse = [1, 1, 1],
                          specular = [0.5, 0.5, 0.5],
                          ambient = [0.1, 0.1, 0.1],
                          shininess = 256
                     ))
    
    graph.add_node("Floor",
                   mesh=floorHangar,
                   pipeline = textured_mesh_lit_pipeline,
                   rotation=[-np.pi/2, 0, 0],
                   scale=[7, 7, 7],
                   texture=road,
                   material = Material(
                          diffuse = [1, 1, 1],
                          specular = [0.5, 0.5, 0.5],
                          ambient = [0.1, 0.1, 0.1],
                          shininess = 256
                     ))
    
    graph.add_node("Podium",
                   mesh=cylinder,
                   pipeline=color_mesh_lit_pipeline,
                   position=[0, 0.1, 0],
                   scale=[2, 0.1, 2],
                   material = Material(
                          diffuse = [1, 0, 0],
                          specular = [0.4, 0, 0.4],
                          ambient = [1, 1, 1],
                          shininess = 256
                     ))
    
    graph.add_node("Vehicles")

    graph.add_node("Car1", attach_to="Vehicles", position=[0, 0, 0])

    #auto = mesh_from_file("assets/alfa2.off")
    #graph.add_node(auto[0]["id"],
    #               attach_to="Car1",
    #               mesh=auto[0]["mesh"],
    #               pipeline=color_mesh_lit_pipeline,
    #               position=[0, 0.6, 0],
    #               scale=[2, 2, 2],
    #               material=Material())

    graph.add_node(chasis[0]["id"],
                attach_to="Car1",
                mesh=chasis[0]["mesh"],
                pipeline=color_mesh_lit_pipeline,
                position=[0, 0.4, 0],
                material=Chrome,
                cull_face=False)
                   
    graph.add_node("Wheel1", attach_to="Car1")

    graph.add_node("RFW1",
                   attach_to="Wheel1",
                   mesh=r1,
                   pipeline=color_mesh_lit_pipeline,
                   position=[-0.35, 0.3, 0.58],
                   scale=[0.2, 0.2, 0.2],
                   material=BlackRubber)
    
    graph.add_node("LFW1",
                   attach_to="Wheel1",
                   mesh=r2,
                   pipeline=color_mesh_lit_pipeline,
                   position=[0.35, 0.3, 0.58],
                   scale=[0.2, 0.2, 0.2],
                   material=BlackRubber)
    
    graph.add_node("RBW1",
                   attach_to="Wheel1",
                   mesh=r3,
                   pipeline=color_mesh_lit_pipeline,
                   position=[-0.35, 0.3, -0.5],
                   scale=[0.2, 0.2, 0.2],
                   material=BlackRubber)
    
    graph.add_node("LBW1",
                   attach_to="Wheel1",
                   mesh=r4,
                   pipeline=color_mesh_lit_pipeline,
                   position=[0.35, 0.3, -0.5],
                   scale=[0.2, 0.2, 0.2],
                   material=BlackRubber)
    
    graph.add_node("Car2", attach_to="Vehicles", position=[10, 0, 0])

    graph.add_node("Car2"+chasis[0]["id"],
                attach_to="Car2",
                mesh=chasis[0]["mesh"],
                pipeline=color_mesh_lit_pipeline,
                position=[0, 0.4, 0],
                material=Jade)
                   
    graph.add_node("Wheel2", attach_to="Car2")

    graph.add_node("RFW2",
                   attach_to="Wheel2",
                   mesh=r1,
                   pipeline=color_mesh_lit_pipeline,
                   position=[-0.35, 0.3, 0.58],
                   scale=[0.2, 0.2, 0.2],
                   material=GreyRubber)
    
    graph.add_node("LFW2",
                   attach_to="Wheel2",
                   mesh=r2,
                   pipeline=color_mesh_lit_pipeline,
                   position=[0.35, 0.3, 0.58],
                   scale=[0.2, 0.2, 0.2],
                   material=GreyRubber)
    
    graph.add_node("RBW2",
                   attach_to="Wheel2",
                   mesh=r3,
                   pipeline=color_mesh_lit_pipeline,
                   position=[-0.35, 0.3, -0.5],
                   scale=[0.2, 0.2, 0.2],
                   material=GreyRubber)
    
    graph.add_node("LBW2",
                   attach_to="Wheel2",
                   mesh=r4,
                   pipeline=color_mesh_lit_pipeline,
                   position=[0.35, 0.3, -0.5],
                   scale=[0.2, 0.2, 0.2],
                   material=GreyRubber)
    
    graph.add_node("Car3", attach_to="Vehicles", position=[-10, 0, 0])

    #graph.add_node("Chasis3",
                   #attach_to="Car3",
                   #mesh=chasis,
                   #pipeline=color_mesh_lit_pipeline,
                   #position=[0, 0.4, 0],
                   #material=Obsidian)

    graph.add_node("Car3"+chasis[0]["id"],
                attach_to="Car3",
                mesh=chasis[0]["mesh"],
                pipeline=color_mesh_lit_pipeline,
                position=[0, 0.4, 0],
                material=Obsidian)
                   
    graph.add_node("Wheel3", attach_to="Car3")

    graph.add_node("RFW3",
                   attach_to="Wheel3",
                   mesh=r1,
                   pipeline=color_mesh_lit_pipeline,
                   position=[-0.35, 0.3, 0.58],
                   scale=[0.2, 0.2, 0.2],
                   material=WhiteRubber)
    
    graph.add_node("LFW3",
                   attach_to="Wheel3",
                   mesh=r2,
                   pipeline=color_mesh_lit_pipeline,
                   position=[0.35, 0.3, 0.58],
                   scale=[0.2, 0.2, 0.2],
                   material=WhiteRubber)
    
    graph.add_node("RBW3",
                   attach_to="Wheel3",
                   mesh=r3,
                   pipeline=color_mesh_lit_pipeline,
                   position=[-0.35, 0.3, -0.5],
                   scale=[0.2, 0.2, 0.2],
                   material=WhiteRubber)
    
    graph.add_node("LBW3",
                   attach_to="Wheel3",
                   mesh=r4,
                   pipeline=color_mesh_lit_pipeline,
                   position=[0.35, 0.3, -0.5],
                   scale=[0.2, 0.2, 0.2],
                   material=WhiteRubber)
    
    def update(dt):
        controller.program_state["total_time"] += dt
        camera = controller.program_state["camera"]

        #if controller.is_key_pressed(pyglet.window.key.A):
        #    camera.position -= camera.right * dt
        #if controller.is_key_pressed(pyglet.window.key.D):
        #    camera.position += camera.right * dt
        #if controller.is_key_pressed(pyglet.window.key.W):
        #    camera.position += camera.forward * dt
        #if controller.is_key_pressed(pyglet.window.key.S):
        #    camera.position -= camera.forward * dt
        #if controller.is_key_pressed(pyglet.window.key.Q):
        #    camera.position[1] -= dt
        #if controller.is_key_pressed(pyglet.window.key.E):
        #    camera.position[1] += dt
        #if controller.is_key_pressed(pyglet.window.key._1):
        #    camera.type = "perspective"
        #if controller.is_key_pressed(pyglet.window.key._2):
        #    camera.type = "orthographic"
        camera.update()

        graph["Podium"]["rotation"][1] -= 0.01
        graph["Car1"]["rotation"][1] -= 0.01
        graph["Car2"]["rotation"][1] -= 0.01
        graph["Car3"]["rotation"][1] -= 0.01

    @controller.event
    def on_resize(width, height):
        controller.program_state["camera"].resize(width, height)

    print("Controles para escoger el vehiculo:\n\tA o W: Escoger el vehiculo anterior\n\tD: Escoger el vehiculo posterior\nHay 2 luces puntuales y 1 spotlight mirando hacia el vehiculo")
    @controller.event
    def on_key_press(symbol, modifiers):
        current_position = graph["Vehicles"]["position"][0]

        if symbol == pyglet.window.key.A or symbol == pyglet.window.key.W:
            if current_position == -10:
                graph["Vehicles"]["position"][0] += 10
            elif current_position == 0:
                graph["Vehicles"]["position"][0] += 10

        elif symbol == pyglet.window.key.D:
            if current_position == 10:
                graph["Vehicles"]["position"][0] -= 10
            elif current_position == 0:
                graph["Vehicles"]["position"][0] -= 10


    # draw loop
    @controller.event
    def on_draw():
        controller.clear()
        graph.draw()

    pyglet.clock.schedule_interval(update, 1/60)
    pyglet.app.run() 
import pyglet
from OpenGL import GL
import numpy as np
import sys
from pyglet.window import key
from Box2D import b2PolygonShape, b2World
import grafica.transformations as tr

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
from auxiliares.utils.colliders import CollisionManager, AABB, Sphere
from auxiliares.utils.helpers import init_axis, init_pipeline, mesh_from_file, get_path

# Leonardo Rikhardsson

WIDTH = 640
HEIGHT = 640

class Controller(pyglet.window.Window):
    def __init__(self, title, *args, **kargs):
        super().__init__(*args, **kargs)
        self.set_minimum_size(240, 240) # Evita error cuando se redimensiona a 0
        self.set_caption(title)
        self.keys_state = {}
        self.program_state = {
            "total_time": 0.0,
            "camera": None,
            "bodies": {},
            "world": None,
            # parámetros para el integrador
            "vel_iters": 6,
            "pos_iters": 2 }
        self.init()

        self.change_car = True
        self.active_car = None

    def init(self):
        GL.glClearColor(1, 1, 1, 1.0)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glCullFace(GL.GL_BACK)
        GL.glFrontFace(GL.GL_CCW)
        #GL.glPolygonMode(GL.GL_FRONT_AND_BACK,GL.GL_LINE)

    def is_key_pressed(self, key):
        return self.keys_state.get(key, False)

    def on_key_press(self, symbol, modifiers):
        controller.keys_state[symbol] = True
        super().on_key_press(symbol, modifiers)

    def on_key_release(self, symbol, modifiers):
        controller.keys_state[symbol] = False

if __name__ == "__main__":
    # Instancia del controller
    controller = Controller("Tarea 3 Por Leonardo Rikhardsson", width=WIDTH, height=HEIGHT, resizable=True)

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

    quad = Model(shapes.Square["position"], shapes.Square["uv"], shapes.Square["normal"], index_data=shapes.Square["indices"])

    road = Texture("assets/Road_001_basecolor.jpg")
    wall5 = Texture("assets/wall5.jpg")

    wall2 = Texture("assets/mario.jpg")

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

    graph.add_node("Place",
                   mesh=hangar,
                   pipeline=color_mesh_lit_pipeline,
                   position=[0, 1.7, 0],
                   scale=[5, 5, 5],
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

    graph.add_node("Chasis1",
                    mesh=chasis[0]["mesh"],
                    pipeline=color_mesh_lit_pipeline,
                    position=[0, 0.4, 0],
                    material=Chrome,
                    cull_face=False)

    graph.add_node("RFW1",
                    mesh=r1,
                    pipeline=color_mesh_lit_pipeline,
                    position=[0, 0.3, 0],
                    scale=[0.2, 0.2, 0.2],
                    material=BlackRubber)
    
    graph.add_node("LFW1",
                    mesh=r2,
                    pipeline=color_mesh_lit_pipeline,
                    position=[0, 0.3, 0],
                    scale=[0.2, 0.2, 0.2],
                    material=BlackRubber)
    
    graph.add_node("RBW1",
                    mesh=r3,
                    pipeline=color_mesh_lit_pipeline,
                    position=[0, 0.3, 0],
                    scale=[0.2, 0.2, 0.2],
                    material=BlackRubber)
    
    graph.add_node("LBW1",
                    mesh=r4,
                    pipeline=color_mesh_lit_pipeline,
                    position=[0, 0.3, 0],
                    scale=[0.2, 0.2, 0.2],
                    material=BlackRubber)

    graph.add_node("Chasis2",
                    mesh=chasis[0]["mesh"],
                    pipeline=color_mesh_lit_pipeline,
                    position=[0, 0.4, 0],
                    material=Jade)

    graph.add_node("RFW2",
                    mesh=r1,
                    pipeline=color_mesh_lit_pipeline,
                    position=[0, 0.3, 0],
                    scale=[0.2, 0.2, 0.2],
                    material=GreyRubber)
    
    graph.add_node("LFW2",
                    mesh=r2,
                    pipeline=color_mesh_lit_pipeline,
                    position=[0, 0.3, 0],
                    scale=[0.2, 0.2, 0.2],
                    material=GreyRubber)
    
    graph.add_node("RBW2",
                    mesh=r3,
                    pipeline=color_mesh_lit_pipeline,
                    position=[0, 0.3, 0],
                    scale=[0.2, 0.2, 0.2],
                    material=GreyRubber)
    
    graph.add_node("LBW2",
                    mesh=r4,
                    pipeline=color_mesh_lit_pipeline,
                    position=[0, 0.3, 0],
                    scale=[0.2, 0.2, 0.2],
                    material=GreyRubber)

    graph.add_node("Chasis3",
                    mesh=chasis[0]["mesh"],
                    pipeline=color_mesh_lit_pipeline,
                    position=[0, 0.4, 0],
                    material=Obsidian)

    graph.add_node("RFW3",
                    mesh=r1,
                    pipeline=color_mesh_lit_pipeline,
                    position=[0, 0.3, 0],
                    scale=[0.2, 0.2, 0.2],
                    material=WhiteRubber)
    
    graph.add_node("LFW3",
                    mesh=r2,
                    pipeline=color_mesh_lit_pipeline,
                    position=[0, 0.3, 0],
                    scale=[0.2, 0.2, 0.2],
                    material=WhiteRubber)
    
    graph.add_node("RBW3",
                    mesh=r3,
                    pipeline=color_mesh_lit_pipeline,
                    position=[0, 0.3, 0],
                    scale=[0.2, 0.2, 0.2],
                    material=WhiteRubber)
    
    graph.add_node("LBW3",
                    mesh=r4,
                    pipeline=color_mesh_lit_pipeline,
                    position=[0, 0.3, 0],
                    scale=[0.2, 0.2, 0.2],
                    material=WhiteRubber)

    graph.add_node("Course",
                    mesh = quad,
                    pipeline = textured_mesh_lit_pipeline,
                    position = [0, -1, 0],
                    rotation = [-np.pi/2, 0, 0],
                    scale = [20, 20, 20],
                    texture=wall2,
                    material = Material(
                          diffuse = [1, 1, 1],
                          specular = [0.5, 0.5, 0.5],
                          ambient = [0.1, 0.1, 0.1],
                          shininess = 256
                     ))
    
    graph.add_node("sun",
                    pipeline=[color_mesh_lit_pipeline, textured_mesh_lit_pipeline],
                    position=[0, 2, 0],
                    rotation=[-np.pi/4, 0, 0],
                    light=DirectionalLight(diffuse = [0.25, 0.25, 0.25], specular = [0.25, 0.25, 0.25], ambient = [0.15, 0.15, 0.15]))

    ########## Simulación Física ##########
    world = b2World(gravity=(0, 0))

    # Objetos estáticos
    wall1_body = world.CreateStaticBody(position=(-10, 0))
    wall1_body.CreatePolygonFixture(box=(0.5, 10), density=1, friction=1)

    wall2_body = world.CreateStaticBody(position=(10, 0))
    wall2_body.CreatePolygonFixture(box=(0.5, 10), density=1, friction=1)

    wall3_body = world.CreateStaticBody(position=(0, -10))
    wall3_body.CreatePolygonFixture(box=(10, 0.5), density=1, friction=1)

    wall4_body = world.CreateStaticBody(position=(0, 10))
    wall4_body.CreatePolygonFixture(box=(10, 0.5), density=1, friction=1)

    winzone_body = world.CreateStaticBody(position=(0, 7))
    winzoneFixture = winzone_body.CreateCircleFixture(radius=1, density=1, friction=1)
    winzoneFixture.sensor = True # No interactúa con otros objetos en la simulación física, solo detecta colisiones

    # Objetos dinámicos
    first_car = world.CreateDynamicBody(position=(0, 0), linearDamping=1, angularDamping=1)
    first_car.CreatePolygonFixture(box=(0.25, 0.5), density=3, friction=1)
    rfw_1 = world.CreateDynamicBody(position=(-0.35, 0.58), linearDamping=1, angularDamping=1)
    rfw_1.CreatePolygonFixture(box=(0.1, 0.1), density=1, friction=1)
    lfw_1 = world.CreateDynamicBody(position=(0.35, 0.58), linearDamping=1, angularDamping=1)
    lfw_1.CreatePolygonFixture(box=(0.1, 0.1), density=1, friction=1)
    rbw_1 = world.CreateDynamicBody(position=(-0.35, -0.5), linearDamping=1, angularDamping=1)
    rbw_1.CreatePolygonFixture(box=(0.1, 0.1), density=1, friction=1)
    lbw_1 = world.CreateDynamicBody(position=(0.35, -0.5), linearDamping=1, angularDamping=1)
    lbw_1.CreatePolygonFixture(box=(0.1, 0.1), density=1, friction=1)

    second_car = world.CreateDynamicBody(position=(0, -60), linearDamping=1, angularDamping=1)
    second_car.CreatePolygonFixture(box=(0.25, 0.5), density=3, friction=1)
    rfw_2 = world.CreateDynamicBody(position=(-0.35, -59.42), linearDamping=1, angularDamping=1)
    rfw_2.CreatePolygonFixture(box=(0.1, 0.1), density=1, friction=1)
    lfw_2 = world.CreateDynamicBody(position=(0.35, -59.42), linearDamping=1, angularDamping=1)
    lfw_2.CreatePolygonFixture(box=(0.1, 0.1), density=1, friction=1)
    rbw_2 = world.CreateDynamicBody(position=(-0.35, -60.5), linearDamping=1, angularDamping=1)
    rbw_2.CreatePolygonFixture(box=(0.1, 0.1), density=1, friction=1)
    lbw_2 = world.CreateDynamicBody(position=(0.35, -60.5), linearDamping=1, angularDamping=1)
    lbw_2.CreatePolygonFixture(box=(0.1, 0.1), density=1, friction=1)

    third_car = world.CreateDynamicBody(position=(0, -70), linearDamping=1, angularDamping=1)
    third_car.CreatePolygonFixture(box=(0.25, 0.5), density=3, friction=1)
    rfw_3 = world.CreateDynamicBody(position=(-0.35, -69.42), linearDamping=1, angularDamping=1)
    rfw_3.CreatePolygonFixture(box=(0.1, 0.1), density=1, friction=1)
    lfw_3 = world.CreateDynamicBody(position=(0.35, -69.42), linearDamping=1, angularDamping=1)
    lfw_3.CreatePolygonFixture(box=(0.1, 0.1), density=1, friction=1)
    rbw_3 = world.CreateDynamicBody(position=(-0.35, -70.5), linearDamping=1, angularDamping=1)
    rbw_3.CreatePolygonFixture(box=(0.1, 0.1), density=1, friction=1)
    lbw_3 = world.CreateDynamicBody(position=(0.35, -70.5), linearDamping=1, angularDamping=1)
    lbw_3.CreatePolygonFixture(box=(0.1, 0.1), density=1, friction=1)

    # Se guardan los cuerpos en el controller para poder acceder a ellos desde el loop de simulación
    controller.program_state["world"] = world

    controller.program_state["bodies"]["Chasis1"] = first_car
    controller.program_state["bodies"]["RFW1"] = rfw_1
    controller.program_state["bodies"]["LFW1"] = lfw_1
    controller.program_state["bodies"]["RBW1"] = rbw_1
    controller.program_state["bodies"]["LBW1"] = lbw_1

    controller.program_state["bodies"]["Chasis2"] = second_car
    controller.program_state["bodies"]["RFW2"] = rfw_2
    controller.program_state["bodies"]["LFW2"] = lfw_2
    controller.program_state["bodies"]["RBW2"] = rbw_2
    controller.program_state["bodies"]["LBW2"] = lbw_2

    controller.program_state["bodies"]["Chasis3"] = third_car
    controller.program_state["bodies"]["RFW3"] = rfw_3
    controller.program_state["bodies"]["LFW3"] = lfw_3
    controller.program_state["bodies"]["RBW3"] = rbw_3
    controller.program_state["bodies"]["LBW3"] = lbw_3

    controller.program_state["bodies"]["winzone"] = winzone_body

    world.CreateWheelJoint(bodyA=first_car, bodyB=rfw_1, anchor=(-0.35, 0.58), motorSpeed=0, maxMotorTorque=100, enableMotor=True)
    world.CreateWheelJoint(bodyA=first_car, bodyB=lfw_1, anchor=(0.35, 0.58), motorSpeed=0, maxMotorTorque=100, enableMotor=True)
    world.CreateWheelJoint(bodyA=first_car, bodyB=rbw_1, anchor=(-0.35, -0.5), motorSpeed=0, maxMotorTorque=100, enableMotor=True)
    world.CreateWheelJoint(bodyA=first_car, bodyB=lbw_1, anchor=(0.35, -0.5), motorSpeed=0, maxMotorTorque=100, enableMotor=True)

    world.CreateWheelJoint(bodyA=second_car, bodyB=rfw_2, anchor=(-0.35, -59.42), motorSpeed=0, maxMotorTorque=100, enableMotor=True)
    world.CreateWheelJoint(bodyA=second_car, bodyB=lfw_2, anchor=(0.35, -59.42), motorSpeed=0, maxMotorTorque=100, enableMotor=True)
    world.CreateWheelJoint(bodyA=second_car, bodyB=rbw_2, anchor=(-0.35, -60.5), motorSpeed=0, maxMotorTorque=100, enableMotor=True)
    world.CreateWheelJoint(bodyA=second_car, bodyB=lbw_2, anchor=(0.35, -60.5), motorSpeed=0, maxMotorTorque=100, enableMotor=True)

    world.CreateWheelJoint(bodyA=third_car, bodyB=rfw_3, anchor=(-0.35, -69.42), motorSpeed=0, maxMotorTorque=100, enableMotor=True)
    world.CreateWheelJoint(bodyA=third_car, bodyB=lfw_3, anchor=(0.35, -69.42), motorSpeed=0, maxMotorTorque=100, enableMotor=True)
    world.CreateWheelJoint(bodyA=third_car, bodyB=rbw_3, anchor=(-0.35, -70.5), motorSpeed=0, maxMotorTorque=100, enableMotor=True)
    world.CreateWheelJoint(bodyA=third_car, bodyB=lbw_3, anchor=(0.35, -70.5), motorSpeed=0, maxMotorTorque=100, enableMotor=True)

    #######################################

    def initialState(car):
        car.angle = 0
        car.angularVelocity = 0
        car.linearVelocity = (0, 0)
        if car == first_car:
                rfw_1.angle = 0
                rfw_1.angularVelocity = 0
                rfw_1.linearVelocity = (0, 0)
                lfw_1.angle = 0
                lfw_1.angularVelocity = 0
                lfw_1.linearVelocity = (0, 0)
                rbw_1.angle = 0
                rbw_1.angularVelocity = 0
                rbw_1.linearVelocity = (0, 0)
                lbw_1.angle = 0
                lbw_1.angularVelocity = 0
                lbw_1.linearVelocity = (0, 0)
        elif car == second_car:
                rfw_2.angle = 0
                rfw_2.angularVelocity = 0
                rfw_2.linearVelocity = (0, 0)
                lfw_2.angle = 0
                lfw_2.angularVelocity = 0
                lfw_2.linearVelocity = (0, 0)
                rbw_2.angle = 0
                rbw_2.angularVelocity = 0
                rbw_2.linearVelocity = (0, 0)
                lbw_2.angle = 0
                lbw_2.angularVelocity = 0
                lbw_2.linearVelocity = (0, 0)
        elif car == third_car:
                rfw_3.angle = 0
                rfw_3.angularVelocity = 0
                rfw_3.linearVelocity = (0, 0)
                lfw_3.angle = 0
                lfw_3.angularVelocity = 0
                lfw_3.linearVelocity = (0, 0)
                rbw_3.angle = 0
                rbw_3.angularVelocity = 0
                rbw_3.linearVelocity = (0, 0)
                lbw_3.angle = 0
                lbw_3.angularVelocity = 0
                lbw_3.linearVelocity = (0, 0)

    # Aquí se actualizan los parámetros de la simulación física
    def update_world(dt):
        controller.program_state["total_time"] += dt
        controller.program_state["world"].Step(dt, controller.program_state["vel_iters"], controller.program_state["pos_iters"])

        graph["Chasis1"]["position"][0] = first_car.position[0]
        graph["Chasis1"]["position"][2] = first_car.position[1]
        graph["Chasis1"]["rotation"][1] = -first_car.angle
        graph["RFW1"]["position"][0] = rfw_1.position[0]
        graph["RFW1"]["position"][2] = rfw_1.position[1]
        graph["LFW1"]["position"][0] = lfw_1.position[0]
        graph["LFW1"]["position"][2] = lfw_1.position[1]
        graph["RBW1"]["position"][0] = rbw_1.position[0]
        graph["RBW1"]["position"][2] = rbw_1.position[1]
        graph["RBW1"]["rotation"][1] = -first_car.angle
        graph["LBW1"]["position"][0] = lbw_1.position[0]
        graph["LBW1"]["position"][2] = lbw_1.position[1]
        graph["LBW1"]["rotation"][1] = -first_car.angle

        graph["Chasis2"]["position"][0] = second_car.position[0]
        graph["Chasis2"]["position"][2] = second_car.position[1]
        graph["Chasis2"]["rotation"][1] = -second_car.angle
        graph["RFW2"]["position"][0] = rfw_2.position[0]
        graph["RFW2"]["position"][2] = rfw_2.position[1]
        graph["LFW2"]["position"][0] = lfw_2.position[0]
        graph["LFW2"]["position"][2] = lfw_2.position[1]
        graph["RBW2"]["position"][0] = rbw_2.position[0]
        graph["RBW2"]["position"][2] = rbw_2.position[1]
        graph["RBW2"]["rotation"][1] = -second_car.angle
        graph["LBW2"]["position"][0] = lbw_2.position[0]
        graph["LBW2"]["position"][2] = lbw_2.position[1]
        graph["LBW2"]["rotation"][1] = -second_car.angle

        graph["Chasis3"]["position"][0] = third_car.position[0]
        graph["Chasis3"]["position"][2] = third_car.position[1]
        graph["Chasis3"]["rotation"][1] = -third_car.angle
        graph["RFW3"]["position"][0] = rfw_3.position[0]
        graph["RFW3"]["position"][2] = rfw_3.position[1]
        graph["LFW3"]["position"][0] = lfw_3.position[0]
        graph["LFW3"]["position"][2] = lfw_3.position[1]
        graph["RBW3"]["position"][0] = rbw_3.position[0]
        graph["RBW3"]["position"][2] = rbw_3.position[1]
        graph["RBW3"]["rotation"][1] = -third_car.angle
        graph["LBW3"]["position"][0] = lbw_3.position[0]
        graph["LBW3"]["position"][2] = lbw_3.position[1]
        graph["LBW3"]["rotation"][1] = -third_car.angle
    
    def update(dt):
        controller.program_state["total_time"] += dt
        camera = controller.program_state["camera"]

        winzone_body = controller.program_state["bodies"]["winzone"]
        if winzone_body.fixtures[0].TestPoint(first_car.position) or winzone_body.fixtures[0].TestPoint(second_car.position) or winzone_body.fixtures[0].TestPoint(third_car.position):
            print("\nGanaste!")
            pyglet.app.exit()

        if controller.change_car == True:            
            graph["Podium"]["rotation"][1] -= 0.01

            first_car.angle += 0.01
            graph["RFW1"]["rotation"][1] = - first_car.angle
            graph["LFW1"]["rotation"][1] = - first_car.angle

            second_car.angle += 0.01
            graph["RFW2"]["rotation"][1] = - second_car.angle
            graph["LFW2"]["rotation"][1] = - second_car.angle

            third_car.angle += 0.01
            graph["RFW3"]["rotation"][1] = - third_car.angle
            graph["LFW3"]["rotation"][1] = - third_car.angle
                                
        else:
            camera.position[0] = controller.active_car.position[0] + 2 * np.sin(controller.active_car.angle)
            camera.position[1] = 2
            camera.position[2] = controller.active_car.position[1] - 2 * np.cos(controller.active_car.angle)
            camera.yaw = controller.active_car.angle + np.pi / 2
            if controller.active_car is not None:
                if controller.is_key_pressed(pyglet.window.key._1):
                    camera.type = "perspective"
                if controller.is_key_pressed(pyglet.window.key._2):
                    camera.type = "orthographic"

                if controller.is_key_pressed(pyglet.window.key.W):
                    if controller.active_car == first_car:
                        graph["RFW1"]["rotation"][0] += 0.05
                        graph["LFW1"]["rotation"][0] += 0.05
                        graph["RBW1"]["rotation"][0] += 0.05
                        graph["LBW1"]["rotation"][0] += 0.05
                        forward = graph.get_forward("Chasis1")
                        controller.program_state["bodies"]["RBW1"].ApplyForceToCenter((forward[0]*4, forward[2]*4), True)
                        controller.program_state["bodies"]["LBW1"].ApplyForceToCenter((forward[0]*4, forward[2]*4), True)
                        if controller.is_key_pressed(pyglet.window.key.A):
                            rfw_1.angularVelocity = -20
                            lfw_1.angularVelocity = -20
                        if controller.is_key_pressed(pyglet.window.key.D):
                            rfw_1.angularVelocity = 20
                            lfw_1.angularVelocity = 20
                    elif controller.active_car == second_car:
                        graph["RFW2"]["rotation"][0] += 0.05
                        graph["LFW2"]["rotation"][0] += 0.05
                        graph["RBW2"]["rotation"][0] += 0.05
                        graph["LBW2"]["rotation"][0] += 0.05
                        forward = graph.get_forward("Chasis2")
                        controller.program_state["bodies"]["RBW2"].ApplyForceToCenter((forward[0]*4, forward[2]*4), True)
                        controller.program_state["bodies"]["LBW2"].ApplyForceToCenter((forward[0]*4, forward[2]*4), True)
                        if controller.is_key_pressed(pyglet.window.key.A):
                            rfw_2.angularVelocity = -20
                            lfw_2.angularVelocity = -20
                        if controller.is_key_pressed(pyglet.window.key.D):
                            rfw_2.angularVelocity = 20
                            lfw_2.angularVelocity = 20
                    elif controller.active_car == third_car:
                        graph["RFW3"]["rotation"][0] += 0.05
                        graph["LFW3"]["rotation"][0] += 0.05
                        graph["RBW3"]["rotation"][0] += 0.05
                        graph["LBW3"]["rotation"][0] += 0.05
                        forward = graph.get_forward("Chasis3")
                        controller.program_state["bodies"]["RBW3"].ApplyForceToCenter((forward[0]*4, forward[2]*4), True)
                        controller.program_state["bodies"]["LBW3"].ApplyForceToCenter((forward[0]*4, forward[2]*4), True)
                        if controller.is_key_pressed(pyglet.window.key.A):
                            rfw_3.angularVelocity = -20
                            lfw_3.angularVelocity = -20
                        if controller.is_key_pressed(pyglet.window.key.D):
                            rfw_3.angularVelocity = 20
                            lfw_3.angularVelocity = 20
            
                if controller.is_key_pressed(pyglet.window.key.S):
                    if controller.active_car == first_car:
                        graph["RFW1"]["rotation"][0] -= 0.05
                        graph["LFW1"]["rotation"][0] -= 0.05
                        graph["RBW1"]["rotation"][0] -= 0.05
                        graph["LBW1"]["rotation"][0] -= 0.05
                        forward = graph.get_forward("Chasis1")
                        controller.program_state["bodies"]["RBW1"].ApplyForceToCenter((-forward[0]*4, -forward[2]*4), True)
                        controller.program_state["bodies"]["LBW1"].ApplyForceToCenter((-forward[0]*4, -forward[2]*4), True)
                        if controller.is_key_pressed(pyglet.window.key.A):
                                rfw_1.angularVelocity = 20
                                lfw_1.angularVelocity = 20
                        if controller.is_key_pressed(pyglet.window.key.D):
                                rfw_1.angularVelocity = -20
                                lfw_1.angularVelocity = -20
                    elif controller.active_car == second_car:
                        graph["RFW2"]["rotation"][0] -= 0.05
                        graph["LFW2"]["rotation"][0] -= 0.05
                        graph["RBW2"]["rotation"][0] -= 0.05
                        graph["LBW2"]["rotation"][0] -= 0.05
                        forward = graph.get_forward("Chasis2")
                        controller.program_state["bodies"]["RBW2"].ApplyForceToCenter((-forward[0]*4, -forward[2]*4), True)
                        controller.program_state["bodies"]["LBW2"].ApplyForceToCenter((-forward[0]*4, -forward[2]*4), True)
                        if controller.is_key_pressed(pyglet.window.key.A):
                                rfw_2.angularVelocity = 20
                                lfw_2.angularVelocity = 20
                        if controller.is_key_pressed(pyglet.window.key.D):
                                rfw_2.angularVelocity = -20
                                lfw_2.angularVelocity = -20
                    elif controller.active_car == third_car:
                        graph["RFW3"]["rotation"][0] -= 0.05
                        graph["LFW3"]["rotation"][0] -= 0.05
                        graph["RBW3"]["rotation"][0] -= 0.05
                        graph["LBW3"]["rotation"][0] -= 0.05
                        forward = graph.get_forward("Chasis3")
                        controller.program_state["bodies"]["RBW3"].ApplyForceToCenter((-forward[0]*4, -forward[2]*4), True)
                        controller.program_state["bodies"]["LBW3"].ApplyForceToCenter((-forward[0]*4, -forward[2]*4), True)
                        if controller.is_key_pressed(pyglet.window.key.A):
                                rfw_3.angularVelocity = 20
                                lfw_3.angularVelocity = 20
                        if controller.is_key_pressed(pyglet.window.key.D):
                                rfw_3.angularVelocity = -20
                                lfw_3.angularVelocity = -20
            
                if controller.is_key_pressed(pyglet.window.key.A):
                    if controller.active_car == first_car:
                        graph["RFW1"]["rotation"][1] = np.pi/6 - first_car.angle
                        graph["LFW1"]["rotation"][1] = np.pi/6 - first_car.angle                       
                    elif controller.active_car == second_car:
                        graph["RFW2"]["rotation"][1] = np.pi/6 - second_car.angle
                        graph["LFW2"]["rotation"][1] = np.pi/6 - second_car.angle                       
                    elif controller.active_car == third_car:
                        graph["RFW3"]["rotation"][1] = np.pi/6 - third_car.angle
                        graph["LFW3"]["rotation"][1] = np.pi/6 - third_car.angle

                elif controller.is_key_pressed(pyglet.window.key.D):
                    if controller.active_car == first_car:
                        graph["RFW1"]["rotation"][1] = -np.pi/6 - first_car.angle
                        graph["LFW1"]["rotation"][1] = -np.pi/6 - first_car.angle
                    if controller.active_car == second_car:
                        graph["RFW2"]["rotation"][1] = -np.pi/6 - second_car.angle
                        graph["LFW2"]["rotation"][1] = -np.pi/6 - second_car.angle
                    if controller.active_car == third_car:
                        graph["RFW3"]["rotation"][1] = -np.pi/6 - third_car.angle
                        graph["LFW3"]["rotation"][1] = -np.pi/6 - third_car.angle
                
                else:
                    if controller.active_car == first_car:
                        graph["RFW1"]["rotation"][1] = - first_car.angle
                        graph["LFW1"]["rotation"][1] = - first_car.angle
                    if controller.active_car == second_car:
                        graph["RFW2"]["rotation"][1] = - second_car.angle
                        graph["LFW2"]["rotation"][1] = - second_car.angle
                    if controller.active_car == third_car:
                        graph["RFW3"]["rotation"][1] = - third_car.angle
                        graph["LFW3"]["rotation"][1] = - third_car.angle
                
        camera.update()
        update_world(dt)

    @controller.event
    def on_resize(width, height):
        controller.program_state["camera"].resize(width, height)

    print("Controles para escoger el vehiculo:\n\tSPACE: Cambia el vehiculo\n\tENTER: Escoger el vehiculo a manejar\n")
    print("Hay 2 luces puntuales, 1 spotlight mirando hacia el vehiculo y 1 luz direccional\n")
    print("Controles para manejar el vehiculo:\n\tA: Gira hacia la izquierda\n\tD: Gira hacia la derecha\n\tW: Para avanzar\n\tS: Para retroceder")
    @controller.event
    def on_key_press(symbol, modifiers):
        camera = controller.program_state["camera"]

        if symbol == pyglet.window.key.SPACE:
            if controller.change_car == True:
                if controller.active_car == None:
                    controller.active_car = first_car

                if controller.active_car == first_car:
                    controller.active_car = second_car
                    initialState(first_car)
                    first_car.position = (0, -70)
                    rfw_1.position = (-0.35, -69.42)
                    lfw_1.position = (0.35, -69.42)
                    rbw_1.position = (-0.35, -70.5)
                    lbw_1.position = (0.35, -70.5)

                    initialState(second_car)
                    second_car.position = (0, 0)
                    rfw_2.position = (-0.35, 0.58)
                    lfw_2.position = (0.35, 0.58)
                    rbw_2.position = (-0.35, -0.5)
                    lbw_2.position = (0.35, -0.5)

                    initialState(third_car)
                    third_car.position = (0, -60)
                    rfw_3.position = (-0.35, -59.42)
                    lfw_3.position = (0.35, -59.42)
                    rbw_3.position = (-0.35, -60.5)
                    lbw_3.position = (0.35, -60.5)
                    
                elif controller.active_car == second_car:
                    controller.active_car = third_car
                    initialState(first_car)
                    first_car.position = (0, -60)
                    rfw_1.position = (-0.35, -59.42)
                    lfw_1.position = (0.35, -59.42)
                    rbw_1.position = (-0.35, -60.5)
                    lbw_1.position = (0.35, -60.5)

                    initialState(second_car)
                    second_car.position = (0, -70)
                    rfw_2.position = (-0.35, -69.42)
                    lfw_2.position = (0.35, -69.42)
                    rbw_2.position = (-0.35, -70.5)
                    lbw_2.position = (0.35, -70.5)

                    initialState(third_car)
                    third_car.position = (0, 0)
                    rfw_3.position = (-0.35, 0.58)
                    lfw_3.position = (0.35, 0.58)
                    rbw_3.position = (-0.35, -0.5)
                    lbw_3.position = (0.35, -0.5)

                elif controller.active_car == third_car:
                    controller.active_car = first_car
                    initialState(first_car)
                    first_car.position = (0, 0)
                    rfw_1.position = (-0.35, 0.58)
                    lfw_1.position = (0.35, 0.58)
                    rbw_1.position = (-0.35, -0.5)
                    lbw_1.position = (0.35, -0.5)

                    initialState(second_car)
                    second_car.position = (0, -60)
                    rfw_2.position = (-0.35, -59.42)
                    lfw_2.position = (0.35, -59.42)
                    rbw_2.position = (-0.35, -60.5)
                    lbw_2.position = (0.35, -60.5)

                    initialState(third_car)
                    third_car.position = (0, -70)
                    rfw_3.position = (-0.35, -69.42)
                    lfw_3.position = (0.35, -69.42)
                    rbw_3.position = (-0.35, -70.5)
                    lbw_3.position = (0.35, -70.5)
                    
        if symbol == pyglet.window.key.ENTER:
            controller.change_car = False
            graph["point_light1"]["position"] = [0, 30, -60]
            graph["point_light2"]["position"] = [0, 30, -60]
            graph["Place"]["position"] = [0, 30, -60]
            graph["Floor"]["position"] = [0, 30, -60]
            graph["Podium"]["position"] = [0, 30, -60]
            graph["spotlight"]["position"] = [0, 2, 7]
            graph["spotlight"]["rotation"] = [-np.pi/2, 0, 0]
            graph["Course"]["position"] = [0, 0, 0]
            if controller.active_car == None:
                controller.active_car = first_car
            
            if controller.active_car == first_car:
                graph["Chasis2"]["position"][1] = 30
                graph["RFW2"]["position"][1] = 30
                graph["LFW2"]["position"][1] = 30
                graph["RBW2"]["position"][1] = 30
                graph["LBW2"]["position"][1] = 30
                graph["Chasis3"]["position"][1] = 30
                graph["RFW3"]["position"][1] = 30
                graph["LFW3"]["position"][1] = 30
                graph["RBW3"]["position"][1] = 30
                graph["LBW3"]["position"][1] = 30
                first_car.position = (0, 0)
                initialState(first_car)
                rfw_1.position = (-0.35, 0.58)
                lfw_1.position = (0.35, 0.58)
                rbw_1.position = (-0.35, -0.5)
                lbw_1.position = (0.35, -0.5)

            elif controller.active_car == second_car:
                graph["Chasis1"]["position"][1] = 30
                graph["RFW1"]["position"][1] = 30
                graph["LFW1"]["position"][1] = 30
                graph["RBW1"]["position"][1] = 30
                graph["LBW1"]["position"][1] = 30
                graph["Chasis3"]["position"][1] = 30
                graph["RFW3"]["position"][1] = 30
                graph["LFW3"]["position"][1] = 30
                graph["RBW3"]["position"][1] = 30
                graph["LBW3"]["position"][1] = 30
                second_car.position = (0, 0)
                initialState(second_car)
                rfw_2.position = (-0.35, 0.58)
                lfw_2.position = (0.35, 0.58)
                rbw_2.position = (-0.35, -0.5)
                lbw_2.position = (0.35, -0.5)

            elif controller.active_car == third_car:
                graph["Chasis1"]["position"][1] = 30
                graph["RFW1"]["position"][1] = 30
                graph["LFW1"]["position"][1] = 30
                graph["RBW1"]["position"][1] = 30
                graph["LBW1"]["position"][1] = 30
                graph["Chasis2"]["position"][1] = 30
                graph["RFW2"]["position"][1] = 30
                graph["LFW2"]["position"][1] = 30
                graph["RBW2"]["position"][1] = 30
                graph["LBW2"]["position"][1] = 30
                third_car.position = (0, 0)
                initialState(third_car)
                rfw_3.position = (-0.35, 0.58)
                lfw_3.position = (0.35, 0.58)
                rbw_3.position = (-0.35, -0.5)
                lbw_3.position = (0.35, -0.5)

    @controller.event
    def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
        if buttons & pyglet.window.mouse.RIGHT:
            controller.program_state["camera"].yaw += dx * 0.01
            controller.program_state["camera"].pitch += dy * 0.01

    # draw loop
    @controller.event
    def on_draw():
        controller.clear()
        #axis_scene.draw()
        graph.draw()
        
    pyglet.clock.schedule_interval(update, 1/60)
    pyglet.app.run()
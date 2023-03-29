from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from direct.actor.Actor import Actor
from ursina.shaders import lit_with_shadows_shader

# Функция выстрела
def shoot():
    if not gun.on_cooldown:
        #print('shoot')
        gun.on_cooldown = True
        invoke(setattr, gun, 'on_cooldown', False, delay=.15) #вызывает функцию с задержкой
        if mouse.hovered_entity and hasattr(mouse.hovered_entity, 'hp'):
            mouse.hovered_entity.hp -= 10
            mouse.hovered_entity.blink(color.red)


# Функция определяющая ввода
def input(key):
    if key == "left mouse down":
        Audio("assets/minigun.wav")
        Animation("assets/spark", parent=camera.ui, fps=5, scale=0.1, position=(0.04, -.16), loop=False)
        shoot()
        # Анимация пули
        bullet = Entity(parent=gun, model='cube', scale=0.7, color=color.black)
        bullet.world_parent = scene
        bullet.animate_position(bullet.position + (bullet.forward * 100), curve=curve.linear, duration=1)
        destroy(bullet, delay=1)



app = Ursina()

editor_camera = EditorCamera(enabled=False, ignore_paused=True) # для паузы и установки камеры в свободное положение
# Небо
sunsetSky = load_texture('assets/skybox/sunset.jpg')
Sky(texture=sunsetSky)

# 2Главный герой
player = FirstPersonController(model="cube", speed=6, origin_y=-.5, position=(40, 0, 40))
player.collider = BoxCollider(player, Vec3(0,1,0), Vec3(1,2,1))

# 1Делаем землю
ground = Entity(model='plane', scale=(150, 1, 150), color=color.lime, texture='white_cube',
                texture_scale=(100, 100), collider='box')

# 3Делаем стенки
wall_1 = Entity(model='cube', collider='box', position=(-8, 0, 0), scale=(8, 5, 1), rotation=(0, 0, 0), texture='brick',
                texture_scale=(5, 5), color=color.rgb(255, 128, 0))
wall_2 = duplicate(wall_1, z=5)
wall_3 = duplicate(wall_1, z=10)
wall_4 = duplicate(wall_1, x=-15, rotation=(0, 90, 0))
wall_5 = duplicate(wall_1, x=-15, z=8, rotation=(0, 90, 0))

# 3Делаем стенки 2
for i in range(16):
    Entity(model='cube', origin_y=-.5, scale=2, texture='brick', texture_scale=(1,2),
        x=random.uniform(-50,50),
        z=random.uniform(-50,50),
        collider='box',
        scale_y = random.uniform(2,3),
        color=color.hsv(0, 0, random.uniform(.9, 1))
        )


# 4Делаем оружие
gun = Entity(model="assets/minigun.obj", parent=camera, scale=0.15, color=color.dark_gray, position=(0.5, -0.75, 1.7),
             rotation=(-5, -10, -10), on_cooldown=False)

# 5 Зомби

"""zombie = Entity(collider='capsule', position=(0, 0, -6), scale=1.43, shader=lit_with_shadows_shader)

animator = Actor("assets/zomby.gltf")
animator.reparentTo(zombie)
animator.loop('run')
zombie.add_script(SmoothFollow(target=player, offset=[0, 0, 0], speed=0.3))


def update():
    # 5 Зомби поворот за героем
    zombie.look_at_2d(player.position, 'y')"""




#robot = FrameAnimation3d('models/zombies/robot', position=(15, 0, 0), fps=18, scale=0.015, color=color.black)


# Враг
shootables_parent = Entity()
mouse.traverse_target = shootables_parent # чтобы срабатывало убывание здоровья при нажатии на клавишу мыши

class Enemy(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=shootables_parent, model=FrameAnimation3d('models/zombies/robot', scale=0.015, color=color.black), origin_y=-.5, color=color.light_gray, collider='box', **kwargs)

        # шкала здоровья у врага
        self.health_bar = Entity(parent=self, y=2.3, model='cube', color=color.red, world_scale=(1.5,.1,.1))
        self.max_hp = 100
        self.hp = self.max_hp

    def update(self):
        dist = distance_xz(player.position, self.position)
        if dist > 40:
            return

        self.health_bar.alpha = max(0, self.health_bar.alpha - time.dt)


        self.look_at_2d(player.position, 'y')
        hit_info = raycast(self.world_position + Vec3(0, 0.1, 0), self.forward, 30, ignore=(self,))
        if hit_info.entity == player:
            if dist > 2:
                self.position += self.forward * time.dt * 3

    @property
    def hp(self):
        return self._hp

    @hp.setter # если здоровье закончится, то удаляем робота
    def hp(self, value):
        self._hp = value
        if value <= 0:
            destroy(self)
            return

        self.health_bar.world_scale_x = self.hp / self.max_hp * 1.5
        self.health_bar.alpha = 1


enemies = [Enemy(x=x*7) for x in range(7)] # Чтобы было 7 врагов на расстоянии *7 по оси x



# Пауза

pause_handler = Entity(ignore_paused=True)
pause_text = Text('ПАУЗА', origin=(0,0), scale=2, enabled=False) # Make a Text saying "PAUSED" just to make it clear when it's paused.

def pause_handler_input(key):
    if key == 'escape':
        application.paused = not application.paused # Pause/unpause the game.
        pause_text.enabled = application.paused     # Also toggle "PAUSED" graphic.

    if key == 'tab':  # press tab to toggle edit/play mode
        editor_camera.enabled = not editor_camera.enabled

        player.visible_self = editor_camera.enabled
        player.cursor.enabled = not editor_camera.enabled
        gun.enabled = not editor_camera.enabled
        mouse.locked = not editor_camera.enabled
        editor_camera.position = player.position

        application.paused = editor_camera.enabled

pause_handler.input = pause_handler_input   # Assign the input function to the pause handler.




app.run()

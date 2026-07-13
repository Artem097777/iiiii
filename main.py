from kivy.config import Config
Config.set('graphics', 'multisamples', '0')
Config.set('graphics', 'window_state', 'visible')

from kivy.core.window import Window
Window.softinput_mode = 'pan'

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color, Ellipse, Line
from kivy.clock import Clock
from math import sqrt


class AdaptiveJoystick(Widget):
    """Джойстик, появляющийся при касании экрана."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.radius = 60
        self.stick_size = 30
        self.padding = 20
        self.center_x = 0
        self.center_y = 0
        self.stick_pos = (0, 0)
        self.vector = (0, 0)
        self.active = False
        self.visible = False

        with self.canvas:
            Color(0.2, 0.2, 0.2, 0.8)
            self.bg_circle = Ellipse(pos=(0, 0), size=(1, 1))
            Color(0.5, 0.5, 0.5, 1)
            self.border = Line(width=2)
            Color(0.8, 0.2, 0.2, 1)
            self.stick = Ellipse(pos=(0, 0), size=(1, 1))

        self.update_size()
        Window.bind(on_resize=self.on_window_resize)
        self.hide()

    def on_window_resize(self, window, width, height):
        self.update_size()

    def update_size(self):
        w, h = Window.width, Window.height
        self.radius = max(40, min(80, min(w, h) * 0.08))
        self.stick_size = self.radius * 0.45
        self.padding = min(w, h) * 0.03

        self.pos = (self.padding, self.padding)
        self.center_x = self.pos[0] + self.radius
        self.center_y = self.pos[1] + self.radius
        self.size = (self.radius * 2, self.radius * 2)

        if not self.active:
            self.stick_pos = (self.center_x, self.center_y)
        self.bg_circle.pos = (self.center_x - self.radius, self.center_y - self.radius)
        self.bg_circle.size = (self.radius * 2, self.radius * 2)
        self.border.circle = (self.center_x, self.center_y, self.radius)
        self.stick.pos = (self.stick_pos[0] - self.stick_size/2,
                          self.stick_pos[1] - self.stick_size/2)
        self.stick.size = (self.stick_size, self.stick_size)

        if self.active:
            dx, dy = self.vector
            new_x = self.center_x + dx * self.radius
            new_y = self.center_y + dy * self.radius
            self.stick_pos = (new_x, new_y)
            self.stick.pos = (self.stick_pos[0] - self.stick_size/2,
                              self.stick_pos[1] - self.stick_size/2)

    def update_stick(self, touch_x, touch_y):
        dx = touch_x - self.center_x
        dy = touch_y - self.center_y
        dist = sqrt(dx*dx + dy*dy)
        if dist > self.radius:
            dx = dx / dist * self.radius
            dy = dy / dist * self.radius
        self.stick_pos = (self.center_x + dx, self.center_y + dy)
        self.vector = (dx / self.radius, dy / self.radius) if self.radius > 0 else (0, 0)
        self.stick.pos = (self.stick_pos[0] - self.stick_size/2,
                          self.stick_pos[1] - self.stick_size/2)

    def reset_stick(self):
        self.stick_pos = (self.center_x, self.center_y)
        self.vector = (0, 0)
        self.stick.pos = (self.stick_pos[0] - self.stick_size/2,
                          self.stick_pos[1] - self.stick_size/2)
        self.active = False

    def on_touch_down(self, touch):
        if not self.visible:
            return False
        dx = touch.x - self.center_x
        dy = touch.y - self.center_y
        if dx*dx + dy*dy <= self.radius*self.radius:
            self.active = True
            self.update_stick(touch.x, touch.y)
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.active and self.visible:
            self.update_stick(touch.x, touch.y)
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if self.active and self.visible:
            self.reset_stick()
            return True
        return super().on_touch_up(touch)

    def show(self):
        self.visible = True
        self.opacity = 1
        self.disabled = False

    def hide(self):
        self.visible = False
        self.opacity = 0
        self.disabled = True
        self.reset_stick()


class AdaptiveSquare(Widget):
    """Квадрат, управляемый джойстиком или клавиатурой."""
    def __init__(self, joystick, **kwargs):
        super().__init__(**kwargs)
        self.joystick = joystick
        self.size = (100, 100)
        self.pos = (0, 0)
        with self.canvas:
            Color(0, 0.8, 0.8, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)

        self.speed = 300
        
        # Поддерживаем WASD и стрелки
        self.keys = {
            'w': False, 'up': False,    # вверх
            's': False, 'down': False,  # вниз
            'a': False, 'left': False,  # влево
            'd': False, 'right': False  # вправо
        }

        Window.bind(on_key_down=self._on_key_down)
        Window.bind(on_key_up=self._on_key_up)
        Window.bind(on_resize=self.on_window_resize)

    def on_window_resize(self, window, width, height):
        self.update_size_and_position()

    def update_size_and_position(self):
        w, h = Window.width, Window.height
        new_size = max(40, min(150, min(w, h) * 0.1))
        self.size = (new_size, new_size)
        self.pos = (w/2 - new_size/2, h/2 - new_size/2)
        self.rect.pos = self.pos
        self.rect.size = self.size

    def _get_key_name(self, keycode):
        """Безопасно извлекает имя клавиши из keycode."""
        if isinstance(keycode, (list, tuple)):
            if len(keycode) > 1 and isinstance(keycode[1], str):
                return keycode[1].lower()
            elif len(keycode) > 0 and isinstance(keycode[0], str):
                return keycode[0].lower()
            else:
                return None
        elif isinstance(keycode, str):
            return keycode.lower()
        else:
            return None

    def _on_key_down(self, *args):
        """Обработчик нажатия клавиш."""
        self.joystick.hide()
        
        if len(args) >= 2:
            keycode = args[1]
            key = self._get_key_name(keycode)
            if key and key in self.keys:
                self.keys[key] = True
        
        return True

    def _on_key_up(self, *args):
        """Обработчик отпускания клавиш."""
        if len(args) >= 2:
            keycode = args[1]
            key = self._get_key_name(keycode)
            if key and key in self.keys:
                self.keys[key] = False
        
        return True

    def move_to(self, x, y):
        w, h = Window.width, Window.height
        x = max(0, min(x, w - self.width))
        y = max(0, min(y, h - self.height))
        self.pos = (x, y)
        self.rect.pos = self.pos

    def move_by_vector(self, dx, dy, dt):
        x = self.pos[0] + dx * self.speed * dt
        y = self.pos[1] + dy * self.speed * dt
        self.move_to(x, y)

    def on_touch_down(self, touch):
        self.joystick.show()
        for k in self.keys:
            self.keys[k] = False
        return super().on_touch_down(touch)


class GameWidget(Widget):
    def __init__(self, joystick, **kwargs):
        super().__init__(**kwargs)
        self.joystick = joystick

    def on_touch_down(self, touch):
        self.joystick.show()
        return super().on_touch_down(touch)


class GameApp(App):
    def build(self):
        root = GameWidget(None)

        self.joystick = AdaptiveJoystick()
        root.add_widget(self.joystick)
        root.joystick = self.joystick

        self.square = AdaptiveSquare(self.joystick)
        root.add_widget(self.square)

        self.joystick.hide()

        Clock.schedule_once(lambda dt: self.square.update_size_and_position(), 0)
        Clock.schedule_once(lambda dt: self.joystick.update_size(), 0)

        Clock.schedule_interval(self.update, 1/60)
        return root

    def update(self, dt):
        # 1. Джойстик
        joystick_vec = self.joystick.vector
        if joystick_vec != (0, 0):
            self.square.move_by_vector(joystick_vec[0], joystick_vec[1], dt)
            return

        # 2. Клавиатура (WASD + стрелки)
        keys = self.square.keys
        dx = 0
        dy = 0
        
        # Влево: A или стрелка влево
        if keys['a'] or keys['left']:
            dx -= 1
        # Вправо: D или стрелка вправо
        if keys['d'] or keys['right']:
            dx += 1
        # Вверх: W или стрелка вверх
        if keys['w'] or keys['up']:
            dy += 1
        # Вниз: S или стрелка вниз
        if keys['s'] or keys['down']:
            dy -= 1

        if dx != 0 or dy != 0:
            length = sqrt(dx*dx + dy*dy)
            if length > 0:
                dx /= length
                dy /= length
            self.square.move_by_vector(dx, dy, dt)


if __name__ == '__main__':
    GameApp().run()

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import AsyncImage, Image
from kivy.uix.popup import Popup
from kivy.uix.modalview import ModalView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line, Ellipse
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.behaviors import ButtonBehavior
from kivy.utils import platform, get_color_from_hex
from kivy.lang import Builder
from kivy.properties import ListProperty, StringProperty, BooleanProperty, NumericProperty
from kivy.uix.widget import Widget
from kivy.uix.progressbar import ProgressBar
import requests
import json
import os
import base64
from datetime import datetime

# Загружаем стили из .kv файла
Builder.load_file('blog.kv')

# Цветовая схема
PRIMARY_COLOR = get_color_from_hex("#4a6ee0")
SECONDARY_COLOR = get_color_from_hex("#6c8ce8")
ACCENT_COLOR = get_color_from_hex("#ff5252")
SUCCESS_COLOR = get_color_from_hex("#4CAF50")
LIGHT_COLOR = get_color_from_hex("#f5f7fa")
DARK_COLOR = get_color_from_hex("#2c3e50")
CARD_BG = get_color_from_hex("#ffffff")
SHADOW_COLOR = get_color_from_hex("#00000020")

Window.clearcolor = LIGHT_COLOR

# ==================== ВИДЖЕТЫ KV ====================

class ModernButton(Button):
    bg_color = ListProperty(PRIMARY_COLOR)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if 'bg_color' in kwargs:
            self.bg_color = kwargs['bg_color']

class IconButton(Button):
    bg_color = ListProperty(PRIMARY_COLOR)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class ModernTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class ModernTextArea(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class Card(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = [dp(20), dp(20)]
        self.spacing = dp(15)
        self.size_hint_y = None
        
        with self.canvas.before:
            Color(*CARD_BG)
            RoundedRectangle(
                pos=self.pos, 
                size=self.size, 
                radius=[dp(16)]
            )
            Color(*SHADOW_COLOR)
            RoundedRectangle(
                pos=(self.x - dp(2), self.y - dp(2)),
                size=(self.width + dp(4), self.height + dp(4)),
                radius=[dp(16)]
            )

class TitleLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = DARK_COLOR
        self.font_size = '20sp'
        self.bold = True
        self.size_hint_y = None
        self.height = dp(40)

class SubtitleLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = (0.6, 0.6, 0.6, 1)
        self.font_size = '14sp'
        self.size_hint_y = None
        self.height = dp(30)

class BodyText(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = (0.3, 0.3, 0.3, 1)
        self.font_size = '15sp'
        self.size_hint_y = None
        self.halign = 'left'
        self.valign = 'top'

class CaptionText(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = (0.5, 0.5, 0.5, 1)
        self.font_size = '12sp'
        self.size_hint_y = None

class ModernPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background = ''
        self.separator_height = 0
        self.overlay_color = (0, 0, 0, 0.5)

class TabButton(Button):
    active = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class FloatingActionButton(Button):
    bg_color = ListProperty(PRIMARY_COLOR)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class LoadingSpinner(Widget):
    angle = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.rotate, 0.05)
    
    def rotate(self, dt):
        self.angle = (self.angle + 5) % 360

class Divider(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(1)

# ==================== КОМПОНЕНТЫ ====================

class ClickableImage(ButtonBehavior, AsyncImage):
    pass

class PhotoCard(BoxLayout):
    def __init__(self, photo_url, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint = (None, None)
        self.size = (dp(100), dp(120))
        self.padding = [dp(5), dp(5)]
        self.spacing = dp(5)
        
        with self.canvas.before:
            Color(0.9, 0.9, 0.9, 1)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(5)])
        
        self.image = ClickableImage(
            source=photo_url,
            size_hint=(1, 0.8),
            fit_mode='contain'
        )
        self.image.bind(on_press=self.show_full_image)
        
        self.add_widget(self.image)
        
        indicator = Label(
            text='👁',
            size_hint=(1, 0.2),
            font_size='12sp',
            color=(0.5, 0.5, 0.5, 1)
        )
        self.add_widget(indicator)
        
        self.photo_url = photo_url
    
    def show_full_image(self, instance):
        full_view = FullImageView(self.photo_url)
        full_view.open()

class FullImageView(ModalView):
    def __init__(self, image_url, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.95, 0.95)
        self.background_color = (0, 0, 0, 0)
        
        layout = FloatLayout()
        
        with layout.canvas.before:
            Color(0, 0, 0, 0.95)
            Rectangle(pos=layout.pos, size=layout.size)
        
        self.image = AsyncImage(
            source=image_url,
            fit_mode='contain',
            size_hint=(0.9, 0.9),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        close_btn = Button(
            text='✕',
            font_size='24sp',
            size_hint=(None, None),
            size=(dp(40), dp(40)),
            pos_hint={'right': 0.98, 'top': 0.98},
            background_color=(0, 0, 0, 0.3),
            color=(1, 1, 1, 1)
        )
        close_btn.bind(on_press=self.dismiss)
        
        layout.add_widget(self.image)
        layout.add_widget(close_btn)
        
        self.add_widget(layout)

class CommentWidget(Card):
    def __init__(self, comment_data, **kwargs):
        super().__init__(**kwargs)
        self.height = dp(80)
        self.padding = [dp(10), dp(10)]
        self.spacing = dp(5)
        
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(25)
        )
        
        user_label = TitleLabel(
            text=comment_data['user']['username'],
            height=dp(25),
            font_size='12sp'
        )
        user_label.color = (0.3, 0.3, 0.6, 1)
        
        time_label = CaptionText(
            text=comment_data['created_at'],
            height=dp(25),
            font_size='10sp',
            halign='right'
        )
        time_label.color = (0.5, 0.5, 0.5, 1)
        
        header.add_widget(user_label)
        header.add_widget(time_label)
        
        content_label = BodyText(
            text=comment_data['content'],
            height=dp(40),
            font_size='13sp'
        )
        content_label.color = (0.2, 0.2, 0.2, 1)
        
        self.add_widget(header)
        self.add_widget(content_label)

# ==================== ЭКРАНЫ ====================

class LoginRegisterScreen(BoxLayout):
    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app = app_instance
        self.orientation = 'vertical'
        self.padding = [dp(30), dp(50)]
        self.spacing = dp(20)
        
        # Фон с градиентом
        with self.canvas.before:
            Color(*LIGHT_COLOR)
            Rectangle(pos=self.pos, size=self.size)
            Color(*PRIMARY_COLOR[:3] + [0.1])
            Ellipse(
                pos=(-self.width * 0.5, self.height * 0.6),
                size=(self.width * 2, self.height * 0.8)
            )
        
        # Заголовок
        title_box = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(120),
            spacing=dp(5)
        )
        
        with title_box.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            RoundedRectangle(
                pos=title_box.pos, 
                size=title_box.size, 
                radius=[dp(20)]
            )
        
        title = TitleLabel(
            text='📱 Мой Блог',
            color=(1, 1, 1, 1),
            font_size='28sp',
            halign='center'
        )
        subtitle = SubtitleLabel(
            text='Делитесь моментами жизни',
            color=(1, 1, 1, 0.9),
            halign='center'
        )
        
        title_box.add_widget(title)
        title_box.add_widget(subtitle)
        self.add_widget(title_box)
        
        # Карточка с формой
        form_card = Card(
            size_hint_y=None,
            height=dp(400)
        )
        
        self.tab_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            spacing=dp(2),
            padding=[dp(5), dp(5)]
        )
        
        self.login_tab = ModernButton(
            text='Вход',
            bg_color=PRIMARY_COLOR,
            on_press=self.show_login
        )
        
        self.register_tab = ModernButton(
            text='Регистрация',
            bg_color=(0.7, 0.7, 0.8, 1),
            on_press=self.show_register
        )
        
        self.tab_layout.add_widget(self.login_tab)
        self.tab_layout.add_widget(self.register_tab)
        
        # Форма
        self.form_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            padding=[dp(10), dp(20)]
        )
        
        form_card.add_widget(self.tab_layout)
        form_card.add_widget(self.form_layout)
        self.add_widget(form_card)
        
        self.show_login()
    
    def show_login(self, instance=None):
        self.login_tab.bg_color = PRIMARY_COLOR
        self.register_tab.bg_color = (0.7, 0.7, 0.8, 1)
        
        self.form_layout.clear_widgets()
        
        # Тестовые данные для удобства
        test_label = CaptionText(
            text='Тестовый пользователь: test / test123',
            height=dp(30),
            color=(0.5, 0.5, 0.5, 1),
            font_size='12sp',
            italic=True,
            halign='center'
        )
        self.form_layout.add_widget(test_label)
        
        self.username_input = ModernTextInput(
            hint_text='Имя пользователя',
            height=dp(50),
            multiline=False
        )
        self.username_input.text = 'test'
        
        self.password_input = ModernTextInput(
            hint_text='Пароль',
            height=dp(50),
            multiline=False,
            password=True
        )
        self.password_input.text = 'test123'
        
        login_btn = ModernButton(
            text='Войти',
            bg_color=PRIMARY_COLOR,
            on_press=self.login
        )
        
        self.form_layout.add_widget(self.username_input)
        self.form_layout.add_widget(self.password_input)
        self.form_layout.add_widget(login_btn)
    
    def show_register(self, instance=None):
        self.register_tab.bg_color = PRIMARY_COLOR
        self.login_tab.bg_color = (0.7, 0.7, 0.8, 1)
        
        self.form_layout.clear_widgets()
        
        self.reg_username = ModernTextInput(
            hint_text='Имя пользователя',
            height=dp(50),
            multiline=False
        )
        
        self.reg_email = ModernTextInput(
            hint_text='Email',
            height=dp(50),
            multiline=False
        )
        
        self.reg_password = ModernTextInput(
            hint_text='Пароль',
            height=dp(50),
            multiline=False,
            password=True
        )
        
        self.reg_password2 = ModernTextInput(
            hint_text='Подтвердите пароль',
            height=dp(50),
            multiline=False,
            password=True
        )
        
        register_btn = ModernButton(
            text='Зарегистрироваться',
            bg_color=PRIMARY_COLOR,
            on_press=self.register
        )
        
        self.form_layout.add_widget(self.reg_username)
        self.form_layout.add_widget(self.reg_email)
        self.form_layout.add_widget(self.reg_password)
        self.form_layout.add_widget(self.reg_password2)
        self.form_layout.add_widget(register_btn)
    
    def login(self, instance):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        
        if not username or not password:
            self.show_error('Заполните все поля')
            return
        
        self.app.login(username, password)
    
    def register(self, instance):
        username = self.reg_username.text.strip()
        email = self.reg_email.text.strip()
        password = self.reg_password.text.strip()
        password2 = self.reg_password2.text.strip()
        
        if not username or not email or not password:
            self.show_error('Заполните все поля')
            return
        
        if password != password2:
            self.show_error('Пароли не совпадают')
            return
        
        if len(password) < 6:
            self.show_error('Пароль должен быть не менее 6 символов')
            return
        
        self.app.register(username, email, password)
    
    def show_error(self, message):
        popup = ModernPopup(
            title='Ошибка',
            content=Label(
                text=message, 
                color=(0.2, 0.2, 0.2, 1),
                font_size='16sp',
                halign='center',
                valign='middle'
            ),
            size_hint=(0.8, 0.4)
        )
        popup.open()

class PostCard(Card):
    def __init__(self, post_data, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app = app_instance
        self.post_id = post_data['id']
        
        # Вычисляем высоту
        content_height = min(len(post_data['content']) * 0.7, dp(200))
        photos_height = dp(130) if post_data.get('photos') else 0
        comments_height = min(len(post_data['comments']) * dp(90), dp(270))
        self.height = dp(120) + content_height + photos_height + comments_height
        
        # Заголовок и автор
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40)
        )
        
        title_label = TitleLabel(
            text=post_data['title'],
            size_hint_x=0.7,
            height=dp(40)
        )
        
        author_label = CaptionText(
            text=f"👤 {post_data['user']['username']}",
            size_hint_x=0.3,
            height=dp(40),
            halign='right'
        )
        
        header.add_widget(title_label)
        header.add_widget(author_label)
        
        # Контент
        content_text = post_data['content']
        if len(content_text) > 150:
            content_text = content_text[:147] + '...'
        
        content_label = BodyText(
            text=content_text,
            height=content_height
        )
        
        # Фотографии если есть
        photos_widget = None
        photos = post_data.get('photos', [])
        if photos:
            photos_widget = self.create_photos_widget(photos)
        
        # Лайки и комментарии
        actions = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=dp(10)
        )
        
        # Лайк
        self.like_btn = ModernButton(
            text=f"❤️ {post_data['likes']['count']}",
            size_hint_x=0.3,
            height=dp(40),
            bg_color=(0.9, 0.3, 0.3, 0.2) if post_data['likes']['user_liked'] else (0.9, 0.9, 0.9, 1)
        )
        self.like_btn.color = (0.9, 0.3, 0.3, 1) if post_data['likes']['user_liked'] else (0.5, 0.5, 0.5, 1)
        self.like_btn.bind(on_press=lambda x: self.toggle_like())
        
        # Комментарии
        comment_btn = ModernButton(
            text=f"💬 {post_data['comments_count']}",
            size_hint_x=0.3,
            height=dp(40),
            bg_color=(0.9, 0.9, 0.9, 1)
        )
        comment_btn.bind(on_press=lambda x: self.show_comment_input())
        
        # Дата
        date_label = CaptionText(
            text=post_data['date'],
            size_hint_x=0.4,
            height=dp(40),
            halign='right'
        )
        
        actions.add_widget(self.like_btn)
        actions.add_widget(comment_btn)
        actions.add_widget(date_label)
        
        # Комментарии
        comments_widget = None
        if post_data['comments']:
            comments_widget = self.create_comments_widget(post_data['comments'])
        
        self.add_widget(header)
        self.add_widget(content_label)
        
        if photos_widget:
            self.add_widget(photos_widget)
        
        self.add_widget(actions)
        
        if comments_widget:
            self.add_widget(comments_widget)
    
    def create_photos_widget(self, photos):
        photos_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(130),
            spacing=dp(5)
        )
        
        photos_title = TitleLabel(
            text=f'📷 Фотографии ({len(photos)})',
            height=dp(25),
            font_size='14sp'
        )
        photos_title.color = (0.3, 0.3, 0.6, 1)
        photos_container.add_widget(photos_title)
        
        scroll = ScrollView(
            size_hint_y=None,
            height=dp(100),
            do_scroll_x=True,
            do_scroll_y=False
        )
        
        thumbnails = BoxLayout(
            orientation='horizontal',
            size_hint_x=None,
            spacing=dp(10),
            padding=[dp(5), 0]
        )
        thumbnails.bind(minimum_width=thumbnails.setter('width'))
        
        for photo in photos[:5]:
            if isinstance(photo, dict):
                photo_url = photo.get('url', '')
                if not photo_url.startswith('http'):
                    photo_url = f"{self.app.server_url}{photo_url}"
            else:
                photo_url = f"{self.app.server_url}/uploads/{photo}"
            
            if photo_url:
                photo_card = PhotoCard(photo_url)
                thumbnails.add_widget(photo_card)
        
        scroll.add_widget(thumbnails)
        photos_container.add_widget(scroll)
        
        return photos_container
    
    def create_comments_widget(self, comments):
        comments_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(5)
        )
        
        show_comments = comments[-3:] if len(comments) > 3 else comments
        comments_height = len(show_comments) * dp(90)
        comments_container.height = comments_height
        
        for comment in show_comments:
            comment_widget = CommentWidget(comment)
            comments_container.add_widget(comment_widget)
        
        if len(comments) > 3:
            more_label = CaptionText(
                text=f"... и ещё {len(comments) - 3} комментариев",
                height=dp(20),
                italic=True
            )
            comments_container.add_widget(more_label)
        
        return comments_container
    
    def toggle_like(self):
        if not self.app.current_user:
            self.app.show_login_required()
            return
        
        self.app.toggle_like(self.post_id, self)
    
    def show_comment_input(self):
        popup = CommentPopup(self.app, self.post_id)
        popup.open()

class CommentPopup(ModernPopup):
    def __init__(self, app_instance, post_id, **kwargs):
        super().__init__(**kwargs)
        self.title = 'Добавить комментарий'
        self.size_hint = (0.9, 0.5)
        self.app = app_instance
        self.post_id = post_id
        
        layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        
        self.comment_input = ModernTextArea(
            hint_text='Ваш комментарий...',
            height=dp(150)
        )
        layout.add_widget(self.comment_input)
        
        buttons = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10)
        )
        
        cancel_btn = ModernButton(
            text='Отмена',
            bg_color=(0.8, 0.8, 0.8, 1),
            on_press=self.dismiss
        )
        
        send_btn = ModernButton(
            text='Отправить',
            bg_color=PRIMARY_COLOR,
            on_press=self.send_comment
        )
        
        buttons.add_widget(cancel_btn)
        buttons.add_widget(send_btn)
        layout.add_widget(buttons)
        
        self.content = layout
    
    def send_comment(self, instance):
        content = self.comment_input.text.strip()
        if not content:
            self.show_error('Комментарий не может быть пустым')
            return
        
        self.app.add_comment(self.post_id, content)
        self.dismiss()
    
    def show_error(self, message):
        popup = ModernPopup(
            title='Ошибка',
            content=Label(text=message),
            size_hint=(0.8, 0.4)
        )
        popup.open()

class CreatePostPopup(ModernPopup):
    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.title = 'Создать новый пост'
        self.size_hint = (0.95, 0.9)
        self.app = app_instance
        self.selected_files = []
        
        content = Card(
            orientation='vertical',
            spacing=dp(10),
            padding=dp(20)
        )
        
        content.add_widget(TitleLabel(
            text='Новый пост',
            height=dp(40),
            font_size='20sp'
        ))
        
        self.title_input = ModernTextInput(
            hint_text='Заголовок...',
            height=dp(50),
            multiline=False
        )
        content.add_widget(self.title_input)
        
        self.content_input = ModernTextArea(
            hint_text='Текст поста...',
            height=dp(150)
        )
        content.add_widget(self.content_input)
        
        photos_buttons = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10)
        )
        
        add_photo_btn = ModernButton(
            text='📷 Добавить фото',
            size_hint_x=0.7,
            bg_color=SECONDARY_COLOR,
            on_press=self.add_photo
        )
        
        clear_photos_btn = ModernButton(
            text='🗑 Очистить',
            size_hint_x=0.3,
            bg_color=ACCENT_COLOR,
            on_press=self.clear_photos
        )
        
        photos_buttons.add_widget(add_photo_btn)
        photos_buttons.add_widget(clear_photos_btn)
        content.add_widget(photos_buttons)
        
        self.files_scroll = ScrollView(
            size_hint_y=None,
            height=dp(100)
        )
        self.files_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(5)
        )
        self.files_layout.bind(minimum_height=self.files_layout.setter('height'))
        self.files_scroll.add_widget(self.files_layout)
        content.add_widget(self.files_scroll)
        
        action_buttons = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10)
        )
        
        cancel_btn = ModernButton(
            text='Отмена',
            bg_color=(0.8, 0.8, 0.8, 1),
            on_press=self.dismiss
        )
        
        self.publish_btn = ModernButton(
            text='📤 Опубликовать',
            bg_color=SUCCESS_COLOR,
            on_press=self.publish_post
        )
        
        action_buttons.add_widget(cancel_btn)
        action_buttons.add_widget(self.publish_btn)
        content.add_widget(action_buttons)
        
        self.content = content
    
    def add_photo(self, instance):
        if platform == 'android':
            self.show_android_notice()
        else:
            self.show_file_chooser()
    
    def show_android_notice(self):
        popup = ModernPopup(
            title='Информация',
            content=Label(text='На Android используйте системный файловый менеджер'),
            size_hint=(0.8, 0.3)
        )
        popup.open()
    
    def show_file_chooser(self):
        content = BoxLayout(orientation='vertical')
        
        filechooser = FileChooserListView(
            filters=['*.png', '*.jpg', '*.jpeg', '*.gif'],
            multiselect=True
        )
        
        buttons = BoxLayout(size_hint_y=None, height=dp(50))
        select_btn = ModernButton(text='Выбрать', bg_color=SUCCESS_COLOR)
        cancel_btn = ModernButton(text='Отмена', bg_color=ACCENT_COLOR)
        
        def select_files(instance):
            for filepath in filechooser.selection:
                if filepath not in self.selected_files:
                    self.selected_files.append(filepath)
            self.update_files_list()
            chooser_popup.dismiss()
        
        select_btn.bind(on_press=select_files)
        cancel_btn.bind(on_press=lambda x: chooser_popup.dismiss())
        
        buttons.add_widget(select_btn)
        buttons.add_widget(cancel_btn)
        
        content.add_widget(filechooser)
        content.add_widget(buttons)
        
        chooser_popup = ModernPopup(
            title='Выберите фотографии',
            content=content,
            size_hint=(0.9, 0.9)
        )
        chooser_popup.open()
    
    def clear_photos(self, instance):
        self.selected_files = []
        self.update_files_list()
    
    def update_files_list(self):
        self.files_layout.clear_widgets()
        
        if not self.selected_files:
            label = Label(
                text='Фотографии не выбраны',
                color=(0.5, 0.5, 0.5, 1),
                italic=True
            )
            self.files_layout.add_widget(label)
            return
        
        for filepath in self.selected_files:
            file_item = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(30),
                padding=[dp(5), 0]
            )
            
            filename = os.path.basename(filepath)
            name_label = Label(
                text=filename[:20] + ('...' if len(filename) > 20 else ''),
                size_hint_x=0.7,
                halign='left',
                color=(0.3, 0.3, 0.3, 1)
            )
            name_label.bind(size=name_label.setter('text_size'))
            
            remove_btn = ModernButton(
                text='×',
                size_hint_x=0.3,
                font_size='16sp',
                bg_color=ACCENT_COLOR,
                on_press=lambda x, f=filepath: self.remove_file(f)
            )
            
            file_item.add_widget(name_label)
            file_item.add_widget(remove_btn)
            self.files_layout.add_widget(file_item)
    
    def remove_file(self, filepath):
        if filepath in self.selected_files:
            self.selected_files.remove(filepath)
            self.update_files_list()
    
    def publish_post(self, instance):
        if not self.app.current_user:
            self.show_error('Вы должны быть авторизованы')
            return
        
        title = self.title_input.text.strip()
        content = self.content_input.text.strip()
        
        if not title or not content:
            self.show_error('Заполните заголовок и текст')
            return
        
        self.publish_btn.disabled = True
        self.publish_btn.text = 'Отправка...'
        
        Clock.schedule_once(lambda dt: self.send_post(title, content), 0.1)
    
    def send_post(self, title, content):
        try:
            files = []
            data = {'title': title, 'content': content}
            
            if self.selected_files and platform != 'android':
                for filepath in self.selected_files:
                    if os.path.exists(filepath):
                        filename = os.path.basename(filepath)
                        files.append(('photos', (filename, open(filepath, 'rb'))))
            
            url = f'{self.app.server_url}/api/create_post'
            
            if files:
                response = self.app.session.post(url, files=files, data=data, timeout=30)
            else:
                headers = {'Content-Type': 'application/json'}
                response = self.app.session.post(url, json=data, headers=headers, timeout=30)
            
            for _, file_tuple in files:
                if len(file_tuple) > 1:
                    file_tuple[1].close()
            
            if response.status_code == 201:
                self.show_success('Пост успешно создан!')
                self.dismiss()
                self.app.load_posts()
            else:
                error_msg = response.json().get('message', 'Неизвестная ошибка')
                self.show_error(f'Ошибка: {error_msg}')
            
            self.publish_btn.disabled = False
            self.publish_btn.text = '📤 Опубликовать'
        
        except requests.exceptions.ConnectionError:
            self.show_error('Нет соединения с сервером')
            self.publish_btn.disabled = False
            self.publish_btn.text = '📤 Опубликовать'
        except Exception as e:
            self.show_error(f'Ошибка: {str(e)[:50]}')
            self.publish_btn.disabled = False
            self.publish_btn.text = '📤 Опубликовать'
    
    def show_error(self, message):
        popup = ModernPopup(
            title='Ошибка',
            content=Label(text=message),
            size_hint=(0.8, 0.4)
        )
        popup.open()
    
    def show_success(self, message):
        popup = ModernPopup(
            title='Успех',
            content=Label(text=message),
            size_hint=(0.7, 0.3)
        )
        popup.open()

# ==================== ПРИЛОЖЕНИЕ ====================

class BlogApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.server_url = 'http://192.168.0.52:5000'
        self.current_user = None
        self.session = requests.Session()
    
    def build(self):
        self.root_layout = BoxLayout(orientation='vertical')
        
        # Проверяем сохраненную сессию
        Clock.schedule_once(lambda dt: self.check_session(), 0.5)
        
        return self.root_layout
    
    def show_login_screen(self):
        self.root_layout.clear_widgets()
        self.login_screen = LoginRegisterScreen(self)
        self.root_layout.add_widget(self.login_screen)
    
    def show_main_screen(self):
        self.root_layout.clear_widgets()
        
        main_layout = FloatLayout()
        
        # Градиентный фон
        with main_layout.canvas.before:
            Color(*LIGHT_COLOR)
            Rectangle(pos=main_layout.pos, size=main_layout.size)
            Color(*PRIMARY_COLOR[:3] + [0.1])
            Ellipse(
                pos=(-main_layout.width*0.5, main_layout.height*0.7), 
                size=(main_layout.width*2, main_layout.height*0.6)
            )
        
        # Навигационная панель
        nav_bar = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(70),
            pos_hint={'top': 1},
            padding=[dp(20), dp(10)],
            spacing=dp(10)
        )
        
        with nav_bar.canvas.before:
            Color(1, 1, 1, 1)
            Rectangle(pos=nav_bar.pos, size=nav_bar.size)
            Color(0.95, 0.95, 0.95, 1)
            Rectangle(pos=(nav_bar.x, nav_bar.y), size=(nav_bar.width, dp(1)))
        
        # Заголовок
        title_box = BoxLayout(
            orientation='vertical',
            size_hint_x=0.5,
            spacing=dp(2)
        )
        
        title = TitleLabel(
            text='📱 Мой Блог',
            color=DARK_COLOR,
            font_size='20sp'
        )
        
        if self.current_user:
            subtitle = CaptionText(
                text=f'👤 {self.current_user["username"]}',
                color=(0.5, 0.5, 0.5, 1)
            )
        else:
            subtitle = CaptionText(
                text='Не авторизован',
                color=(0.7, 0.7, 0.7, 1)
            )
        
        title_box.add_widget(title)
        title_box.add_widget(subtitle)
        
        # Кнопки действий
        buttons_box = BoxLayout(
            orientation='horizontal',
            size_hint_x=0.5,
            spacing=dp(5)
        )
        
        refresh_btn = IconButton(
            text='🔄',
            bg_color=PRIMARY_COLOR,
            on_press=lambda x: self.load_posts()
        )
        
        create_btn = IconButton(
            text='➕',
            bg_color=SUCCESS_COLOR,
            on_press=self.open_create_post
        )
        
        logout_btn = IconButton(
            text='🚪',
            bg_color=ACCENT_COLOR,
            on_press=lambda x: self.logout()
        )
        
        buttons_box.add_widget(refresh_btn)
        buttons_box.add_widget(create_btn)
        buttons_box.add_widget(logout_btn)
        
        nav_bar.add_widget(title_box)
        nav_bar.add_widget(buttons_box)
        
        # Основная область с постами
        content_layout = BoxLayout(
            orientation='vertical',
            size_hint=(1, 1),
            pos_hint={'top': 0.9}
        )
        
        self.posts_container = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            size_hint_y=None,
            padding=[dp(20), dp(20), dp(20), dp(80)]
        )
        self.posts_container.bind(minimum_height=self.posts_container.setter('height'))
        
        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.posts_container)
        
        content_layout.add_widget(scroll)
        
        # Плавающая кнопка добавления
        fab = FloatingActionButton(
            text='✏️',
            bg_color=PRIMARY_COLOR,
            size_hint=(None, None),
            size=(dp(60), dp(60)),
            pos_hint={'right': 0.95, 'bottom': 0.95},
            on_press=self.open_create_post
        )
        
        # Статусная строка
        self.status_label = Label(
            text='Загружаю посты...',
            size_hint=(1, None),
            height=dp(40),
            pos_hint={'bottom': 1},
            color=(0.5, 0.5, 0.5, 1),
            font_size='12sp'
        )
        
        main_layout.add_widget(nav_bar)
        main_layout.add_widget(content_layout)
        main_layout.add_widget(fab)
        main_layout.add_widget(self.status_label)
        
        self.root_layout.add_widget(main_layout)
        
        # Загружаем посты
        Clock.schedule_once(lambda dt: self.load_posts(), 0.5)
    
    def check_session(self):
        try:
            response = self.session.get(f'{self.server_url}/api/current_user', timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('authenticated'):
                    self.current_user = data['user']
                    self.show_main_screen()
                else:
                    self.show_login_screen()
            else:
                self.show_login_screen()
        except:
            self.show_login_screen()
    
    def login(self, username, password):
        try:
            response = self.session.post(
                f'{self.server_url}/api/login',
                json={'username': username, 'password': password},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    self.current_user = data['user']
                    self.show_main_screen()
                    self.show_success('Вход выполнен успешно!')
                else:
                    self.show_error(data['message'])
            else:
                self.show_error('Ошибка сервера')
        except requests.exceptions.ConnectionError:
            self.show_error('Нет соединения с сервером')
        except Exception as e:
            self.show_error(f'Ошибка: {str(e)}')
    
    def register(self, username, email, password):
        try:
            response = self.session.post(
                f'{self.server_url}/api/register',
                json={'username': username, 'email': email, 'password': password},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    self.current_user = data['user']
                    self.show_main_screen()
                    self.show_success('Регистрация успешна!')
                else:
                    self.show_error(data['message'])
            else:
                error_data = response.json()
                self.show_error(error_data.get('message', 'Ошибка сервера'))
        except requests.exceptions.ConnectionError:
            self.show_error('Нет соединения с сервером')
        except Exception as e:
            self.show_error(f'Ошибка: {str(e)}')
    
    def logout(self):
        try:
            self.session.post(f'{self.server_url}/api/logout', timeout=5)
        except:
            pass
        
        self.current_user = None
        self.session = requests.Session()
        self.show_login_screen()
    
    def open_create_post(self, instance):
        if not self.current_user:
            self.show_login_required()
            return
        
        popup = CreatePostPopup(self)
        popup.open()
    
    def load_posts(self):
        if not hasattr(self, 'status_label'):
            return
        
        self.status_label.text = 'Загрузка...'
        self.status_label.color = (0.8, 0.4, 0, 1)
        
        try:
            response = self.session.get(f'{self.server_url}/api/posts', timeout=10)
            
            if response.status_code == 200:
                posts = response.json()
                self.posts_container.clear_widgets()
                
                if not posts:
                    empty_label = Label(
                        text='[size=18]📝 Пока нет постов[/size]\n[size=14]Создайте первый пост![/size]',
                        markup=True,
                        size_hint_y=None,
                        height=dp(150),
                        color=(0.6, 0.6, 0.6, 1),
                        halign='center'
                    )
                    empty_label.bind(size=empty_label.setter('text_size'))
                    self.posts_container.add_widget(empty_label)
                else:
                    for post in posts:
                        card = PostCard(post, self)
                        self.posts_container.add_widget(card)
                
                self.status_label.text = f'✅ Загружено {len(posts)} постов'
                self.status_label.color = (0.2, 0.6, 0.2, 1)
            else:
                self.status_label.text = f'❌ Ошибка: {response.status_code}'
                self.status_label.color = (1, 0, 0, 1)
                
        except requests.exceptions.ConnectionError:
            self.status_label.text = '❌ Нет соединения с сервером'
            self.status_label.color = (1, 0, 0, 1)
            
            retry_box = BoxLayout(
                orientation='vertical',
                size_hint_y=None,
                height=dp(100),
                spacing=dp(10)
            )
            
            error_label = Label(
                text='Не удалось подключиться к серверу',
                color=(0.8, 0.2, 0.2, 1)
            )
            
            retry_btn = ModernButton(
                text='Повторить попытку',
                bg_color=PRIMARY_COLOR,
                on_press=lambda x: self.load_posts()
            )
            
            retry_box.add_widget(error_label)
            retry_box.add_widget(retry_btn)
            self.posts_container.add_widget(retry_box)
            
        except Exception as e:
            self.status_label.text = f'❌ Ошибка: {str(e)[:30]}...'
            self.status_label.color = (1, 0, 0, 1)
    
    def toggle_like(self, post_id, post_card=None):
        if not self.current_user:
            self.show_login_required()
            return
        
        try:
            response = self.session.post(f'{self.server_url}/api/like/{post_id}', timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    self.load_posts()
                else:
                    self.show_error(data['message'])
            else:
                self.show_error('Ошибка сервера')
        except:
            self.show_error('Ошибка при установке лайка')
    
    def add_comment(self, post_id, content):
        if not self.current_user:
            self.show_login_required()
            return
        
        try:
            response = self.session.post(
                f'{self.server_url}/api/comment/{post_id}',
                json={'content': content},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    self.load_posts()
                else:
                    self.show_error(data['message'])
            else:
                self.show_error('Ошибка сервера')
        except requests.exceptions.ConnectionError:
            self.show_error('Нет соединения с сервером')
        except Exception as e:
            self.show_error(f'Ошибка: {str(e)}')
    
    def show_login_required(self):
        popup = ModernPopup(
            title='Требуется авторизация',
            content=Label(text='Для этого действия необходимо войти в систему'),
            size_hint=(0.8, 0.4)
        )
        popup.open()
    
    def show_error(self, message):
        popup = ModernPopup(
            title='Ошибка',
            content=Label(text=message),
            size_hint=(0.8, 0.4)
        )
        popup.open()
    
    def show_success(self, message):
        popup = ModernPopup(
            title='Успех',
            content=Label(text=message),
            size_hint=(0.7, 0.3)
        )
        popup.open()

if __name__ == '__main__':
    print("📱 Запуск мобильного приложения...")
    print(f"🌐 Сервер: http://192.168.0.52:5000")
    print("✨ Функции:")
    print("   - Регистрация и авторизация")
    print("   - Просмотр постов с фото")
    print("   - Создание постов с фото")
    print("   - Комментирование постов")
    print("   - Лайки постов")
    print("   - Полноэкранный просмотр фото")
    print("👤 Тестовый пользователь: test / test123")
    
    BlogApp().run()

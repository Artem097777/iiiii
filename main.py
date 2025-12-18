from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty, ListProperty, BooleanProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.dialog import MDDialog
from kivy.network.urlrequest import UrlRequest
from kivy.uix.image import AsyncImage
from kivy.clock import Clock
from kivy.storage.jsonstore import JsonStore
from datetime import datetime
import os
import requests
import json
from kivy.factory import Factory


class PostCard(MDCard):
    title = StringProperty('')
    content = StringProperty('')
    author = StringProperty('')
    image_url = StringProperty('')
    likes = NumericProperty(0)
    created_at = StringProperty('')
    comments_list = ListProperty([])
    post_id = NumericProperty(0)
    user_liked = BooleanProperty(False)
    formatted_date = StringProperty('')
    comments_count = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.format_date()
        self.comments_count = len(self.comments_list)
        Clock.schedule_once(self.update_like_button, 0.1)
    
    def format_date(self):
        if not self.created_at:
            self.formatted_date = ''
            return
        
        try:
            post_date = datetime.fromisoformat(self.created_at.replace('Z', '+00:00'))
            now = datetime.now()
            diff = now - post_date
            
            if diff.days == 0:
                if diff.seconds < 60:
                    self.formatted_date = 'сейчас'
                elif diff.seconds < 3600:
                    self.formatted_date = f'{diff.seconds // 60}м'
                else:
                    self.formatted_date = f'{diff.seconds // 3600}ч'
            elif diff.days == 1:
                self.formatted_date = 'вчера'
            elif diff.days < 7:
                self.formatted_date = f'{diff.days}д'
            elif diff.days < 30:
                self.formatted_date = f'{diff.days // 7}н'
            else:
                self.formatted_date = post_date.strftime('%d.%m')
        except:
            self.formatted_date = 'новый'
    
    def update_like_button(self, dt):
        like_button = self.ids.like_button
        if self.user_liked:
            like_button.icon = 'heart'
            like_button.text_color = (1, 0.35, 0.35, 1)
        else:
            like_button.icon = 'heart-outline'
            like_button.text_color = (0.7, 0.7, 0.7, 1)
    
    def show_comments_dialog(self):
        comments_text = ""
        for comment in self.comments_list[:5]:
            if isinstance(comment, dict):
                comments_text += f"• {comment.get('author_name', 'Аноним')}: {comment.get('text', '')}\n"
        
        if not comments_text:
            comments_text = "Пока нет комментариев"
        
        app = MDApp.get_running_app()
        if app:
            app.show_dialog("💬 Комментарии", comments_text)
    
    def like_post(self):
        app = MDApp.get_running_app()
        if app and app.current_user:
            app.like_post(self.post_id)
            self.user_liked = not self.user_liked
            self.update_like_button(0)
            self.ids.likes_count.text = str(self.likes + 1 if self.user_liked else max(0, self.likes - 1))
    
    def view_post(self):
        app = MDApp.get_running_app()
        if app:
            app.show_view_post_screen(self.post_id, {
                'title': self.title,
                'content': self.content,
                'author': self.author,
                'image_url': self.image_url,
                'likes': self.likes,
                'created_at': self.created_at,
                'comments': self.comments_list,
                'user_liked': self.user_liked
            })


class ViewPostScreen(Screen):
    full_author = StringProperty('')
    full_date = StringProperty('')
    current_post_id = NumericProperty(0)
    user_liked = BooleanProperty(False)
    
    def on_pre_enter(self):
        app = MDApp.get_running_app()
        if app:
            post_data = app.current_post_data
            if post_data:
                self.current_post_id = post_data.get('post_id', 0)
                self.full_author = post_data.get('author', 'Аноним')
                self.full_date = self.format_full_date(post_data.get('created_at', ''))
                self.user_liked = post_data.get('user_liked', False)
                
                self.ids.full_title.text = post_data.get('title', '')
                self.ids.full_content.text = post_data.get('content', '')
                self.ids.full_image.source = post_data.get('image_url', '')
                self.ids.full_likes_count.text = str(post_data.get('likes', 0))
                self.ids.full_comments_count.text = str(len(post_data.get('comments', [])))
                
                if self.user_liked:
                    self.ids.full_like_button.icon = 'heart'
                    self.ids.full_like_button.text_color = (1, 0.35, 0.35, 1)
                else:
                    self.ids.full_like_button.icon = 'heart-outline'
                    self.ids.full_like_button.text_color = (0.7, 0.7, 0.7, 1)
                
                self.display_comments(post_data.get('comments', []))
    
    def format_full_date(self, date_str):
        if not date_str:
            return ''
        try:
            post_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return post_date.strftime('%d.%m.%Y в %H:%M')
        except:
            return date_str[:16]
    
    def display_comments(self, comments):
        comments_container = self.ids.full_comments_container
        comments_container.clear_widgets()
        
        if not comments:
            label = MDLabel(
                text='Будьте первым, кто оставит комментарий!',
                font_style='Body2',
                theme_text_color='Secondary',
                halign='center',
                size_hint_y=None,
                height=40
            )
            comments_container.add_widget(label)
            return
        
        for comment in comments[-10:]:  # Последние 10 комментариев
            if isinstance(comment, dict):
                card = MDCard(
                    orientation='vertical',
                    padding=12,
                    spacing=5,
                    size_hint_y=None,
                    height=70,
                    elevation=0,
                    radius=12,
                    md_bg_color=(0.98, 0.98, 0.98, 1)
                )
                
                top_box = MDBoxLayout(size_hint_y=None, height=25)
                top_box.add_widget(MDLabel(
                    text=comment.get('author_name', 'Аноним'),
                    font_style='Subtitle2',
                    bold=True,
                    theme_text_color='Primary',
                    size_hint_x=0.7
                ))
                
                comment_time = ''
                if comment.get('created_at'):
                    try:
                        comment_date = datetime.fromisoformat(comment['created_at'].replace('Z', '+00:00'))
                        comment_time = comment_date.strftime('%H:%M')
                    except:
                        comment_time = comment['created_at'][11:16]
                
                top_box.add_widget(MDLabel(
                    text=comment_time,
                    font_style='Caption',
                    theme_text_color='Hint',
                    halign='right',
                    size_hint_x=0.3
                ))
                
                card.add_widget(top_box)
                card.add_widget(MDLabel(
                    text=comment.get('text', ''),
                    font_style='Body2',
                    theme_text_color='Secondary',
                    size_hint_y=None,
                    height=25
                ))
                
                comments_container.add_widget(card)
    
    def like_post(self):
        app = MDApp.get_running_app()
        if app and self.current_post_id:
            app.like_post(self.current_post_id)
            self.user_liked = not self.user_liked
            
            if self.user_liked:
                self.ids.full_like_button.icon = 'heart'
                self.ids.full_like_button.text_color = (1, 0.35, 0.35, 1)
                current_likes = int(self.ids.full_likes_count.text) + 1
            else:
                self.ids.full_like_button.icon = 'heart-outline'
                self.ids.full_like_button.text_color = (0.7, 0.7, 0.7, 1)
                current_likes = max(0, int(self.ids.full_likes_count.text) - 1)
            
            self.ids.full_likes_count.text = str(current_likes)
    
    def add_comment(self):
        text = self.ids.full_comment_input.text.strip()
        if text and self.current_post_id:
            app = MDApp.get_running_app()
            if app:
                app.add_comment(self.current_post_id, text)
                self.ids.full_comment_input.text = ''
                current_comments = int(self.ids.full_comments_count.text) + 1
                self.ids.full_comments_count.text = str(current_comments)


class LoginScreen(Screen):
    def login(self):
        username = self.ids.username_input.text.strip()
        password = self.ids.password_input.text.strip()
        
        if username and password:
            app = MDApp.get_running_app()
            if app:
                app.login(username, password)


class RegisterScreen(Screen):
    avatar_path = ''
    
    def register(self):
        username = self.ids.reg_username_input.text.strip()
        email = self.ids.reg_email_input.text.strip()
        password = self.ids.reg_password_input.text.strip()
        confirm_password = self.ids.reg_confirm_password_input.text.strip()
        
        if not username or not email or not password or not confirm_password:
            MDApp.get_running_app().show_dialog('⚠️ Заполните все поля', 'Все поля обязательны для заполнения')
            return
        
        if password != confirm_password:
            MDApp.get_running_app().show_dialog('⚠️ Ошибка', 'Пароли не совпадают')
            return
        
        if len(password) < 6:
            MDApp.get_running_app().show_dialog('⚠️ Ошибка', 'Пароль должен быть не менее 6 символов')
            return
        
        import re
        email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_regex, email):
            MDApp.get_running_app().show_dialog('⚠️ Ошибка', 'Введите корректный email')
            return
        
        app = MDApp.get_running_app()
        if app:
            app.register_user(username, email, password, self.avatar_path)
    
    def clear_fields(self):
        self.ids.reg_username_input.text = ''
        self.ids.reg_email_input.text = ''
        self.ids.reg_password_input.text = ''
        self.ids.reg_confirm_password_input.text = ''
        self.avatar_path = ''


class MainScreen(Screen):
    def on_enter(self):
        Clock.schedule_once(lambda dt: self.load_posts(), 0.3)
    
    def load_posts(self):
        app = MDApp.get_running_app()
        if app:
            app.load_posts()


class CreatePostScreen(Screen):
    image_path = ''
    
    def select_image(self):
        app = MDApp.get_running_app()
        if app:
            app.open_file_manager('post_image')
    
    def create_post(self):
        app = MDApp.get_running_app()
        title = self.ids.title_input.text.strip()
        content = self.ids.content_input.text.strip()
        
        if not title or not content:
            MDApp.get_running_app().show_dialog('⚠️ Заполните поля', 'Заголовок и текст поста обязательны')
            return
        
        if app:
            app.create_post(title, content, self.image_path)
    
    def clear_fields(self):
        self.ids.title_input.text = ''
        self.ids.content_input.text = ''
        self.ids.image_status.text = "Фото не выбрано"
        self.image_path = ''


Factory.register('PostCard', cls=PostCard)
Factory.register('ViewPostScreen', cls=ViewPostScreen)
Factory.register('LoginScreen', cls=LoginScreen)
Factory.register('RegisterScreen', cls=RegisterScreen)
Factory.register('MainScreen', cls=MainScreen)
Factory.register('CreatePostScreen', cls=CreatePostScreen)


KV = '''
#:import dp kivy.metrics.dp

<PostCard>:
    orientation: 'vertical'
    padding: dp(20)
    spacing: dp(15)
    size_hint: None, None
    size: dp(320), dp(320)
    elevation: 4
    radius: [dp(20),]
    md_bg_color: [1, 1, 1, 1]
    
    BoxLayout:
        size_hint_y: None
        height: dp(40)
        spacing: dp(10)
        
        MDBoxLayout:
            size_hint_x: None
            width: dp(40)
            height: dp(40)
            radius: [dp(20),]
            md_bg_color: [0.9, 0.95, 1, 1]
            pos_hint: {'center_y': 0.5}
            
            MDLabel:
                text: "👤"
                font_style: 'H6'
                halign: 'center'
                valign: 'center'
                theme_text_color: 'Primary'
        
        BoxLayout:
            orientation: 'vertical'
            size_hint_x: 0.6
            spacing: dp(2)
            
            MDLabel:
                text: root.author[:15] + ('...' if len(root.author) > 15 else '')
                font_style: 'Subtitle2'
                bold: True
                theme_text_color: 'Primary'
                halign: 'left'
            
            MDLabel:
                text: root.formatted_date
                font_style: 'Caption'
                theme_text_color: 'Hint'
                halign: 'left'
        
        Widget:
            size_hint_x: 0.4
    
    MDLabel:
        text: root.title
        font_style: 'Subtitle1'
        bold: True
        size_hint_y: None
        height: dp(40)
        theme_text_color: 'Primary'
        halign: 'left'
        shorten: True
        shorten_from: 'right'
    
    BoxLayout:
        size_hint_y: None
        height: dp(120)
        
        AsyncImage:
            source: root.image_url if root.image_url else ''
            size_hint_x: 0.4 if root.image_url else 0
            size_hint_y: 1
            radius: [dp(12),]
            allow_stretch: True
            keep_ratio: False
            opacity: 1 if root.image_url else 0
        
        MDLabel:
            text: root.content[:100] + ('...' if len(root.content) > 100 else '')
            size_hint_x: 0.6 if root.image_url else 1
            theme_text_color: 'Secondary'
            font_style: 'Body2'
            halign: 'left'
            valign: 'top'
            shorten: True
    
    BoxLayout:
        size_hint_y: None
        height: dp(40)
        spacing: dp(15)
        
        BoxLayout:
            size_hint_x: 0.5
            spacing: dp(5)
            
            MDIconButton:
                id: like_button
                icon: 'heart-outline' if not root.user_liked else 'heart'
                theme_text_color: 'Custom'
                text_color: [1, 0.35, 0.35, 1] if root.user_liked else [0.5, 0.5, 0.5, 1]
                on_release: root.like_post()
                size_hint_x: None
                width: dp(30)
            
            MDLabel:
                id: likes_count
                text: str(root.likes)
                font_style: 'Body2'
                theme_text_color: 'Secondary'
                size_hint_x: None
                width: dp(30)
        
        BoxLayout:
            size_hint_x: 0.5
            spacing: dp(5)
            
            MDIconButton:
                icon: 'comment-outline'
                theme_text_color: 'Hint'
                on_release: root.show_comments_dialog()
                size_hint_x: None
                width: dp(30)
            
            MDLabel:
                text: str(root.comments_count)
                id: comments_count
                font_style: 'Body2'
                theme_text_color: 'Secondary'
                size_hint_x: None
                width: dp(30)
        
        Widget:
            size_hint_x: 1
        
        MDIconButton:
            icon: 'arrow-right'
            theme_text_color: 'Primary'
            on_release: root.view_post()
            size_hint_x: None
            width: dp(40)

ScreenManager:
    id: screen_manager
    
    LoginScreen:
        id: login_screen
        name: 'login'
    
    RegisterScreen:
        id: register_screen
        name: 'register'
    
    MainScreen:
        id: main_screen
        name: 'main'
    
    CreatePostScreen:
        id: create_screen
        name: 'create_post'
    
    ViewPostScreen:
        id: view_post_screen
        name: 'view_post'

<LoginScreen>:
    canvas.before:
        Color:
            rgba: 0.95, 0.96, 0.98, 1
        Rectangle:
            pos: self.pos
            size: self.size
    
    FloatLayout:
        BoxLayout:
            orientation: 'vertical'
            size_hint: 0.9, 0.7
            pos_hint: {'center_x': 0.5, 'center_y': 0.5}
            spacing: dp(25)
            
            MDLabel:
                text: "👋 Добро\\nпожаловать!"
                font_style: 'H4'
                halign: 'center'
                bold: True
                size_hint_y: None
                height: self.texture_size[1]
                theme_text_color: 'Primary'
            
            BoxLayout:
                orientation: 'vertical'
                spacing: dp(20)
                size_hint_y: None
                height: dp(200)
                
                MDTextField:
                    id: username_input
                    hint_text: 'Имя пользователя'
                    mode: 'rectangle'
                    size_hint_y: None
                    height: dp(50)
                    text: 'testuser'
                
                MDTextField:
                    id: password_input
                    hint_text: 'Пароль'
                    mode: 'rectangle'
                    size_hint_y: None
                    height: dp(50)
                    text: 'test123'
                    password: True
            
            BoxLayout:
                orientation: 'vertical'
                spacing: dp(15)
                size_hint_y: None
                height: dp(120)
                
                MDRaisedButton:
                    text: 'Войти'
                    on_release: root.login()
                    size_hint: None, None
                    size: dp(200), dp(48)
                    pos_hint: {'center_x': 0.5}
                
                MDLabel:
                    text: "Ещё нет аккаунта?"
                    font_style: 'Body2'
                    halign: 'center'
                    size_hint_y: None
                    height: self.texture_size[1]
                    theme_text_color: 'Hint'
                
                MDFlatButton:
                    text: 'Создать аккаунт'
                    on_release: app.show_register_screen()
                    pos_hint: {'center_x': 0.5}
                    theme_text_color: 'Primary'

<RegisterScreen>:
    canvas.before:
        Color:
            rgba: 0.95, 0.96, 0.98, 1
        Rectangle:
            pos: self.pos
            size: self.size
    
    ScrollView:
        BoxLayout:
            orientation: 'vertical'
            size_hint: 0.9, None
            height: self.minimum_height
            padding: dp(20)
            spacing: dp(20)
            pos_hint: {'center_x': 0.5, 'top': 1}
            
            BoxLayout:
                size_hint_y: None
                height: dp(56)
                
                MDIconButton:
                    icon: 'arrow-left'
                    on_release: app.show_login_screen()
                    pos_hint: {'center_y': 0.5}
                
                MDLabel:
                    text: "Создать аккаунт"
                    font_style: 'H5'
                    halign: 'center'
                    bold: True
                    size_hint_x: 0.8
            
            BoxLayout:
                orientation: 'vertical'
                spacing: dp(15)
                size_hint_y: None
                height: dp(420)
                
                MDTextField:
                    id: reg_username_input
                    hint_text: 'Имя пользователя'
                    mode: 'rectangle'
                    size_hint_y: None
                    height: dp(50)
                
                MDTextField:
                    id: reg_email_input
                    hint_text: 'Email'
                    mode: 'rectangle'
                    size_hint_y: None
                    height: dp(50)
                
                MDTextField:
                    id: reg_password_input
                    hint_text: 'Пароль'
                    mode: 'rectangle'
                    size_hint_y: None
                    height: dp(50)
                    password: True
                
                MDTextField:
                    id: reg_confirm_password_input
                    hint_text: 'Повторите пароль'
                    mode: 'rectangle'
                    size_hint_y: None
                    height: dp(50)
                    password: True
            
            MDRaisedButton:
                text: 'Создать аккаунт'
                on_release: root.register()
                size_hint: None, None
                size: dp(200), dp(48)
                pos_hint: {'center_x': 0.5}

<MainScreen>:
    BoxLayout:
        orientation: 'vertical'
        
        MDTopAppBar:
            title: "[b]Паблик[/b]"
            elevation: 1
            md_bg_color: app.theme_cls.primary_color
            specific_text_color: 1, 1, 1, 1
            left_action_items: [['refresh', lambda x: root.load_posts()]]
            right_action_items: [['account', lambda x: app.show_profile()], ['plus', lambda x: app.show_create_screen()]]
        
        ScrollView:
            canvas.before:
                Color:
                    rgba: 0.95, 0.96, 0.98, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
            
            GridLayout:
                id: posts_grid
                cols: 2
                spacing: dp(20)
                padding: dp(20)
                size_hint_y: None
                height: self.minimum_height
                row_default_height: dp(320)
                row_force_default: True

<CreatePostScreen>:
    canvas.before:
        Color:
            rgba: 0.95, 0.96, 0.98, 1
        Rectangle:
            pos: self.pos
            size: self.size
    
    BoxLayout:
        orientation: 'vertical'
        
        MDTopAppBar:
            title: "Новый пост"
            elevation: 1
            md_bg_color: app.theme_cls.primary_color
            specific_text_color: 1, 1, 1, 1
            left_action_items: [['arrow-left', lambda x: app.show_main_screen()]]
        
        ScrollView:
            BoxLayout:
                orientation: 'vertical'
                spacing: dp(20)
                padding: dp(20)
                size_hint_y: None
                height: self.minimum_height
                
                MDTextField:
                    id: title_input
                    hint_text: 'Заголовок'
                    mode: 'rectangle'
                    size_hint_y: None
                    height: dp(50)
                
                MDTextField:
                    id: content_input
                    hint_text: 'Напишите что-нибудь...'
                    mode: 'rectangle'
                    multiline: True
                    size_hint_y: None
                    height: dp(120)
                
                MDRaisedButton:
                    text: '📷 Добавить фото'
                    on_release: root.select_image()
                    size_hint: None, None
                    size: dp(180), dp(40)
                    pos_hint: {'center_x': 0.5}
                    md_bg_color: 0.9, 0.9, 0.9, 1
                    theme_text_color: 'Primary'
                
                MDLabel:
                    id: image_status
                    text: "Фото не выбрано"
                    font_style: 'Caption'
                    halign: 'center'
                    theme_text_color: 'Hint'
                    size_hint_y: None
                    height: self.texture_size[1]
                
                Widget:
                    size_hint_y: 1
                
                MDRaisedButton:
                    text: 'Опубликовать'
                    on_release: root.create_post()
                    size_hint: None, None
                    size: dp(200), dp(48)
                    pos_hint: {'center_x': 0.5}

<ViewPostScreen>:
    canvas.before:
        Color:
            rgba: 0.95, 0.96, 0.98, 1
        Rectangle:
            pos: self.pos
            size: self.size
    
    BoxLayout:
        orientation: 'vertical'
        
        MDTopAppBar:
            title: "Публикация"
            elevation: 1
            md_bg_color: app.theme_cls.primary_color
            specific_text_color: 1, 1, 1, 1
            left_action_items: [['arrow-left', lambda x: app.show_main_screen()]]
        
        ScrollView:
            BoxLayout:
                orientation: 'vertical'
                spacing: dp(20)
                padding: dp(20)
                size_hint_y: None
                height: self.minimum_height
                
                BoxLayout:
                    orientation: 'vertical'
                    size_hint_y: None
                    height: dp(70)
                    spacing: dp(10)
                    
                    BoxLayout:
                        size_hint_y: None
                        height: dp(30)
                        spacing: dp(10)
                        
                        MDLabel:
                            text: "👤"
                            font_style: 'H5'
                            size_hint_x: None
                            width: dp(30)
                        
                        MDLabel:
                            text: root.full_author
                            font_style: 'Subtitle1'
                            bold: True
                            theme_text_color: 'Primary'
                            halign: 'left'
                        
                        Widget:
                            size_hint_x: 1
                        
                        MDLabel:
                            text: root.full_date
                            font_style: 'Caption'
                            theme_text_color: 'Hint'
                            halign: 'right'
                    
                    MDLabel:
                        id: full_title
                        text: ""
                        font_style: 'H5'
                        bold: True
                        size_hint_y: None
                        height: self.texture_size[1]
                        theme_text_color: 'Primary'
                
                AsyncImage:
                    id: full_image
                    source: ""
                    size_hint_y: None
                    height: dp(250) if self.source else 0
                    radius: dp(12)
                    allow_stretch: True
                    keep_ratio: True
                
                MDLabel:
                    id: full_content
                    text: ""
                    font_style: 'Body1'
                    size_hint_y: None
                    height: self.texture_size[1]
                    theme_text_color: 'Secondary'
                    line_height: 1.4
                
                BoxLayout:
                    size_hint_y: None
                    height: dp(50)
                    spacing: dp(20)
                    
                    BoxLayout:
                        size_hint_x: 0.5
                        spacing: dp(10)
                        
                        MDIconButton:
                            id: full_like_button
                            icon: 'heart-outline'
                            theme_text_color: 'Custom'
                            text_color: (1, 0.35, 0.35, 1) if root.user_liked else (0.7, 0.7, 0.7, 1)
                            on_release: root.like_post()
                            size_hint_x: None
                            width: dp(40)
                        
                        MDLabel:
                            id: full_likes_count
                            text: "0"
                            font_style: 'Subtitle1'
                            theme_text_color: 'Primary'
                            halign: 'left'
                    
                    BoxLayout:
                        size_hint_x: 0.5
                        spacing: dp(10)
                        
                        MDIconButton:
                            icon: 'comment-outline'
                            theme_text_color: 'Hint'
                            size_hint_x: None
                            width: dp(40)
                        
                        MDLabel:
                            id: full_comments_count
                            text: "0"
                            font_style: 'Subtitle1'
                            theme_text_color: 'Primary'
                            halign: 'left'
                
                MDLabel:
                    text: "💬 Комментарии"
                    font_style: 'Subtitle1'
                    bold: True
                    size_hint_y: None
                    height: dp(30)
                    theme_text_color: 'Primary'
                
                BoxLayout:
                    id: full_comments_container
                    orientation: 'vertical'
                    size_hint_y: None
                    height: self.minimum_height
                    spacing: dp(10)
                
                BoxLayout:
                    size_hint_y: None
                    height: dp(60)
                    spacing: dp(10)
                    
                    MDTextField:
                        id: full_comment_input
                        hint_text: 'Ваш комментарий...'
                        size_hint_x: 0.75
                        mode: 'rectangle'
                    
                    MDIconButton:
                        icon: 'send'
                        theme_text_color: 'Primary'
                        on_release: root.add_comment()
                        size_hint_x: 0.25
'''


class PublicApp(MDApp):
    API_URL = 'http://192.168.0.18:5000/api'
    BASE_URL = 'http://192.168.0.18:5000'
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_user = None
        self.store = JsonStore('user_data.json')
        self.dialog = None
        self.current_post_data = None
    
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Indigo"
        self.theme_cls.accent_palette = "Blue"
        return Builder.load_string(KV)
    
    def on_start(self):
        try:
            if self.store.exists('user'):
                self.current_user = self.store.get('user')
                self.show_main_screen()
            else:
                self.show_login_screen()
        except:
            self.show_login_screen()
    
    def show_login_screen(self):
        self.root.current = 'login'
    
    def show_register_screen(self):
        self.root.current = 'register'
    
    def show_main_screen(self):
        self.root.current = 'main'
        Clock.schedule_once(lambda dt: self.load_posts(), 0.3)
    
    def show_create_screen(self):
        if self.current_user:
            self.root.current = 'create_post'
        else:
            self.show_login_screen()
    
    def show_view_post_screen(self, post_id, post_data):
        if self.current_user:
            self.current_post_data = post_data
            self.current_post_data['post_id'] = post_id
            self.root.current = 'view_post'
        else:
            self.show_login_screen()
    
    def show_profile(self):
        if self.current_user:
            self.show_dialog("👤 Профиль", 
                           f"Имя: {self.current_user.get('username', 'Неизвестно')}\n"
                           f"Email: {self.current_user.get('email', 'Неизвестно')}")
        else:
            self.show_login_screen()
    
    def open_file_manager(self, file_type):
        from tkinter import Tk, filedialog
        Tk().withdraw()
        
        filetypes = [
            ('Изображения', '*.png *.jpg *.jpeg *.gif'),
            ('Все файлы', '*.*')
        ]
        
        file_path = filedialog.askopenfilename(
            title='Выберите файл',
            filetypes=filetypes
        )
        
        if file_path:
            self.select_file(file_path, file_type)
    
    def select_file(self, file_path, file_type):
        if not file_path:
            return
        
        file_size = os.path.getsize(file_path) / (1024 * 1024)
        if file_size > 10:
            self.show_dialog('⚠️ Ошибка', 'Файл слишком большой (максимум 10MB)')
            return
        
        allowed_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext not in allowed_extensions:
            self.show_dialog('⚠️ Ошибка', 'Неподдерживаемый формат файла')
            return
        
        if file_type == 'post_image':
            self.root.ids.create_screen.image_path = file_path
            self.root.ids.create_screen.ids.image_status.text = f"Фото: {os.path.basename(file_path)[:20]}..."
    
    def login(self, username, password):
        data = {
            'username': username,
            'password': password
        }
        
        try:
            UrlRequest(
                f'{self.API_URL}/login',
                on_success=self.handle_login_success,
                on_error=self.handle_login_error,
                req_headers={'Content-Type': 'application/json'},
                req_body=json.dumps(data),
                method='POST',
                timeout=10
            )
        except Exception as e:
            self.show_dialog('⚠️ Ошибка', f'Ошибка соединения: {str(e)}')
    
    def handle_login_success(self, req, result):
        if isinstance(result, dict) and 'error' in result:
            self.show_dialog('⚠️ Ошибка', result['error'])
        else:
            self.current_user = result
            if self.store:
                self.store.put('user', **result)
            self.show_main_screen()
            self.show_dialog('✅ Успех', 'Вход выполнен!')
    
    def handle_login_error(self, req, error):
        self.show_dialog('⚠️ Ошибка', 'Не удалось подключиться к серверу')
    
    def register_user(self, username, email, password, avatar_path=None):
        try:
            if avatar_path and os.path.exists(avatar_path):
                with open(avatar_path, 'rb') as f:
                    files = {'avatar': f}
                    data = {
                        'username': username,
                        'email': email,
                        'password': password
                    }
                    
                    response = requests.post(
                        f'{self.API_URL}/register',
                        files=files,
                        data=data,
                        timeout=10
                    )
                    
                    if response.status_code == 201:
                        result = response.json()
                        self.handle_register_success(None, result)
                    else:
                        error_data = response.json()
                        self.show_dialog('⚠️ Ошибка', error_data.get('error', 'Ошибка регистрации'))
            else:
                data = {
                    'username': username,
                    'email': email,
                    'password': password
                }
                
                UrlRequest(
                    f'{self.API_URL}/register',
                    on_success=self.handle_register_success,
                    on_error=self.handle_register_error,
                    req_headers={'Content-Type': 'application/json'},
                    req_body=json.dumps(data),
                    method='POST',
                    timeout=10
                )
                
        except Exception as e:
            self.show_dialog('⚠️ Ошибка', f'Ошибка соединения: {str(e)}')
    
    def handle_register_success(self, req, result):
        if isinstance(result, dict) and 'error' in result:
            self.show_dialog('⚠️ Ошибка', result['error'])
        else:
            self.show_dialog('✅ Успех', 'Аккаунт создан! Теперь войдите.')
            self.root.ids.register_screen.clear_fields()
            self.show_login_screen()
    
    def handle_register_error(self, req, error):
        self.show_dialog('⚠️ Ошибка', 'Ошибка при регистрации')
    
    def load_posts(self):
        if not self.current_user:
            return
        
        try:
            user_id = self.current_user.get('id', 1)
            UrlRequest(
                f'{self.API_URL}/posts?user_id={user_id}',
                on_success=self.display_posts,
                on_error=self.handle_error,
                timeout=10
            )
        except Exception as e:
            self.show_dialog('⚠️ Ошибка', f'Не удалось загрузить посты: {str(e)}')
    
    def display_posts(self, req, result):
        if not self.root or not self.current_user:
            return
        
        main_screen = self.root.ids.main_screen
        if not main_screen:
            return
        
        posts_grid = main_screen.ids.posts_grid
        posts_grid.clear_widgets()
        
        if not result or not isinstance(result, list):
            label = MDLabel(
                text='🎉 Создайте первый пост!',
                halign='center',
                theme_text_color='Secondary',
                font_style='H6'
            )
            posts_grid.add_widget(label)
            return
        
        for post in result:
            if isinstance(post, dict):
                image_url = ''
                if post.get('image_path'):
                    image_path = post.get('image_path', '')
                    if image_path.startswith('http'):
                        image_url = image_path
                    else:
                        filename = os.path.basename(image_path)
                        image_url = f"{self.BASE_URL}{image_path}"
                        if not image_path.startswith('/static'):
                            image_url = f"{self.BASE_URL}/static{image_path}"
                        if not image_path.startswith('/uploads'):
                            image_url = f"{self.BASE_URL}/static/uploads/{filename}"
                
                card = PostCard(
                    size_hint=(None, None),
                    size=(320, 320),
                    title=post.get('title', 'Без названия'),
                    content=post.get('content', ''),
                    author=post.get('author_name', 'Аноним'),
                    image_url=image_url,
                    likes=post.get('likes', 0),
                    created_at=post.get('created_at', ''),
                    post_id=post.get('id', 0),
                    comments_list=post.get('comments', []),
                    user_liked=post.get('user_liked', False)
                )
                posts_grid.add_widget(card)
        
        # Автоматически рассчитать высоту
        posts_grid.height = ((len(result) + 1) // 2) * 340 + 40
    
    def create_post(self, title, content, image_path=None):
        if not self.current_user:
            self.show_login_screen()
            return
        
        try:
            if image_path and os.path.exists(image_path):
                with open(image_path, 'rb') as f:
                    files = {'image': f}
                    data = {
                        'title': title,
                        'content': content,
                        'author_id': str(self.current_user.get('id', 1))
                    }
                    
                    response = requests.post(
                        f'{self.API_URL}/posts',
                        files=files,
                        data=data,
                        timeout=10
                    )
                    
                    if response.status_code == 201:
                        result = response.json()
                        self.handle_post_created(None, result)
                    else:
                        error_data = response.json()
                        self.show_dialog('⚠️ Ошибка', error_data.get('error', 'Ошибка при создании поста'))
            else:
                data = {
                    'title': title,
                    'content': content,
                    'author_id': self.current_user.get('id', 1)
                }
                
                UrlRequest(
                    f'{self.API_URL}/posts',
                    on_success=self.handle_post_created,
                    on_error=self.handle_error,
                    req_headers={'Content-Type': 'application/json'},
                    req_body=json.dumps(data),
                    method='POST',
                    timeout=10
                )
                
        except Exception as e:
            self.show_dialog('⚠️ Ошибка', f'Ошибка при создании поста: {str(e)}')
    
    def handle_post_created(self, req, result):
        if isinstance(result, dict) and 'error' in result:
            self.show_dialog('⚠️ Ошибка', result['error'])
        else:
            self.show_dialog('✅ Успех', 'Пост опубликован!')
            self.root.ids.create_screen.clear_fields()
            self.show_main_screen()
    
    def add_comment(self, post_id, text):
        if not self.current_user:
            self.show_login_screen()
            return
        
        data = {
            'author_id': self.current_user.get('id', 1),
            'text': text
        }
        
        try:
            UrlRequest(
                f'{self.API_URL}/posts/{post_id}/comment',
                on_success=self.handle_comment_added,
                on_error=self.handle_error,
                req_headers={'Content-Type': 'application/json'},
                req_body=json.dumps(data),
                method='POST',
                timeout=10
            )
        except Exception as e:
            self.show_dialog('⚠️ Ошибка', f'Ошибка при добавлении комментария: {str(e)}')
    
    def handle_comment_added(self, req, result):
        self.load_posts()
        if self.root.current == 'view_post':
            view_screen = self.root.ids.view_post_screen
            if view_screen and view_screen.current_post_id:
                self.load_single_post(view_screen.current_post_id)
    
    def load_single_post(self, post_id):
        try:
            user_id = self.current_user.get('id', 1) if self.current_user else 1
            UrlRequest(
                f'{self.API_URL}/posts/{post_id}?user_id={user_id}',
                on_success=self.handle_single_post_loaded,
                on_error=self.handle_error,
                timeout=10
            )
        except Exception as e:
            print(f"Ошибка при загрузке поста: {e}")
    
    def handle_single_post_loaded(self, req, result):
        if isinstance(result, dict) and 'error' not in result:
            self.current_post_data = result
            self.current_post_data['post_id'] = result.get('id', 0)
            view_screen = self.root.ids.view_post_screen
            if view_screen:
                view_screen.on_pre_enter()
    
    def like_post(self, post_id):
        if not self.current_user:
            self.show_login_screen()
            return
        
        data = {
            'user_id': self.current_user.get('id', 1)
        }
        
        try:
            UrlRequest(
                f'{self.API_URL}/posts/{post_id}/like',
                on_success=self.handle_like_added,
                on_error=self.handle_error,
                req_headers={'Content-Type': 'application/json'},
                req_body=json.dumps(data),
                method='POST',
                timeout=10
            )
        except Exception as e:
            self.show_dialog('⚠️ Ошибка', f'Ошибка при добавлении лайка: {str(e)}')
    
    def handle_like_added(self, req, result):
        self.load_posts()
        if self.root.current == 'view_post':
            view_screen = self.root.ids.view_post_screen
            if view_screen and view_screen.current_post_id:
                self.load_single_post(view_screen.current_post_id)
    
    def handle_error(self, req, error):
        self.show_dialog('⚠️ Ошибка', f'Ошибка запроса: {str(error)}')
    
    def show_dialog(self, title, text):
        if self.dialog:
            self.dialog.dismiss()
        
        self.dialog = MDDialog(
            title=f"[b]{title}[/b]",
            text=text,
            size_hint=(0.8, None),
            buttons=[
                MDRaisedButton(
                    text="OK",
                    on_release=lambda x: self.dialog.dismiss()
                )
            ]
        )
        self.dialog.open()


if __name__ == '__main__':
    from kivy.config import Config
    Config.set('graphics', 'width', '1220')
    Config.set('graphics', 'height', '2712')
    Config.set('graphics', 'resizable', '0')
    
    PublicApp().run()

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
import json
from kivy.clock import Clock
from kivy.storage.jsonstore import JsonStore
from datetime import datetime

KV = '''
ScreenManager:
    id: screen_manager
    
    LoginScreen:
        id: login_screen
        name: 'login'
    
    MainScreen:
        id: main_screen
        name: 'main'
    
    CreatePostScreen:
        id: create_screen
        name: 'create_post'
    
    PostDetailScreen:
        id: post_detail_screen
        name: 'post_detail'

<LoginScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 20
        
        MDTopAppBar:
            title: "Паблик - Вход"
            elevation: 10
        
        BoxLayout:
            orientation: 'vertical'
            spacing: 20
            size_hint_y: None
            height: 400
            pos_hint: {'center_y': 0.5}
            
            MDLabel:
                text: "Добро пожаловать!"
                font_style: 'H4'
                halign: 'center'
                size_hint_y: None
                height: self.texture_size[1]
            
            MDTextField:
                id: username_input
                hint_text: 'Имя пользователя'
                mode: 'rectangle'
                size_hint_y: None
                height: 50
                text: 'testuser'
            
            MDTextField:
                id: password_input
                hint_text: 'Пароль'
                mode: 'rectangle'
                size_hint_y: None
                height: 50
                text: 'test123'
                password: True
            
            MDRaisedButton:
                text: 'Войти'
                on_release: root.login()
                size_hint: None, None
                size: 200, 50
                pos_hint: {'center_x': 0.5}
            
            MDLabel:
                text: "Тестовый пользователь: testuser / test123"
                font_style: 'Caption'
                halign: 'center'
                theme_text_color: 'Secondary'
                size_hint_y: None
                height: self.texture_size[1]

<PostCard>:
    orientation: 'vertical'
    padding: 10
    spacing: 10
    size_hint_y: None
    height: 200
    elevation: 2
    md_bg_color: 0.95, 0.95, 0.95, 1
    radius: [10,]
    
    BoxLayout:
        size_hint_y: None
        height: 30
        spacing: 10
        
        MDLabel:
            text: root.author
            font_style: 'Subtitle1'
            theme_text_color: 'Primary'
            size_hint_x: 0.7
            bold: True
        
        MDLabel:
            text: root.formatted_date
            font_style: 'Caption'
            theme_text_color: 'Hint'
            halign: 'right'
            size_hint_x: 0.3
    
    MDLabel:
        text: root.title
        font_style: 'H6'
        size_hint_y: None
        height: self.texture_size[1]
        theme_text_color: 'Primary'
        bold: True
    
    MDLabel:
        text: root.content
        size_hint_y: None
        height: 60
        theme_text_color: 'Secondary'
        text_size: self.width - 20, None
        valign: 'top'
        shorten: True
        shorten_from: 'right'
    
    BoxLayout:
        size_hint_y: None
        height: 40
        spacing: 10
        
        MDIconButton:
            id: like_button
            icon: 'heart-outline'
            theme_text_color: 'Custom'
            text_color: 0.5, 0.5, 0.5, 1
            on_release: root.like_post()
        
        MDLabel:
            id: likes_count
            text: '0'
            font_style: 'Caption'
            theme_text_color: 'Hint'
            size_hint_x: 0.2
        
        MDIconButton:
            icon: 'comment'
            theme_text_color: 'Hint'
            on_release: root.open_post_detail()
        
        MDLabel:
            text: '0'
            id: comments_count
            font_style: 'Caption'
            theme_text_color: 'Hint'
            size_hint_x: 0.2
        
        Widget:
            size_hint_x: 0.4
        
        MDIconButton:
            icon: 'arrow-right'
            theme_text_color: 'Hint'
            on_release: root.open_post_detail()
            size_hint_x: None
            width: 40

<MainScreen>:
    BoxLayout:
        orientation: 'vertical'
        
        MDTopAppBar:
            title: "Паблик"
            elevation: 10
            left_action_items: [['refresh', lambda x: root.load_posts()]]
            right_action_items: [['account', lambda x: app.show_profile()], ['plus', lambda x: app.show_create_screen()]]
        
        ScrollView:
            MDList:
                id: posts_list
                spacing: 10

<CreatePostScreen>:
    BoxLayout:
        orientation: 'vertical'
        
        MDTopAppBar:
            title: "Новый пост"
            elevation: 10
            left_action_items: [['arrow-left', lambda x: app.show_main_screen()]]
        
        ScrollView:
            BoxLayout:
                orientation: 'vertical'
                spacing: 20
                padding: 20
                size_hint_y: None
                height: self.minimum_height
                
                MDTextField:
                    id: title_input
                    hint_text: 'Заголовок'
                    mode: 'rectangle'
                    size_hint_y: None
                    height: 50
                
                MDTextField:
                    id: content_input
                    hint_text: 'Содержание'
                    mode: 'rectangle'
                    multiline: True
                    size_hint_y: None
                    height: 150
                
                MDRaisedButton:
                    text: 'Опубликовать'
                    on_release: root.create_post()
                    size_hint: None, None
                    size: 200, 50
                    pos_hint: {'center_x': 0.5}

<PostDetailScreen>:
    BoxLayout:
        orientation: 'vertical'
        
        MDTopAppBar:
            id: detail_topbar
            title: "Детали поста"
            elevation: 10
            left_action_items: [['arrow-left', lambda x: app.show_main_screen()]]
        
        ScrollView:
            BoxLayout:
                orientation: 'vertical'
                padding: 20
                spacing: 20
                size_hint_y: None
                height: self.minimum_height
                
                BoxLayout:
                    size_hint_y: None
                    height: 40
                    
                    MDLabel:
                        id: detail_author
                        text: ""
                        font_style: 'Subtitle1'
                        bold: True
                        size_hint_x: 0.7
                    
                    MDLabel:
                        id: detail_date
                        text: ""
                        font_style: 'Caption'
                        theme_text_color: 'Hint'
                        halign: 'right'
                        size_hint_x: 0.3
                
                MDLabel:
                    id: detail_title
                    text: ""
                    font_style: 'H4'
                    theme_text_color: 'Primary'
                    size_hint_y: None
                    height: self.texture_size[1]
                
                MDLabel:
                    id: detail_content
                    text: ""
                    font_style: 'Body1'
                    theme_text_color: 'Secondary'
                    size_hint_y: None
                    height: self.texture_size[1]
                    text_size: self.width, None
                
                BoxLayout:
                    size_hint_y: None
                    height: 40
                    spacing: 20
                    
                    BoxLayout:
                        orientation: 'horizontal'
                        size_hint_x: 0.3
                        spacing: 5
                        
                        MDIconButton:
                            id: detail_like_button
                            icon: 'heart-outline'
                            theme_text_color: 'Custom'
                            text_color: 0.5, 0.5, 0.5, 1
                            on_release: root.toggle_like()
                        
                        MDLabel:
                            id: detail_likes_count
                            text: '0'
                            font_style: 'Caption'
                            theme_text_color: 'Hint'
                
                MDLabel:
                    text: "Комментарии:"
                    font_style: 'H6'
                    theme_text_color: 'Primary'
                    size_hint_y: None
                    height: 40
                
                BoxLayout:
                    id: detail_comments_list
                    orientation: 'vertical'
                    size_hint_y: None
                    height: self.minimum_height
                    spacing: 10
                
                BoxLayout:
                    size_hint_y: None
                    height: 60
                    spacing: 10
                    
                    MDTextField:
                        id: detail_comment_input
                        hint_text: 'Добавить комментарий...'
                        mode: 'fill'
                        size_hint_x: 0.7
                    
                    MDRaisedButton:
                        text: 'Отправить'
                        on_release: root.add_comment()
                        size_hint_x: 0.3
'''


class PostCard(MDCard):
    title = StringProperty('')
    content = StringProperty('')
    author = StringProperty('')
    likes = NumericProperty(0)
    created_at = StringProperty('')
    comments_list = ListProperty([])
    post_id = NumericProperty(0)
    user_liked = BooleanProperty(False)
    formatted_date = StringProperty('')
    
    def __init__(self, **kwargs):
        user_liked = kwargs.pop('user_liked', False)
        super().__init__(**kwargs)
        self.user_liked = user_liked
        self.format_date()
        Clock.schedule_once(self.update_display, 0.1)
    
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
                    self.formatted_date = 'только что'
                elif diff.seconds < 3600:
                    self.formatted_date = f'{diff.seconds // 60} мин. назад'
                else:
                    self.formatted_date = f'{diff.seconds // 3600} ч. назад'
            elif diff.days == 1:
                self.formatted_date = 'вчера'
            elif diff.days < 7:
                self.formatted_date = f'{diff.days} дн. назад'
            else:
                self.formatted_date = post_date.strftime('%d.%m.%Y')
        except:
            self.formatted_date = self.created_at[:10]
    
    def update_display(self, dt):
        # Обновляем счетчики
        self.ids.likes_count.text = str(self.likes)
        self.ids.comments_count.text = str(len(self.comments_list))
        
        # Обновляем иконку лайка
        like_button = self.ids.like_button
        if self.user_liked:
            like_button.icon = 'heart'
            like_button.text_color = (1, 0, 0, 1)
        else:
            like_button.icon = 'heart-outline'
            like_button.text_color = (0.5, 0.5, 0.5, 1)
    
    def like_post(self):
        app = MDApp.get_running_app()
        if app and app.current_user:
            app.like_post(self.post_id)
    
    def open_post_detail(self):
        app = MDApp.get_running_app()
        if app:
            app.show_post_detail(self)


class LoginScreen(Screen):
    def login(self):
        username = self.ids.username_input.text.strip()
        password = self.ids.password_input.text.strip()
        
        if username and password:
            app = MDApp.get_running_app()
            if app:
                app.login(username, password)


class MainScreen(Screen):
    def on_enter(self):
        Clock.schedule_once(lambda dt: self.load_posts(), 0.5)
    
    def load_posts(self):
        app = MDApp.get_running_app()
        if app:
            app.load_posts()


class CreatePostScreen(Screen):
    def create_post(self):
        app = MDApp.get_running_app()
        title = self.ids.title_input.text.strip()
        content = self.ids.content_input.text.strip()
        
        if title and content and app:
            app.create_post(title, content)
            self.clear_fields()
            app.show_main_screen()
    
    def clear_fields(self):
        self.ids.title_input.text = ''
        self.ids.content_input.text = ''


class PostDetailScreen(Screen):
    post_data = None
    
    def on_pre_enter(self):
        self.update_post_display()
    
    def update_post_display(self):
        if not self.post_data:
            return
        
        # Обновляем заголовок в тулбаре
        self.ids.detail_topbar.title = self.post_data.title
        
        self.ids.detail_author.text = self.post_data.author
        self.ids.detail_date.text = self.post_data.formatted_date
        self.ids.detail_title.text = self.post_data.title
        self.ids.detail_content.text = self.post_data.content
        self.ids.detail_likes_count.text = str(self.post_data.likes)
        
        # Обновляем иконку лайка
        like_button = self.ids.detail_like_button
        if self.post_data.user_liked:
            like_button.icon = 'heart'
            like_button.text_color = (1, 0, 0, 1)
        else:
            like_button.icon = 'heart-outline'
            like_button.text_color = (0.5, 0.5, 0.5, 1)
        
        # Обновляем комментарии
        self.update_comments_list()
    
    def update_comments_list(self):
        comments_list = self.ids.detail_comments_list
        comments_list.clear_widgets()
        
        if not self.post_data or not self.post_data.comments_list:
            label = MDLabel(
                text="Комментариев пока нет",
                theme_text_color='Hint',
                font_style='Caption',
                halign='center',
                size_hint_y=None,
                height=40
            )
            comments_list.add_widget(label)
            return
        
        for comment in self.post_data.comments_list:
            if isinstance(comment, dict):
                comment_card = MDBoxLayout(
                    orientation='vertical',
                    size_hint_y=None,
                    height=60,
                    padding=10,
                    spacing=5
                )
                
                # Автор и дата комментария
                author_date_box = MDBoxLayout(
                    size_hint_y=None,
                    height=20
                )
                
                author_label = MDLabel(
                    text=comment.get('author_name', 'Аноним'),
                    font_style='Caption',
                    theme_text_color='Primary',
                    bold=True,
                    size_hint_x=0.7
                )
                
                # Пытаемся получить дату комментария
                comment_date = ''
                if 'created_at' in comment:
                    try:
                        comment_datetime = datetime.fromisoformat(
                            comment['created_at'].replace('Z', '+00:00')
                        )
                        comment_date = comment_datetime.strftime('%d.%m.%Y %H:%M')
                    except:
                        comment_date = comment['created_at'][:16]
                
                date_label = MDLabel(
                    text=comment_date,
                    font_style='Caption',
                    theme_text_color='Hint',
                    halign='right',
                    size_hint_x=0.3
                )
                
                author_date_box.add_widget(author_label)
                author_date_box.add_widget(date_label)
                
                # Текст комментария
                text_label = MDLabel(
                    text=comment.get('text', ''),
                    font_style='Body2',
                    theme_text_color='Secondary',
                    size_hint_y=None,
                    height=30
                )
                
                comment_card.add_widget(author_date_box)
                comment_card.add_widget(text_label)
                comments_list.add_widget(comment_card)
    
    def toggle_like(self):
        if self.post_data:
            self.post_data.like_post()
            # Обновляем отображение через небольшой промежуток времени
            Clock.schedule_once(lambda dt: self.update_post_display(), 0.3)
    
    def add_comment(self):
        text = self.ids.detail_comment_input.text.strip()
        if text and self.post_data:
            app = MDApp.get_running_app()
            if app and app.current_user:
                app.add_comment(self.post_data.post_id, text)
                self.ids.detail_comment_input.text = ''
                # Обновляем комментарии через секунду
                Clock.schedule_once(lambda dt: self.update_comments_list(), 1.0)


class PublicApp(MDApp):
    API_URL = 'http://192.168.0.18:5000/api'
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_user = None
        self.store = JsonStore('user_data.json')
        self.dialog = None
    
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
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
    
    def show_main_screen(self):
        self.root.current = 'main'
        main_screen = self.root.ids.main_screen
        if main_screen:
            main_screen.load_posts()
    
    def show_create_screen(self):
        if self.current_user:
            self.root.current = 'create_post'
        else:
            self.show_login_screen()
    
    def show_post_detail(self, post_card):
        post_detail_screen = self.root.ids.post_detail_screen
        if post_detail_screen:
            post_detail_screen.post_data = post_card
            self.root.current = 'post_detail'
    
    def show_profile(self):
        if self.current_user:
            self.show_dialog("Профиль", 
                           f"Имя: {self.current_user.get('username', 'Неизвестно')}\n"
                           f"Email: {self.current_user.get('email', 'Неизвестно')}")
        else:
            self.show_login_screen()
    
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
            self.show_dialog('Ошибка', f'Ошибка соединения: {str(e)}')
    
    def handle_login_success(self, req, result):
        if isinstance(result, dict) and 'error' in result:
            self.show_dialog('Ошибка', result['error'])
        else:
            self.current_user = result
            if self.store:
                self.store.put('user', **result)
            self.show_main_screen()
            self.show_dialog('Успех', 'Вы успешно вошли в систему!')
    
    def handle_login_error(self, req, error):
        self.show_dialog('Ошибка', 'Не удалось подключиться к серверу')
    
    def logout(self):
        self.current_user = None
        if self.store:
            self.store.delete('user')
        self.show_login_screen()
    
    def load_posts(self):
        if not self.current_user:
            return
        
        try:
            UrlRequest(
                f'{self.API_URL}/posts',
                on_success=self.display_posts,
                on_error=self.handle_error,
                timeout=10
            )
        except Exception as e:
            print(f"Ошибка при загрузке постов: {e}")
            self.show_dialog('Ошибка', f'Не удалось загрузить посты: {str(e)}')
    
    def display_posts(self, req, result):
        if not self.root or not self.current_user:
            return
        
        main_screen = self.root.ids.main_screen
        if not main_screen:
            return
        
        posts_list = main_screen.ids.posts_list
        posts_list.clear_widgets()
        
        if not result or not isinstance(result, list):
            label = MDLabel(
                text='Нет постов. Создайте первый!',
                halign='center',
                theme_text_color='Secondary'
            )
            posts_list.add_widget(label)
            return
        
        for post in result:
            if isinstance(post, dict):
                user_liked = False
                if 'liked_by' in post and isinstance(post['liked_by'], list):
                    user_liked = any(
                        user.get('id') == self.current_user.get('id') 
                        for user in post['liked_by']
                    )
                
                card = PostCard(
                    size_hint_y=None,
                    height=200,
                    title=post.get('title', 'Без названия'),
                    content=post.get('content', ''),
                    author=post.get('author_name', 'Аноним'),
                    likes=post.get('likes', 0),
                    created_at=post.get('created_at', ''),
                    post_id=post.get('id', 0),
                    comments_list=post.get('comments', []),
                    user_liked=user_liked
                )
                posts_list.add_widget(card)
    
    def create_post(self, title, content):
        if not self.current_user:
            self.show_login_screen()
            return
        
        data = {
            'title': title,
            'content': content,
            'author_id': self.current_user.get('id', 1)
        }
        
        try:
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
            self.show_dialog('Ошибка', f'Ошибка при создании поста: {str(e)}')
    
    def handle_post_created(self, req, result):
        if isinstance(result, dict) and 'error' in result:
            self.show_dialog('Ошибка', result['error'])
        else:
            self.show_dialog('Успех', 'Пост создан успешно!')
            self.load_posts()
    
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
            self.show_dialog('Ошибка', f'Ошибка при добавлении комментария: {str(e)}')
    
    def handle_comment_added(self, req, result):
        # Перезагружаем посты для обновления данных
        self.load_posts()
    
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
            print(f"Ошибка при добавлении лайка: {e}")
            self.show_dialog('Ошибка', f'Ошибка при добавлении лайка: {str(e)}')
    
    def handle_like_added(self, req, result):
        self.load_posts()
    
    def handle_error(self, req, error):
        print(f"Ошибка запроса: {error}")
        self.show_dialog('Ошибка', f'Ошибка запроса: {str(error)}')
    
    def show_dialog(self, title, text):
        if self.dialog:
            self.dialog.dismiss()
        
        self.dialog = MDDialog(
            title=title,
            text=text,
            size_hint=(0.8, None),
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=lambda x: self.dialog.dismiss()
                )
            ]
        )
        self.dialog.open()


if __name__ == '__main__':
    PublicApp().run()

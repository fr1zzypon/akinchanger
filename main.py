# ============================================
# SKIN CHANGER - БЕЗ БАЗЫ
# Только замена ID. База пустая.
# ============================================

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.config import Config
from kivy.utils import platform
import json
import os

# === НАСТРОЙКИ ОКНА ===
Config.set('graphics', 'width', '450')
Config.set('graphics', 'height', '500')
Config.set('graphics', 'resizable', False)

# === ЗАПРОС РАЗРЕШЕНИЙ ДЛЯ ANDROID ===
def request_android_permissions():
    """Запрос разрешения на поверх других окон"""
    if platform == 'android':
        try:
            from android.permissions import request_permissions, Permission, check_permission
            if not check_permission(Permission.SYSTEM_ALERT_WINDOW):
                request_permissions([Permission.SYSTEM_ALERT_WINDOW])
                
                from kivy.uix.popup import Popup
                from kivy.uix.label import Label
                from kivy.uix.button import Button
                from kivy.uix.boxlayout import BoxLayout
                
                content = BoxLayout(orientation='vertical', padding=20, spacing=15)
                content.add_widget(
                    Label(
                        text='📱 Разрешение на поверх других окон\n\n'
                             'Для работы поверх других приложений '
                             'необходимо разрешение.\n\n'
                             'Нажмите "ОТКРЫТЬ НАСТРОЙКИ" и включите '
                             '"Разрешить поверх других окон" для этого приложения.',
                        font_size=15,
                        color=(1, 1, 1, 1),
                        halign='center'
                    )
                )
                
                btn_box = BoxLayout(spacing=10, size_hint=(1, 0.3))
                
                def open_settings(btn):
                    try:
                        from android import mActivity
                        import android
                        mActivity.startActivity(
                            android.content.Intent(
                                android.provider.Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                                android.net.Uri.parse('package:' + mActivity.getPackageName())
                            )
                        )
                    except:
                        import os
                        os.system('am start -a android.settings.ACTION_MANAGE_OVERLAY_PERMISSION')
                    popup.dismiss()
                
                def close_popup(btn):
                    popup.dismiss()
                
                settings_btn = Button(
                    text='⚙️ ОТКРЫТЬ НАСТРОЙКИ',
                    font_size=15,
                    bold=True,
                    background_color=(0, 0.6, 0.8, 1),
                    color=(1, 1, 1, 1)
                )
                settings_btn.bind(on_press=open_settings)
                
                close_btn = Button(
                    text='ЗАКРЫТЬ',
                    font_size=15,
                    bold=True,
                    background_color=(0.5, 0.2, 0.2, 1),
                    color=(1, 1, 1, 1)
                )
                close_btn.bind(on_press=close_popup)
                
                btn_box.add_widget(settings_btn)
                btn_box.add_widget(close_btn)
                content.add_widget(btn_box)
                
                popup = Popup(
                    title='⚠️ РАЗРЕШЕНИЕ',
                    content=content,
                    size_hint=(0.9, 0.5),
                    background_color=(0.04, 0.04, 0.12, 1),
                    auto_dismiss=False
                )
                popup.open()
                
        except Exception as e:
            print(f'Permission error: {e}')

# === ОСНОВНОЕ ПРИЛОЖЕНИЕ ===
class SkinChangerApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.skins = {}  # ПУСТАЯ БАЗА
        self.changes_log = []
        self.title = 'Skin Changer'
    
    def build(self):
        # === ЗАПРОС РАЗРЕШЕНИЙ ===
        request_android_permissions()
        
        # Настройка окна
        Window.clearcolor = (0.04, 0.04, 0.12, 1)
        
        # Делаем окно поверх всех (если разрешено)
        try:
            Window.attributes.topmost = True
        except:
            pass
        
        # === ОСНОВНОЙ КОНТЕЙНЕР ===
        root = BoxLayout(
            orientation='vertical',
            padding=20,
            spacing=12
        )
        
        # === ВЕРХНЯЯ ПАНЕЛЬ ===
        top_panel = BoxLayout(
            size_hint=(1, 0.07),
            spacing=10
        )
        
        title = Label(
            text='SKIN CHANGER',
            font_size=28,
            bold=True,
            color=(0, 0.85, 1, 1),
            size_hint=(0.7, 1),
            halign='left'
        )
        title.bind(size=title.setter('text_size'))
        top_panel.add_widget(title)
        
        self.permission_status = Label(
            text='🔴',
            font_size=20,
            size_hint=(0.15, 1),
            halign='center'
        )
        top_panel.add_widget(self.permission_status)
        
        perm_check_btn = Button(
            text='🔍',
            font_size=16,
            size_hint=(0.15, 1),
            background_color=(0.2, 0.2, 0.3, 1),
            color=(1, 1, 1, 1)
        )
        perm_check_btn.bind(on_press=self.check_permission_status)
        top_panel.add_widget(perm_check_btn)
        
        root.add_widget(top_panel)
        
        # === СТАТУС ===
        self.status = Label(
            text='Skins: 0 | Changes: 0',
            font_size=14,
            color=(0.5, 0.5, 0.5, 1),
            size_hint=(1, 0.05)
        )
        root.add_widget(self.status)
        
        # === ОТСТУП ===
        spacer = BoxLayout(size_hint=(1, 0.02))
        root.add_widget(spacer)
        
        # === ПОЛЯ ВВОДА ===
        input_box = BoxLayout(
            orientation='vertical',
            size_hint=(1, 0.30),
            spacing=8
        )
        
        # OLD ID
        old_label = Label(
            text='OLD ID',
            font_size=16,
            bold=True,
            color=(1, 0.4, 0.4, 1),
            size_hint=(1, 0.15),
            halign='left'
        )
        old_label.bind(size=old_label.setter('text_size'))
        input_box.add_widget(old_label)
        
        self.old_input = TextInput(
            hint_text='Enter old ID',
            font_size=20,
            multiline=False,
            size_hint=(1, 0.32),
            background_color=(0.1, 0.1, 0.22, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(0, 0.85, 1, 1),
            padding=(15, 12)
        )
        self.old_input.bind(on_text_validate=self.on_enter)
        input_box.add_widget(self.old_input)
        
        # NEW ID
        new_label = Label(
            text='NEW ID',
            font_size=16,
            bold=True,
            color=(0.3, 0.9, 0.4, 1),
            size_hint=(1, 0.15),
            halign='left'
        )
        new_label.bind(size=new_label.setter('text_size'))
        input_box.add_widget(new_label)
        
        self.new_input = TextInput(
            hint_text='Enter new ID',
            font_size=20,
            multiline=False,
            size_hint=(1, 0.32),
            background_color=(0.1, 0.1, 0.22, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(0, 0.85, 1, 1),
            padding=(15, 12)
        )
        self.new_input.bind(on_text_validate=self.on_enter)
        input_box.add_widget(self.new_input)
        
        root.add_widget(input_box)
        
        # === ОТСТУП ===
        spacer2 = BoxLayout(size_hint=(1, 0.02))
        root.add_widget(spacer2)
        
        # === КНОПКИ ===
        btn_grid = GridLayout(
            cols=3,
            size_hint=(1, 0.12),
            spacing=10
        )
        
        replace_btn = Button(
            text='REPLACE',
            font_size=22,
            bold=True,
            background_color=(0, 0.75, 0.25, 1),
            color=(1, 1, 1, 1)
        )
        replace_btn.bind(on_press=self.replace_skin)
        btn_grid.add_widget(replace_btn)
        
        reset_btn = Button(
            text='RESET',
            font_size=18,
            bold=True,
            background_color=(0.7, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        reset_btn.bind(on_press=self.reset_changes)
        btn_grid.add_widget(reset_btn)
        
        clear_btn = Button(
            text='CLEAR',
            font_size=18,
            bold=True,
            background_color=(0.3, 0.3, 0.3, 1),
            color=(1, 1, 1, 1)
        )
        clear_btn.bind(on_press=self.clear_fields)
        btn_grid.add_widget(clear_btn)
        
        root.add_widget(btn_grid)
        
        # === ИНФОРМАЦИОННАЯ СТРОКА ===
        self.info = Label(
            text='Enter ID and press REPLACE',
            font_size=15,
            color=(0.6, 0.6, 0.6, 1),
            size_hint=(1, 0.05)
        )
        root.add_widget(self.info)
        
        # === ИСТОРИЯ ===
        history_label = Label(
            text='HISTORY',
            font_size=14,
            bold=True,
            color=(0, 0.85, 1, 1),
            size_hint=(1, 0.04)
        )
        root.add_widget(history_label)
        
        self.scroll = ScrollView(
            size_hint=(1, 0.25),
            do_scroll_x=False,
            bar_width=4,
            bar_color=(0, 0.85, 1, 0.3)
        )
        
        self.history_container = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            spacing=2
        )
        self.history_container.bind(minimum_height=self.history_container.setter('height'))
        
        self.scroll.add_widget(self.history_container)
        root.add_widget(self.scroll)
        
        # === НИЖНЯЯ ПАНЕЛЬ ===
        bottom_grid = GridLayout(
            cols=3,
            size_hint=(1, 0.07),
            spacing=8
        )
        
        add_btn = Button(
            text='ADD',
            font_size=14,
            bold=True,
            background_color=(0.15, 0.5, 0.8, 1),
            color=(1, 1, 1, 1)
        )
        add_btn.bind(on_press=self.show_add_popup)
        bottom_grid.add_widget(add_btn)
        
        history_btn = Button(
            text='HISTORY',
            font_size=13,
            bold=True,
            background_color=(0.4, 0.15, 0.6, 1),
            color=(1, 1, 1, 1)
        )
        history_btn.bind(on_press=self.show_full_history)
        bottom_grid.add_widget(history_btn)
        
        export_btn = Button(
            text='SAVE',
            font_size=14,
            bold=True,
            background_color=(0.2, 0.6, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        export_btn.bind(on_press=self.export_history)
        bottom_grid.add_widget(export_btn)
        
        root.add_widget(bottom_grid)
        
        self.update_history()
        self.check_permission_status(None)
        
        return root
    
    def check_permission_status(self, instance):
        """Проверка статуса разрешения"""
        if platform == 'android':
            try:
                from android.permissions import check_permission, Permission
                if check_permission(Permission.SYSTEM_ALERT_WINDOW):
                    self.permission_status.text = '🟢'
                    self.permission_status.color = (0, 1, 0, 1)
                else:
                    self.permission_status.text = '🔴'
                    self.permission_status.color = (1, 0, 0, 1)
                    self.show_permission_request()
            except:
                self.permission_status.text = '❓'
        else:
            self.permission_status.text = '✅'
            self.permission_status.color = (0, 1, 0, 1)
    
    def show_permission_request(self):
        """Показать запрос разрешения"""
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        content.add_widget(
            Label(
                text='📱 Разрешение на поверх других окон\n\n'
                     'Для работы поверх других приложений\n'
                     'необходимо включить разрешение.',
                font_size=16,
                color=(1, 1, 1, 1),
                halign='center'
            )
        )
        
        btn_box = BoxLayout(spacing=10, size_hint=(1, 0.3))
        
        def open_settings(btn):
            try:
                from android import mActivity
                import android
                mActivity.startActivity(
                    android.content.Intent(
                        android.provider.Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                        android.net.Uri.parse('package:' + mActivity.getPackageName())
                    )
                )
            except:
                import os
                os.system('am start -a android.settings.ACTION_MANAGE_OVERLAY_PERMISSION')
            popup.dismiss()
        
        def refresh_status(btn):
            self.check_permission_status(None)
            popup.dismiss()
        
        settings_btn = Button(
            text='⚙️ НАСТРОЙКИ',
            font_size=15,
            bold=True,
            background_color=(0, 0.6, 0.8, 1),
            color=(1, 1, 1, 1)
        )
        settings_btn.bind(on_press=open_settings)
        
        refresh_btn = Button(
            text='🔄 ПРОВЕРИТЬ',
            font_size=15,
            bold=True,
            background_color=(0.3, 0.3, 0.3, 1),
            color=(1, 1, 1, 1)
        )
        refresh_btn.bind(on_press=refresh_status)
        
        close_btn = Button(
            text='ЗАКРЫТЬ',
            font_size=15,
            bold=True,
            background_color=(0.5, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        
        popup = Popup(
            title='⚠️ РАЗРЕШЕНИЕ',
            content=content,
            size_hint=(0.9, 0.4),
            background_color=(0.04, 0.04, 0.12, 1),
            auto_dismiss=False
        )
        close_btn.bind(on_press=popup.dismiss)
        
        btn_box.add_widget(settings_btn)
        btn_box.add_widget(refresh_btn)
        btn_box.add_widget(close_btn)
        content.add_widget(btn_box)
        
        popup.open()
    
    def on_enter(self, instance):
        """Обработка Enter"""
        self.replace_skin(None)
    
    def replace_skin(self, instance):
        """ЗАМЕНА ID СКИНА"""
        old_text = self.old_input.text.strip()
        new_text = self.new_input.text.strip()
        
        if not old_text or not new_text:
            self.show_info('ERROR: Fill both fields!', (1, 0.3, 0.3, 1))
            return
        
        try:
            old_id = int(old_text)
            new_id = int(new_text)
        except ValueError:
            self.show_info('ERROR: Enter numbers only!', (1, 0.3, 0.3, 1))
            return
        
        if old_id == new_id:
            self.show_info('WARNING: IDs are the same!', (1, 0.8, 0.2, 1))
            return
        
        # Проверяем есть ли старый ID в базе
        if old_id not in self.skins:
            self.show_info(f'⚠️ Скин с ID {old_id} не найден!', (1, 0.8, 0.2, 1))
            return
        
        old_name = self.skins[old_id]
        
        # Проверка занятости нового ID
        old_new_skin = None
        if new_id in self.skins:
            old_new_skin = self.skins[new_id]
        
        # ВЫПОЛНЯЕМ ЗАМЕНУ
        self.skins[new_id] = old_name
        del self.skins[old_id]
        
        # Сохраняем в историю
        self.changes_log.append({
            'old_id': old_id,
            'new_id': new_id,
            'skin_name': old_name,
            'replaced_skin': old_new_skin
        })
        
        self.old_input.text = ''
        self.new_input.text = ''
        
        self.update_history()
        self.update_status()
        
        self.show_info(f'✅ {old_name} → ID {new_id}', (0, 0.8, 0.3, 1))
        self.show_result_popup(old_name, old_id, new_id)
    
    def show_result_popup(self, name, old_id, new_id):
        """Показать результат замены"""
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        result_label = Label(
            text=f'✅ REPLACE SUCCESSFUL!\n\n{name}\n{old_id} → {new_id}',
            font_size=16,
            color=(1, 1, 1, 1),
            halign='center'
        )
        result_label.bind(size=result_label.setter('text_size'))
        content.add_widget(result_label)
        
        close_btn = Button(
            text='OK',
            font_size=18,
            bold=True,
            size_hint=(1, 0.3),
            background_color=(0, 0.75, 0.25, 1),
            color=(1, 1, 1, 1)
        )
        
        popup = Popup(
            title='SUCCESS',
            content=content,
            size_hint=(0.8, 0.4),
            background_color=(0.04, 0.04, 0.12, 1)
        )
        close_btn.bind(on_press=popup.dismiss)
        content.add_widget(close_btn)
        popup.open()
    
    def reset_changes(self, instance):
        """Сброс всех изменений"""
        if not self.changes_log:
            self.show_info('No changes to reset', (0.5, 0.5, 0.5, 1))
            return
        
        for change in reversed(self.changes_log):
            old_id = change['old_id']
            new_id = change['new_id']
            skin_name = change['skin_name']
            replaced_skin = change.get('replaced_skin')
            
            self.skins[old_id] = skin_name
            del self.skins[new_id]
            
            if replaced_skin:
                self.skins[new_id] = replaced_skin
        
        self.changes_log.clear()
        self.update_history()
        self.update_status()
        self.show_info('✅ All changes undone!', (0, 0.8, 0.3, 1))
    
    def clear_fields(self, instance):
        """Очистить поля"""
        self.old_input.text = ''
        self.new_input.text = ''
        self.show_info('Fields cleared', (0.5, 0.5, 0.5, 1))
    
    def show_add_popup(self, instance):
        """Попап для добавления скина"""
        content = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        content.add_widget(Label(text='ADD NEW SKIN', font_size=18, bold=True, color=(0, 0.85, 1, 1)))
        
        id_input = TextInput(
            hint_text='Enter ID',
            font_size=16,
            multiline=False,
            background_color=(0.1, 0.1, 0.22, 1),
            foreground_color=(1, 1, 1, 1),
            padding=(15, 10)
        )
        content.add_widget(id_input)
        
        name_input = TextInput(
            hint_text='Enter skin name',
            font_size=16,
            multiline=False,
            background_color=(0.1, 0.1, 0.22, 1),
            foreground_color=(1, 1, 1, 1),
            padding=(15, 10)
        )
        content.add_widget(name_input)
        
        btn_box = BoxLayout(spacing=10, size_hint=(1, 0.3))
        
        add_btn = Button(
            text='ADD',
            font_size=16,
            bold=True,
            background_color=(0, 0.75, 0.25, 1),
            color=(1, 1, 1, 1)
        )
        cancel_btn = Button(
            text='CANCEL',
            font_size=16,
            bold=True,
            background_color=(0.5, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        
        popup = Popup(
            title='ADD SKIN',
            content=content,
            size_hint=(0.85, 0.45),
            background_color=(0.04, 0.04, 0.12, 1)
        )
        
        def do_add(btn):
            sid = id_input.text.strip()
            name = name_input.text.strip()
            if not sid or not name:
                self.show_info('Fill both fields!', (1, 0.3, 0.3, 1))
                return
            try:
                skin_id = int(sid)
                if skin_id in self.skins:
                    self.show_info(f'ID {skin_id} already exists!', (1, 0.8, 0.2, 1))
                    return
                self.skins[skin_id] = name
                self.update_history()
                self.update_status()
                self.show_info(f'Added: {skin_id} - {name}', (0, 0.8, 0.3, 1))
                popup.dismiss()
            except ValueError:
                self.show_info('ID must be a number!', (1, 0.3, 0.3, 1))
        
        add_btn.bind(on_press=do_add)
        cancel_btn.bind(on_press=popup.dismiss)
        
        btn_box.add_widget(add_btn)
        btn_box.add_widget(cancel_btn)
        content.add_widget(btn_box)
        
        popup.open()
    
    def show_full_history(self, instance):
        """Показать всю историю"""
        if not self.changes_log:
            self.show_info('History is empty', (0.5, 0.5, 0.5, 1))
            return
        
        content = BoxLayout(orientation='vertical', padding=15, spacing=5)
        
        history_text = '\n'.join([
            f'{i+1}. {c["skin_name"]} ({c["old_id"]} → {c["new_id"]})'
            for i, c in enumerate(self.changes_log)
        ])
        
        label = Label(
            text=f'History ({len(self.changes_log)} changes):\n\n{history_text}',
            font_size=14,
            color=(1, 1, 1, 1),
            halign='center'
        )
        label.bind(size=label.setter('text_size'))
        content.add_widget(label)
        
        close_btn = Button(
            text='OK',
            font_size=16,
            bold=True,
            size_hint=(1, 0.12),
            background_color=(0.3, 0.3, 0.3, 1),
            color=(1, 1, 1, 1)
        )
        
        popup = Popup(
            title='HISTORY',
            content=content,
            size_hint=(0.85, 0.6),
            background_color=(0.04, 0.04, 0.12, 1)
        )
        close_btn.bind(on_press=popup.dismiss)
        content.add_widget(close_btn)
        popup.open()
    
    def export_history(self, instance):
        """Экспорт истории в JSON"""
        try:
            data = {
                'skins': {str(k): v for k, v in self.skins.items()},
                'history': self.changes_log
            }
            with open('skins_data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.show_info(f'Saved {len(self.skins)} skins, {len(self.changes_log)} changes', (0, 0.8, 0.3, 1))
        except Exception as e:
            self.show_info(f'Error: {e}', (1, 0.3, 0.3, 1))
    
    def update_history(self):
        """Обновление списка истории"""
        self.history_container.clear_widgets()
        
        if not self.changes_log:
            empty = Label(
                text='No changes yet',
                font_size=14,
                color=(0.3, 0.3, 0.3, 1),
                size_hint=(1, 1)
            )
            self.history_container.add_widget(empty)
            return
        
        # Показываем последние 10 записей
        for change in reversed(self.changes_log[-10:]):
            item = BoxLayout(
                size_hint=(1, None),
                height=28,
                spacing=5,
                padding=(5, 2)
            )
            
            text = f'{change["skin_name"][:20]} {change["old_id"]}→{change["new_id"]}'
            label = Label(
                text=text,
                font_size=12,
                color=(0.8, 0.8, 0.8, 1),
                size_hint=(1, 1),
                halign='left'
            )
            label.bind(size=label.setter('text_size'))
            item.add_widget(label)
            
            self.history_container.add_widget(item)
    
    def show_info(self, text, color):
        self.info.text = text
        self.info.color = color
    
    def update_status(self):
        self.status.text = f'Skins: {len(self.skins)} | Changes: {len(self.changes_log)}'

# === ЗАПУСК ===
if __name__ == '__main__':
    SkinChangerApp().run()
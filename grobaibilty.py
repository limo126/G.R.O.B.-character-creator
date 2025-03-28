
from kivy.app import App
from kivy.core.image import Image as CoreImage
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Line
from kivy.graphics import Fbo, ClearColor, ClearBuffers, Scale, Translate
from kivy.graphics.texture import Texture
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.switch import Switch
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
import os
import re
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
import os


def save_data(self, key, value):
    """Сохраняет данные в глобальный словарь"""
    app = App.get_running_app()
    app.user_data[key] = value


# Цвет фона
BG_COLOR = (53 / 255, 59 / 255, 79 / 255, 1)  # #606E8C

class ThemedScreenManager(ScreenManager):
    """ScreenManager с цветным фоном (убирает мигание черного экрана)"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(*BG_COLOR)  # Устанавливаем цвет фона ScreenManager
            self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self.update_rect, pos=self.update_rect)

    def update_rect(self, *args):
        """Обновляет фон при изменении размера окна"""
        self.rect.size = self.size
        self.rect.pos = self.pos


class ThemedScreen(Screen):
    """Экран с изменённым фоном"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(*BG_COLOR)  # Цвет фона
            self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self.update_rect, pos=self.update_rect)

    def update_rect(self, *args):
        """Обновляет фон при изменении размера"""
        self.rect.size = self.size
        self.rect.pos = self.pos




class AbilityCreationScreen(ThemedScreen):
    """Экран ввода названия и описания способности"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_data = {}
        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        self.label_name = Label(text="Название способности:")
        self.entry_name = TextInput(multiline=False)

        self.label_description = Label(text="Описание способности:")
        self.entry_description = TextInput(multiline=True)

        self.button_next = Button(text="Далее", on_press=self.next_screen)

        layout.add_widget(self.label_name)
        layout.add_widget(self.entry_name)
        layout.add_widget(self.label_description)
        layout.add_widget(self.entry_description)
        layout.add_widget(self.button_next)

        self.add_widget(layout)


    def on_pre_leave(self):
        """Сохраняем название и описание способности"""
        app = App.get_running_app()
        if not hasattr(app, "user_data"):
            app.user_data = {}

        app.user_data["entry_name"] = self.entry_name.text
        app.user_data["entry_description"] = self.entry_description.text
        """Очистка полей ввода при уходе с экрана"""
        self.entry_name.text = ""
        self.entry_description.text = ""

    def next_screen(self, instance):
        """Сохраняем данные и переходим к выбору типа действия"""
        self.manager.get_screen("action").entry_name = self.entry_name.text
        self.manager.get_screen("action").entry_description = self.entry_description.text
        self.manager.current = "action"

class AbilityApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_data = {}  # Добавляем глобальное хранилище данных

    def build(self):
        sm = ScreenManager()
        sm.add_widget(AbilityCreationScreen(name="creation"))
        sm.add_widget(ActionSelectionScreen(name="action"))
        return sm


class ActionSelectionScreen(ThemedScreen):
    """Экран выбора типа действия"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.entry_name = ""
        self.entry_description = ""
        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        self.label_action_type = Label(text="Выберите тип действия:")
        self.spinner_action_type = Spinner(
            text="Выберите",
            values=[
                "Действие",
                "Бонусное действие",
                "Ответное действие",
                "Свободное действие",
            ],
        )

        self.button_next = Button(text="Далее", on_press=self.next_screen)

        layout.add_widget(self.label_action_type)
        layout.add_widget(self.spinner_action_type)
        layout.add_widget(self.button_next)

        self.add_widget(layout)

    def save_data(self, key, value):
        """Сохраняет данные в глобальный словарь"""
        app = App.get_running_app()
        data = app.user_data

    def on_pre_leave(self):
        """Сохраняем выбранный тип действия"""
        app = App.get_running_app()
        if not hasattr(app, "user_data"):
            app.user_data = {}
        app.user_data["spinner_action_type"] = self.spinner_action_type.text

    def next_screen(self, instance):
        """Сохраняем выбор и переходим к области действия"""
        self.manager.get_screen("target").entry_name = self.entry_name
        self.manager.get_screen("target").entry_description = self.entry_description
        self.manager.get_screen("target").action_type = self.spinner_action_type.text
        self.manager.current = "target"
        """Очистка spinner при уходе с экрана"""
        self.spinner_action_type.text = "Выберите"


class TargetSelectionScreen(ThemedScreen):
    """Экран выбора области действия с оптимизированными размерами"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Добавляем атрибуты для передачи данных, как в старом коде
        self.entry_name = ""
        self.entry_description = ""
        self.action_type = ""
        self.target_area = ""

        # Основной контейнер с вертикальной ориентацией
        main_layout = BoxLayout(
            orientation='vertical',
            padding='20dp',
            spacing='20dp'
        )

        # Заголовок (уменьшенный текст)
        title = Label(
            text='Область действия',
            size_hint=(1, None),
            height='60dp',
            font_size='18sp'
        )
        main_layout.add_widget(title)

        # Выбор типа области (компактный)
        self.area_type = Spinner(
            text='Выберите тип',
            values=['Одна цель', 'Несколько целей', 'На себя', 'Площадь'],
            size_hint=(1, None),
            height='70dp',
            font_size='16sp'
        )
        self.area_type.bind(text=self.update_options)
        main_layout.add_widget(self.area_type)

        # Контейнер для динамических элементов
        self.options_container = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height='250dp',
            spacing='15dp'
        )
        main_layout.add_widget(self.options_container)

        # Создаем элементы управления
        self.create_option_widgets()

        # Кнопка далее (крупная)
        next_btn = Button(
            text='Далее',
            size_hint=(1, None),
            height='80dp',
            font_size='18sp'
        )
        next_btn.bind(on_press=self.go_next)
        main_layout.add_widget(next_btn)

        # Добавляем прокрутку
        scroll = ScrollView()
        scroll.add_widget(main_layout)
        self.add_widget(scroll)

    def on_pre_enter(self):
        """Получаем данные от предыдущих экранов, как в старом коде"""
        prev_screen = self.manager.get_screen('action')
        self.entry_name = prev_screen.entry_name
        self.entry_description = prev_screen.entry_description
        self.action_type = prev_screen.spinner_action_type.text

    def create_option_widgets(self):
        """Создает элементы для разных вариантов выбора"""
        # Для нескольких целей
        self.multi_target_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height='60dp'
        )
        self.multi_target_layout.add_widget(Label(
            text='Кол-во целей:',
            size_hint=(0.6, 1),
            font_size='16sp'
        ))
        self.target_count = TextInput(
            multiline=False,
            input_filter='int',
            hint_text='2',
            size_hint=(0.4, 1),
            font_size='16sp',
            height='60dp'
        )
        self.multi_target_layout.add_widget(self.target_count)

        # Для площади
        self.area_layout = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height='180dp',
            spacing='10dp'
        )

        # Размер площади
        area_size_row = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height='60dp'
        )
        area_size_row.add_widget(Label(
            text='Размер (м²):',
            size_hint=(0.6, 1),
            font_size='16sp'
        ))
        self.area_size = TextInput(
            multiline=False,
            input_filter='int',
            hint_text='3',
            size_hint=(0.4, 1),
            font_size='16sp',
            height='60dp'
        )
        area_size_row.add_widget(self.area_size)

        # Переключатель перемещения
        switch_row = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height='60dp'
        )
        switch_row.add_widget(Label(
            text='Перемещаемая:',
            size_hint=(0.6, 1),
            font_size='16sp'
        ))
        self.move_switch = Switch(active=False, size_hint=(0.4, 1))
        switch_row.add_widget(self.move_switch)

        # Дальность перемещения
        self.move_range_row = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height='60dp'
        )
        self.move_range_row.add_widget(Label(
            text='Дальность (м):',
            size_hint=(0.6, 1),
            font_size='16sp'
        ))
        self.move_range = TextInput(
            multiline=False,
            input_filter='int',
            hint_text='3',
            disabled=True,
            size_hint=(0.4, 1),
            font_size='16sp',
            height='60dp'
        )
        self.move_range_row.add_widget(self.move_range)

        # Собираем всё вместе
        self.area_layout.add_widget(area_size_row)
        self.area_layout.add_widget(switch_row)
        self.area_layout.add_widget(self.move_range_row)

        # Привязываем события
        self.move_switch.bind(active=self.toggle_move_range)

    def toggle_move_range(self, instance, value):
        """Управляет доступностью поля дальности перемещения"""
        self.move_range.disabled = not value
        self.move_range.text = '' if value else ''

    def update_options(self, instance, value):
        """Обновляет отображаемые элементы управления"""
        self.options_container.clear_widgets()

        if value == 'Несколько целей':
            self.options_container.add_widget(self.multi_target_layout)
        elif value == 'Площадь':
            self.options_container.add_widget(self.area_layout)

    def go_next(self, instance):
        """Обрабатывает переход к следующему экрану"""
        area_type = self.area_type.text

        if area_type == 'Несколько целей':
            if not self.validate_input(self.target_count.text, 'количество целей'):
                return
            count = int(self.target_count.text or '2')
            target_area = f'Несколько целей ({count})'

        elif area_type == 'Площадь':
            if not self.validate_input(self.area_size.text, 'размер площади'):
                return

            size = int(self.area_size.text or '3')
            if self.move_switch.active:
                if not self.validate_input(self.move_range.text, 'дальность перемещения'):
                    return
                move = int(self.move_range.text or '3')
                target_area = f'Площадь ({size} м², перемещение {move} м)'
            else:
                target_area = f'Площадь ({size} м²)'
        else:
            target_area = area_type  # "Одна цель" или "На себя"

        # Сохраняем в user_data для использования на последнем экране
        app = App.get_running_app()
        app.user_data['target_area'] = target_area

        # Передаем данные следующему экрану
        duration_screen = self.manager.get_screen('duration')
        duration_screen.entry_name = self.entry_name
        duration_screen.entry_description = self.entry_description
        duration_screen.action_type = self.action_type
        duration_screen.target_area = target_area  # Используем вычисленное значение

        self.manager.current = 'duration'

    def on_leave(self, *args):
        """Очищает экран при уходе"""
        self.clear_inputs()
        return super().on_leave(*args)

    def clear_inputs(self):
        """Сбрасывает все поля ввода"""
        self.area_type.text = 'Выберите тип'
        self.target_count.text = ''
        self.area_size.text = ''
        self.move_switch.active = False
        self.move_range.text = ''
        self.options_container.clear_widgets()

    def validate_input(self, value, field_name):
        """Проверяет корректность ввода"""
        if not value.strip():
            return True  # Допускаем пустое значение

        try:
            num = int(value)
            if num < 1:
                self.show_error('Некорректное значение', f'{field_name.capitalize()} должно быть больше 0')
                return False
            return True
        except ValueError:
            self.show_error('Ошибка ввода', f'Введите целое число для {field_name}')
            return False

    def show_error(self, title, message):
        """Отображает сообщение об ошибке"""
        Popup(
            title=title,
            content=Label(text=message),
            size_hint=(0.7, 0.3)
        ).open()



class DurationSelectionScreen(ThemedScreen):
        """Экран выбора продолжительности способности"""

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

            self.label_duration = Label(text="Выберите продолжительность:")
            self.spinner_duration = Spinner(
                text="Выберите",
                values=[
                    "Моментально",
                    "Раунды",
                    "Минуты",
                    "Часы",
                    "До конца сцены",
                    "Постоянное действие",
                ],
            )

            self.button_next = Button(text="Далее", on_press=self.check_duration)

            layout.add_widget(self.label_duration)
            layout.add_widget(self.spinner_duration)
            layout.add_widget(self.button_next)

            self.add_widget(layout)

        def check_duration(self, instance):
            """Проверяем выбор и при необходимости запрашиваем ввод числа"""
            duration = self.spinner_duration.text

            if duration in ["Раунды", "Минуты", "Часы"]:
                self.ask_number_input(duration)
            else:
                self.save_duration(duration)

        def ask_number_input(self, duration):
            """Открываем всплывающее окно для ввода числа"""
            content = BoxLayout(orientation="vertical", padding=10, spacing=10)
            label = Label(text=f"Введите количество {duration.lower()}:")
            self.entry_duration_number = TextInput(multiline=False)

            button_ok = Button(text="OK", on_press=lambda x: self.save_duration(duration))
            content.add_widget(label)
            content.add_widget(self.entry_duration_number)
            content.add_widget(button_ok)

            self.popup = Popup(title="Введите значение", content=content, size_hint=(0.6, 0.4))
            self.popup.open()

        def save_duration(self, duration):
            """Сохраняем продолжительность и переходим дальше"""
            if duration in ["Раунды", "Минуты", "Часы"]:
                try:
                    value = int(self.entry_duration_number.text)
                    duration = f"{value} {duration.lower()}"
                except ValueError:
                    duration = f"1 {duration.lower()}"  # Значение по умолчанию

            self.manager.get_screen("probability").entry_name = self.entry_name
            self.manager.get_screen("probability").entry_description = self.entry_description
            self.manager.get_screen("probability").action_type = self.action_type
            self.manager.get_screen("probability").target_area = self.target_area
            self.manager.get_screen("probability").duration = duration
            self.popup.dismiss() if hasattr(self, "popup") else None
            self.manager.current = "probability"

        def save_data(self, key, value):
            """Сохраняет данные в глобальный словарь"""
            app = App.get_running_app()
            app.user_data[key] = value

        def on_pre_leave(self):
            """Сохраняем выбранную продолжительность и её значение (если есть)."""
            app = App.get_running_app()
            if not hasattr(app, "user_data"):
                app.user_data = {}

            duration = self.spinner_duration.text  # "Раунды", "Минуты", "Часы" и т.д.

            # Проверяем, если выбраны "Раунды", "Минуты" или "Часы", берём введённое число
            if duration in ["Раунды", "Минуты", "Часы"]:
                try:
                    value = int(self.entry_duration_number.text)  # Берём введённое число
                    duration = f"{value} {duration}"  # Например, "3 Раунды"
                except ValueError:
                    duration = f"1 {duration}"  # Если число не введено, ставим 1

            app.user_data["spinner_duration"] = duration  # Сохраняем с числом!
            """Очистка виджетов выбора длительности"""
            self.spinner_duration.text = "Выберите"
            if hasattr(self, "entry_duration_number"):
                self.entry_duration_number.text = ""


class ProbabilitySelectionScreen(ThemedScreen):
        """Экран выбора вероятности успеха способности"""

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

            self.label_probability = Label(text="Выберите вероятность успеха:")
            self.spinner_probability = Spinner(
                text="Выберите",
                values=["Проверка", "Автоматический успех", "Состязание"],
            )

            self.button_next = Button(text="Далее", on_press=self.check_probability)

            layout.add_widget(self.label_probability)
            layout.add_widget(self.spinner_probability)
            layout.add_widget(self.button_next)

            self.add_widget(layout)

        def check_probability(self, instance):
            """Проверяем выбор и учитываем штрафы для авт. успеха"""
            self.probability = self.spinner_probability.text

            # Получаем данные о предыдущем выборе
            target_screen = self.manager.get_screen("target")
            target_area = getattr(target_screen, "target_area", "Цели")
            self.probability = self.spinner_probability.text

            if self.probability == "Автоматический успех":
                if target_area == "Цели":
                    action_screen = self.manager.get_screen("action")
                    action_type = getattr(action_screen, "action_type", "")

                    # Если цель - "на себя", штраф 10 ОП, иначе 40 ОП
                    penalty = 10 if "на себя" in action_type else 40
                else:
                    penalty = 40  # Для площади всегда штраф 40 ОП
            else:
                penalty = 0

            range_screen = self.manager.get_screen("range")
            range_screen.probability = self.probability
            range_screen.penalty = penalty
            self.manager.current = "range"

        def on_pre_leave(self):
            """Сохраняем вероятность успеха"""
            app = App.get_running_app()
            if not hasattr(app, "user_data"):
                app.user_data = {}

            app.user_data["spinner_probability"] = self.spinner_probability.text
            """Очистка spinner вероятности"""
            self.spinner_probability.text = "Выберите"


class RangeSelectionScreen(ThemedScreen):
    """Экран ввода дальности действия способности"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.entry_name = ""
        self.entry_description = ""
        self.action_type = ""
        self.target_area = ""
        self.duration = ""
        self.probability = ""

        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        self.label_range = Label(text="Введите дальность (число):")
        self.entry_range = TextInput(multiline=False, input_filter="int")

        self.button_next = Button(text="Далее", on_press=self.process_range)

        layout.add_widget(self.label_range)
        layout.add_widget(self.entry_range)
        layout.add_widget(self.button_next)

        self.add_widget(layout)

    def on_pre_enter(self):
        """Получаем данные от предыдущих экранов"""
        prev_screen = self.manager.get_screen("probability")
        self.entry_name = prev_screen.entry_name
        self.entry_description = prev_screen.entry_description
        self.action_type = prev_screen.action_type
        self.target_area = prev_screen.target_area
        self.duration = prev_screen.duration
        self.probability = prev_screen.probability

    def on_pre_leave(self):
        """Сохраняем дальность действия"""
        app = App.get_running_app()
        if not hasattr(app, "user_data"):
            app.user_data = {}

        app.user_data["entry_range"] = self.entry_range.text
        """Очистка поля ввода дальности"""
        self.entry_range.text = ""

    def process_range(self, instance):
        """Проверяем ввод и рассчитываем стоимость дальности"""
        try:
            range_value = int(self.entry_range.text)
        except ValueError:
            self.show_error("Ошибка", "Введите корректное число.")
            return

        # Рассчитываем стоимость дальности
        if range_value < 50:
            cost = range_value
        elif 50 <= range_value <= 100:
            cost = 50 + (range_value - 50) // 5
        elif 100 < range_value <= 300:
            cost = 60 + (range_value - 100) // 10
        elif range_value > 300:
            cost = 80 + (range_value - 300) // 50
        else:
            cost = 123456789  # Неограниченная дальность

        # Сохраняем данные и переходим к следующему экрану
        effects_screen = self.manager.get_screen("effects")
        effects_screen.entry_name = self.entry_name
        effects_screen.entry_description = self.entry_description
        effects_screen.action_type = self.action_type
        effects_screen.target_area = self.target_area
        effects_screen.duration = self.duration
        effects_screen.probability = self.probability
        effects_screen.range_value = range_value
        effects_screen.range_cost = cost

        self.manager.current = "effects"

    def show_error(self, title, message):
        """Всплывающее окно ошибки"""
        popup = Popup(
            title=title,
            content=Label(text=message),
            size_hint=(0.6, 0.3),
        )
        popup.open()

    def save_data(self, key, value):
        """Сохраняет данные в глобальный словарь"""
        app = App.get_running_app()
        app.user_data[key] = value



class EffectsSelectionScreen(ThemedScreen):
        """Экран выбора эффекта способности"""

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.selected_effects = []  # Список выбранных эффектов

            layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

            self.label_effects = Label(text="Выберите эффект:")
            self.spinner_effects = Spinner(
                text="Выберите",
                values=[
                    "Урон",
                    "Лечение",
                    "Превращение",
                    "Доп. Действия",
                    "Перемещение",
                    "Дескрипторы",
                    "Бонусы и штрафы",
                    "Создание существа",
                    "Щит",
                    "Прочие эффекты",
                    "Ограничения",
                ],
            )

            self.button_add = Button(text="Добавить эффект", on_press=self.add_effect)
            self.button_done = Button(text="Готово", on_press=self.finish_selection)

            self.label_selected = Label(text="Выбранные эффекты: None", size_hint_y=None, height=40)

            layout.add_widget(self.label_effects)
            layout.add_widget(self.spinner_effects)
            layout.add_widget(self.button_add)
            layout.add_widget(self.label_selected)
            layout.add_widget(self.button_done)

            self.add_widget(layout)

        def add_effect(self, instance):
            """Добавляем эффект и переходим на соответствующий экран"""
            effect = self.spinner_effects.text

            if effect == "Выберите":
                self.show_error("Ошибка", "Выберите эффект перед добавлением.")
                return

            self.label_selected.text = f"Выбранные эффекты: {', '.join(self.selected_effects)}"

            # Переход на соответствующий экран
            effect_screens = {
                "Урон": "damage",
                "Лечение": "healing",
                "Превращение": "transformation",
                "Доп. Действия": "extra_action",
                "Перемещение": "movement",
                "Дескрипторы": "descriptors",
                "Бонусы и штрафы": "bonuses",
                "Создание существа": "creature",
                "Щит": "shield",
                "Прочие эффекты": "other_effects",
                "Ограничения": "restriction",
            }

            if effect in effect_screens:
                self.manager.current = effect_screens[effect]

        def on_pre_leave(self):
            """Сохраняем выбранные эффекты"""
            app = App.get_running_app()
            if not hasattr(app, "user_data"):
                app.user_data = {}

            app.user_data["selected_effects"] = self.selected_effects


        def finish_selection(self, instance):
            """Сохраняем эффекты и переходим к итоговому экрану"""
            self.manager.get_screen("final_summary").entry_name = self.entry_name
            self.manager.get_screen("final_summary").entry_description = self.entry_description
            self.manager.get_screen("final_summary").action_type = self.action_type
            self.manager.get_screen("final_summary").target_area = self.target_area
            self.manager.get_screen("final_summary").duration = self.duration
            self.manager.get_screen("final_summary").probability = self.probability
            self.manager.get_screen("final_summary").range_value = self.range_value
            self.manager.get_screen("final_summary").selected_effects = self.selected_effects
            self.manager.current = "final_summary"
            """Сброс выбранных эффектов"""
            self.spinner_effects.text = "Выберите"
            self.selected_effects = []
            self.label_selected.text = "Выбранные эффекты: None"

        def show_error(self, title, message):
            """Всплывающее окно ошибки"""
            popup = Popup(
                title=title,
                content=Label(text=message),
                size_hint=(0.6, 0.3),
            )
            popup.open()

        def save_data(self, key, value):
           """Сохраняет данные в глобальный словарь"""
           app = App.get_running_app()
           app.user_data[key] = value


class DamageSelectionScreen(ThemedScreen):
        """Экран ввода параметров урона"""

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

            self.label_damage_type = Label(text="Выберите тип урона:")
            self.spinner_damage_type = Spinner(
                text="Выберите",
                values=["единицы", "d4", "d6", "de", "d8", "d10", "d12"],
            )

            self.label_dice_count = Label(text="Введите количество костей:")
            self.entry_dice_count = TextInput(multiline=False, input_filter="int")

            self.button_save = Button(text="Сохранить", on_press=self.save_damage)

            layout.add_widget(self.label_damage_type)
            layout.add_widget(self.spinner_damage_type)
            layout.add_widget(self.label_dice_count)
            layout.add_widget(self.entry_dice_count)
            layout.add_widget(self.button_save)

            self.add_widget(layout)

        def save_damage(self, instance):
            damage_type = self.spinner_damage_type.text
            try:
                dice_count = int(self.entry_dice_count.text)
            except ValueError:
                self.show_error("Ошибка", "Введите корректное число костей.")
                return

            if damage_type == "Выберите":
                self.show_error("Ошибка", "Выберите тип урона.")
                return
            """Очистка параметров урона"""
            self.spinner_damage_type.text = "Выберите"
            self.entry_dice_count.text = ""

            # Формируем строку с описанием урона
            damage_description = f"Урон: {dice_count}x{damage_type}"

            # === ВСТАВИТЬ ЗДЕСЬ ===
            app = App.get_running_app()
            app.user_data["damage"] = damage_description  # Сохраняем в глобальные данные
            effects_screen = self.manager.get_screen("effects")
            effects_screen.selected_effects.append(damage_description)  # Добавляем в текущий список эффектов
            # ======================

            # Возвращаемся в меню эффектов
            self.manager.current = "effects"

        def show_error(self, title, message):
            """Всплывающее окно ошибки"""
            popup = Popup(
                title=title,
                content=Label(text=message),
                size_hint=(0.6, 0.3),
            )
            popup.open()


class HealingSelectionScreen(ThemedScreen):
        """Экран ввода параметров лечения"""

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

            self.label_healing_type = Label(text="Выберите тип лечения:")
            self.spinner_healing_type = Spinner(
                text="Выберите",
                values=["единицы", "d4", "d6", "d8", "de", "d10", "d12"],
            )

            self.label_dice_count = Label(text="Введите количество костей:")
            self.entry_dice_count = TextInput(multiline=False, input_filter="int")

            self.button_save = Button(text="Сохранить", on_press=self.save_healing)

            layout.add_widget(self.label_healing_type)
            layout.add_widget(self.spinner_healing_type)
            layout.add_widget(self.label_dice_count)
            layout.add_widget(self.entry_dice_count)
            layout.add_widget(self.button_save)

            self.add_widget(layout)

        def save_healing(self, instance):
            healing_type = self.spinner_healing_type.text
            try:
                dice_count = int(self.entry_dice_count.text)
            except ValueError:
                self.show_error("Ошибка", "Введите корректное число кубиков.")
                return

            if healing_type == "Выберите":
                self.show_error("Ошибка", "Выберите тип лечения.")
                return

            healing_description = f"Лечение: {dice_count}x{healing_type}"

            # === ВСТАВИТЬ ЗДЕСЬ ===
            app = App.get_running_app()
            app.user_data["healing"] = healing_description
            effects_screen = self.manager.get_screen("effects")
            effects_screen.selected_effects.append(healing_description)
            # ======================

            self.manager.current = "effects"
            """Очистка параметров лечения"""
            self.spinner_healing_type.text = "Выберите"
            self.entry_dice_count.text = ""

        def show_error(self, title, message):
            """Всплывающее окно ошибки"""
            popup = Popup(
                title=title,
                content=Label(text=message),
                size_hint=(0.6, 0.3),
            )
            popup.open()


class ExtraActionSelectionScreen(ThemedScreen):
    """Экран выбора количества дополнительных действий"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.extra_action_count = 0  # Количество дополнительных действий

        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        self.label_extra = Label(text="Введите количество дополнительных действий:")
        self.entry_extra_count = TextInput(multiline=False, input_filter="int")

        self.button_next = Button(text="Далее", on_press=self.process_extra_actions)

        layout.add_widget(self.label_extra)
        layout.add_widget(self.entry_extra_count)
        layout.add_widget(self.button_next)

        self.add_widget(layout)

    def process_extra_actions(self, instance):
        """Сохраняем количество доп. действий и переходим к описанию"""
        try:
            count = int(self.entry_extra_count.text)
            if count < 1:
                raise ValueError("Должно быть хотя бы одно действие.")
            self.extra_action_count = count

            desc_screen = self.manager.get_screen("extra_action_desc")
            desc_screen.extra_actions = []
            desc_screen.current_extra_index = 0
            desc_screen.total_extra_actions = count  # Передаём количество
            desc_screen.update_prompt()  # Обновляем текст запроса

            self.manager.current = "extra_action_desc"
        except ValueError:
            self.show_error("Ошибка", "Введите корректное число.")
        """Очистка поля ввода количества действий"""
        self.entry_extra_count.text = ""

    def show_error(self, title, message):
        """Всплывающее окно ошибки"""
        popup = Popup(title=title, content=Label(text=message), size_hint=(0.6, 0.3))
        popup.open()


class ExtraActionDescriptionScreen(ThemedScreen):
    """Экран ввода описания каждого доп. действия"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.extra_actions = []
        self.current_extra_index = 0
        self.total_extra_actions = 0  # Общее количество действий

        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        self.label_extra_desc = Label(text="Введите описание дополнительного действия:")
        self.entry_extra_desc = TextInput(multiline=False)

        self.button_next = Button(text="Далее", on_press=self.process_extra_action_description)

        layout.add_widget(self.label_extra_desc)
        layout.add_widget(self.entry_extra_desc)
        layout.add_widget(self.button_next)

        self.add_widget(layout)

    def update_prompt(self):
        """Обновляет текст с номером текущего действия"""
        self.label_extra_desc.text = f"Введите описание доп. действия {self.current_extra_index + 1}/{self.total_extra_actions}:"
        self.entry_extra_desc.text = ""  # Очищаем поле ввода

    def process_extra_action_description(self, instance):
        """Сохраняем описание доп. действия и переходим к следующему"""
        action_desc = self.entry_extra_desc.text.strip()
        if action_desc:
            self.extra_actions.append(action_desc)

        self.current_extra_index += 1
        if self.current_extra_index < self.total_extra_actions:
            self.update_prompt()  # Обновляем текст и поле ввода
        else:
            # Сохраняем все доп. действия в EffectsSelectionScreen
            effects_screen = self.manager.get_screen("effects")
            effects_screen.selected_effects.append(f"Доп. действия: {', '.join(self.extra_actions)}")
            self.manager.current = "effects"


class DescriptorsSelectionScreen(ThemedScreen):
    """Экран ввода дескрипторов"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.descriptors = []  # Список для хранения дескрипторов

        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        self.label_descriptors = Label(text="Введите дескриптор способности:")
        self.entry_descriptors = TextInput(multiline=False)

        self.button_add = Button(text="Добавить", on_press=self.add_descriptor)
        self.button_done = Button(text="Готово", on_press=self.finish_selection)

        self.label_selected = Label(text="Выбранные дескрипторы: None", size_hint_y=None, height=40)

        layout.add_widget(self.label_descriptors)
        layout.add_widget(self.entry_descriptors)
        layout.add_widget(self.button_add)
        layout.add_widget(self.label_selected)
        layout.add_widget(self.button_done)

        self.add_widget(layout)

    def add_descriptor(self, instance):
        """Добавляем дескриптор в список"""
        descriptor = self.entry_descriptors.text.strip()

        if descriptor:
            self.descriptors.append(descriptor)
            self.label_selected.text = f"Выбранные дескрипторы: {', '.join(self.descriptors)}"
            self.entry_descriptors.text = ""

    def finish_selection(self, instance):
        """Сохраняем дескрипторы и переходим к следующему шагу"""
        app = App.get_running_app()
        if not hasattr(app, "user_data"):
            app.user_data = {}

        # Сохраняем дескрипторы в user_data
        app.user_data["descriptors"] = self.descriptors

        # Переходим к экрану эффектов
        effects_screen = self.manager.get_screen("effects")
        effects_screen.selected_effects.append(f"Дескрипторы: {', '.join(self.descriptors)}")
        self.manager.current = "effects"
        """Очистка списка дескрипторов"""
        self.descriptors = []
        self.entry_descriptors.text = ""
        self.label_selected.text = "Выбранные дескрипторы: None"


class BonusesSelectionScreen(ThemedScreen):
    """Экран ввода бонусов и штрафов"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bonuses = []  # Список для хранения бонусов/штрафов

        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        self.label_bonuses = Label(text="Введите характеристику для бонуса/штрафа:")
        self.entry_bonuses = TextInput(multiline=False)

        self.label_bonuses_value = Label(text="Введите значение (число):")
        self.entry_bonuses_value = TextInput(multiline=False, input_filter="int")

        self.button_add = Button(text="Добавить", on_press=self.add_bonus)
        self.button_done = Button(text="Готово", on_press=self.finish_selection)

        self.label_selected = Label(text="Выбранные бонусы/штрафы: None", size_hint_y=None, height=40)

        layout.add_widget(self.label_bonuses)
        layout.add_widget(self.entry_bonuses)
        layout.add_widget(self.label_bonuses_value)
        layout.add_widget(self.entry_bonuses_value)
        layout.add_widget(self.button_add)
        layout.add_widget(self.label_selected)
        layout.add_widget(self.button_done)

        self.add_widget(layout)

    def add_bonus(self, instance):
        """Добавляем бонус/штраф в список"""
        characteristic = self.entry_bonuses.text.strip()
        value = self.entry_bonuses_value.text.strip()

        if characteristic and value:
            try:
                value = int(value)
                # Сохраняем абсолютное значение для расчета ОП
                absolute_value = abs(value)
                # Сохраняем бонус/штраф в виде словаря
                bonus = {
                    "characteristic": characteristic,
                    "value": value,
                    "absolute_value": absolute_value  # Добавляем абсолютное значение
                }
                self.bonuses.append(bonus)
                # Обновляем список выбранных бонусов/штрафов
                self.label_selected.text = f"""Выбранные бонусы/штрафы: {', '.join([f'{b["characteristic"]}: {b["value"]}' for b in self.bonuses])}"""
                self.entry_bonuses.text = ""
                self.entry_bonuses_value.text = ""
            except ValueError:
                self.show_error("Ошибка", "Введите корректное число.")
        else:
            self.show_error("Ошибка", "Заполните все поля.")

    def finish_selection(self, instance):
        """Сохраняем бонусы и штрафы и переходим к следующему шагу"""
        app = App.get_running_app()
        if not hasattr(app, "user_data"):
            app.user_data = {}

        # Сохраняем бонусы/штрафы в user_data
        app.user_data["bonuses"] = self.bonuses

        # Переходим к экрану эффектов
        effects_screen = self.manager.get_screen("effects")
        effects_screen.selected_effects.append(f"""Бонусы/Штрафы: {', '.join([f'''{b['characteristic']}: {b['value']}''' for b in self.bonuses])}""")
        self.manager.current = "effects"
        """Сброс бонусов/штрафов"""
        self.bonuses = []
        self.entry_bonuses.text = ""
        self.entry_bonuses_value.text = ""
        self.label_selected.text = "Выбранные бонусы/штрафы: None"

    def show_error(self, title, message):
        """Всплывающее окно ошибки"""
        popup = Popup(title=title, content=Label(text=message), size_hint=(0.6, 0.3))
        popup.open()


class CreatureCreationScreen(ThemedScreen):
    """Экран создания существа"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.creatures = []

        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        self.label_creature = Label(text="Введите название существа:")
        self.entry_creature = TextInput(multiline=False)

        self.label_po = Label(text="Введите ПО существа:")
        self.entry_po = TextInput(multiline=False, input_filter="int")

        self.label_control = Label(text="Выберите уровень контроля:")
        self.spinner_control = Spinner(
            text="Выберите",
            values=["По своей воле (0 ОП)", "Подчиняется устным командам (10 ОП)", "Под полным ментальным контролем (20 ОП)"],
        )

        self.button_add = Button(text="Добавить", on_press=self.add_creature)
        self.button_done = Button(text="Готово", on_press=self.finish_selection)

        self.label_selected = Label(text="Созданные существа: None", size_hint_y=None, height=40)

        layout.add_widget(self.label_creature)
        layout.add_widget(self.entry_creature)
        layout.add_widget(self.label_po)
        layout.add_widget(self.entry_po)
        layout.add_widget(self.label_control)
        layout.add_widget(self.spinner_control)
        layout.add_widget(self.button_add)
        layout.add_widget(self.label_selected)
        layout.add_widget(self.button_done)

        self.add_widget(layout)

    def add_creature(self, instance):
        """Добавляем описание существа"""
        creature_name = self.entry_creature.text.strip()
        po = self.entry_po.text.strip()
        control = self.spinner_control.text

        if creature_name and po:
            try:
                po = int(po)
                control_cost = 0
                control_text = control.split(" (")[0]  # Убираем ОП из типа контроля
                if "устным командам" in control:
                    control_cost = 10
                elif "полным ментальным контролем" in control:
                    control_cost = 20

                total_cost = po * 25 + control_cost
                # Сохраняем существо в формате: {"name": "Лошадь", "po": 5, "control": "Подчиняется устным командам", "cost": 135}
                creature_data = {
                    "name": creature_name,
                    "po": po,
                    "control": control_text,
                    "cost": total_cost
                }
                self.creatures.append(creature_data)
                self.label_selected.text = f"Созданные существа: {', '.join([c['name'] for c in self.creatures])}"
                self.entry_creature.text = ""
                self.entry_po.text = ""
            except ValueError:
                self.show_error("Ошибка", "ПО должно быть числом.")
        else:
            self.show_error("Ошибка", "Заполните все поля.")

    def finish_selection(self, instance):
        """Сохраняем создание существ и переходим к следующему шагу"""
        app = App.get_running_app()
        if not hasattr(app, "user_data"):
            app.user_data = {}

        # Сохраняем созданные существа в user_data в правильном формате
        app.user_data["created_creatures"] = [
            {
                "name": c["name"],
                "po": c["po"],
                "control": c["control"],
                "cost": c["cost"]
            }
            for c in self.creatures
        ]

        # Переходим к экрану эффектов
        effects_screen = self.manager.get_screen("effects")
        effects_screen.selected_effects.append(
            f"""Создание существа: {', '.join([f'{c["name"]} (ПО: {c["po"]}, {c["control"]})' for c in self.creatures])}"""
        )
        self.manager.current = "effects"
        """Очистка данных о существах"""
        self.creatures = []
        self.entry_creature.text = ""
        self.entry_po.text = ""
        self.spinner_control.text = "Выберите"
        self.label_selected.text = "Созданные существа: None"

    def show_error(self, title, message):
        """Всплывающее окно ошибки"""
        popup = Popup(title=title, content=Label(text=message), size_hint=(0.6, 0.3))
        popup.open()


class TransformationScreen(ThemedScreen):
    """Экран превращения"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.transformations = []

        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        self.label_creature = Label(text="Введите название существа:")
        self.entry_creature = TextInput(multiline=False)

        self.label_po = Label(text="Введите ПО существа:")
        self.entry_po = TextInput(multiline=False, input_filter="int")

        self.button_add = Button(text="Добавить", on_press=self.add_transformation)
        self.button_done = Button(text="Готово", on_press=self.finish_selection)

        self.label_selected = Label(text="Выбранные превращения: None", size_hint_y=None, height=40)

        layout.add_widget(self.label_creature)
        layout.add_widget(self.entry_creature)
        layout.add_widget(self.label_po)
        layout.add_widget(self.entry_po)
        layout.add_widget(self.button_add)
        layout.add_widget(self.label_selected)
        layout.add_widget(self.button_done)

        self.add_widget(layout)

    def add_transformation(self, instance):
        creature_name = self.entry_creature.text.strip()
        po = self.entry_po.text.strip()

        if creature_name and po:
            try:
                po = int(po)
                total_cost = po * 25
                transformation_data = {
                    "name": creature_name,
                    "po": po,
                    "cost": total_cost
                }

                # Сохраняем в глобальные данные
                app = App.get_running_app()
                if not hasattr(app, "user_data"):
                    app.user_data = {}

                if "transformations" not in app.user_data:
                    app.user_data["transformations"] = []

                app.user_data["transformations"].append(transformation_data)

                # Обновляем отображение
                self.transformations.append(f"{creature_name} (ПО: {po})")
                self.label_selected.text = f"Выбранные превращения: {', '.join(self.transformations)}"
                self.entry_creature.text = ""
                self.entry_po.text = ""
            except ValueError:
                self.show_error("Ошибка", "ПО должно быть числом.")

    def finish_selection(self, instance):
        """Сохраняем превращение и переходим к следующему шагу"""
        effects_screen = self.manager.get_screen("effects")
        effects_screen.selected_effects.append(f"Превращение: {', '.join(self.transformations)}")
        self.manager.current = "effects"
        """Сброс данных о превращениях"""
        self.transformations = []
        self.entry_creature.text = ""
        self.entry_po.text = ""
        self.label_selected.text = "Выбранные превращения: None"

    def show_error(self, title, message):
        """Всплывающее окно ошибки"""
        popup = Popup(title=title, content=Label(text=message), size_hint=(0.6, 0.3))
        popup.open()



class ShieldSelectionScreen(ThemedScreen):
        """Экран создания щита или баррикады"""

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.shield_type = None
            self.shield_stat = None
            self.shield_value = 0

            layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

            self.label_shield_type = Label(text="Выберите тип: Щит или Баррикада")
            self.spinner_shield_type = Spinner(text="Выберите", values=["Щит", "Баррикада"])

            self.button_next = Button(text="Далее", on_press=self.process_shield_type)

            layout.add_widget(self.label_shield_type)
            layout.add_widget(self.spinner_shield_type)
            layout.add_widget(self.button_next)

            self.add_widget(layout)

        def process_shield_type(self, instance):
            """Переход к настройкам в зависимости от выбора"""
            self.shield_type = self.spinner_shield_type.text
            if self.shield_type == "Щит":
                self.manager.current = "shield_config"
            elif self.shield_type == "Баррикада":
                self.manager.current = "barrier_config"
            else:
                self.show_error("Ошибка", "Выберите Щит или Баррикаду.")
            """Очистка выбора типа защиты"""
            self.spinner_shield_type.text = "Выберите"

        def show_error(self, title, message):
            """Всплывающее окно ошибки"""
            popup = Popup(title=title, content=Label(text=message), size_hint=(0.6, 0.3))
            popup.open()


class ShieldConfigScreen(ThemedScreen):
        """Экран выбора характеристик щита"""

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

            layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

            self.label_shield_stat = Label(text="Выберите характеристику (Выносливость / Сила воли):")
            self.spinner_shield_stat = Spinner(text="Выберите", values=["Выносливость", "Сила воли"])

            self.label_shield_value = Label(text="Введите количество единиц защиты:")
            self.entry_shield_value = TextInput(multiline=False, input_filter="int")

            self.button_done = Button(text="Сохранить", on_press=self.save_shield)

            layout.add_widget(self.label_shield_stat)
            layout.add_widget(self.spinner_shield_stat)
            layout.add_widget(self.label_shield_value)
            layout.add_widget(self.entry_shield_value)
            layout.add_widget(self.button_done)

            self.add_widget(layout)

        def save_shield(self, instance):
            """Сохраняем параметры щита и переходим дальше"""
            stat = self.spinner_shield_stat.text
            value = self.entry_shield_value.text.strip()

            if stat == "Выберите" or not value:
                self.show_error("Ошибка", "Заполните все поля.")
                return

            try:
                value = int(value)
                effects_screen = self.manager.get_screen("effects")
                effects_screen.selected_effects.append(f"Щит ({stat}): {value} ед. защиты")
                self.manager.current = "effects"
            except ValueError:
                self.show_error("Ошибка", "Введите корректное число.")
            """Сброс параметров щита"""
            self.spinner_shield_stat.text = "Выберите"
            self.entry_shield_value.text = ""

        def show_error(self, title, message):
            """Всплывающее окно ошибки"""
            popup = Popup(title=title, content=Label(text=message), size_hint=(0.6, 0.3))
            popup.open()


class BarrierConfigScreen(ThemedScreen):
        """Экран настройки баррикады"""

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

            layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

            self.label_barrier_value = Label(text="Введите количество единиц прочности баррикады:")
            self.entry_barrier_value = TextInput(multiline=False, input_filter="int")

            self.button_done = Button(text="Сохранить", on_press=self.save_barrier)

            layout.add_widget(self.label_barrier_value)
            layout.add_widget(self.entry_barrier_value)
            layout.add_widget(self.button_done)

            self.add_widget(layout)

        def save_barrier(self, instance):
            """Сохраняем параметры баррикады и переходим дальше"""
            value = self.entry_barrier_value.text.strip()

            if not value:
                self.show_error("Ошибка", "Введите количество прочности.")
                return

            try:
                value = int(value)
                effects_screen = self.manager.get_screen("effects")
                effects_screen.selected_effects.append(f"Баррикада: {value} ед. прочности")
                self.manager.current = "effects"
            except ValueError:
                self.show_error("Ошибка", "Введите корректное число.")
            """Очистка параметров баррикады"""
            self.entry_barrier_value.text = ""

        def show_error(self, title, message):
            """Всплывающее окно ошибки"""
            popup = Popup(title=title, content=Label(text=message), size_hint=(0.6, 0.3))
            popup.open()

class MovementSelectionScreen(ThemedScreen):
    """Экран ввода параметров перемещения"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        self.label_distance = Label(text="Введите дистанцию перемещения (в метрах):")
        self.entry_distance = TextInput(multiline=False, input_filter="int")

        self.button_save = Button(text="Сохранить", on_press=self.save_movement)

        layout.add_widget(self.label_distance)
        layout.add_widget(self.entry_distance)
        layout.add_widget(self.button_save)

        self.add_widget(layout)

    def save_movement(self, instance):
        """Сохраняем расстояние перемещения и рассчитываем стоимость ОП"""
        try:
            distance = int(self.entry_distance.text)
            if distance <= 0:
                raise ValueError("Дистанция должна быть больше 0.")
        except ValueError:
            self.show_error("Ошибка", "Введите корректное число метров.")
            return

        # Рассчитываем стоимость ОП в зависимости от дистанции
        if distance <= 5:
            cost = distance * 5
        elif distance <= 15:
            cost = distance * 3
        elif distance <= 50:
            cost = distance * 2
        elif distance <= 100:
            cost = 100 + (distance - 50)
        else:
            cost = 300  # Неограниченное перемещение

        # Сохраняем эффект в user_data
        app = App.get_running_app()
        if not hasattr(app, "user_data"):
            app.user_data = {}
        app.user_data["movement"] = f"Перемещение: {distance} м ({cost} ОП)"

        # Сохраняем эффект в список
        effects_screen = self.manager.get_screen("effects")
        effects_screen.selected_effects.append(f"Перемещение: {distance} м ({cost} ОП)")

        # Возвращаемся в меню эффектов
        self.manager.current = "effects"
        """Очистка поля ввода дистанции перемещения при уходе с экрана"""
        self.entry_distance.text = ""

    def show_error(self, title, message):
        """Всплывающее окно ошибки"""
        popup = Popup(
            title=title,
            content=Label(text=message),
            size_hint=(0.6, 0.3),
        )
        popup.open()


class OtherEffectsScreen(ThemedScreen):
    """Экран ввода прочих эффектов"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.effects = []  # Список для хранения прочих эффектов

        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        self.label_other_effects = Label(text="Введите описание прочего эффекта:")
        self.entry_other_effects = TextInput(multiline=True)

        self.button_add = Button(text="Добавить", on_press=self.add_effect)
        self.button_done = Button(text="Готово", on_press=self.finish_selection)

        self.label_selected = Label(text="Выбранные эффекты: None", size_hint_y=None, height=40)

        layout.add_widget(self.label_other_effects)
        layout.add_widget(self.entry_other_effects)
        layout.add_widget(self.button_add)
        layout.add_widget(self.label_selected)
        layout.add_widget(self.button_done)

        self.add_widget(layout)

    def add_effect(self, instance):
        """Добавляем прочий эффект в список"""
        effect_desc = self.entry_other_effects.text.strip()

        if effect_desc:
            self.effects.append(effect_desc)
            self.label_selected.text = f"Выбранные эффекты: {', '.join(self.effects)}"
            self.entry_other_effects.text = ""

    def finish_selection(self, instance):
        """Сохраняем прочие эффекты и переходим к следующему шагу"""
        app = App.get_running_app()
        if not hasattr(app, "user_data"):
            app.user_data = {}

        # Сохраняем прочие эффекты в user_data
        app.user_data["other_effects"] = self.effects

        # Переходим к экрану эффектов
        effects_screen = self.manager.get_screen("effects")
        effects_screen.selected_effects.append(f"Прочие эффекты: {', '.join(self.effects)}")
        self.manager.current = "effects"
        """Сброс списка эффектов"""
        self.effects = []
        self.entry_other_effects.text = ""
        self.label_selected.text = "Выбранные эффекты: None"


class RestrictionScreen(ThemedScreen):
        """Экран ввода ограничений"""

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.restrictions = []

            layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

            self.label_restriction = Label(text="Введите описание ограничения:")
            self.entry_restriction = TextInput(multiline=True)

            self.label_discount = Label(text="Введите скидку (число ОП):")
            self.entry_discount = TextInput(multiline=False, input_filter="int")

            self.button_add = Button(text="Добавить", on_press=self.add_restriction)
            self.button_done = Button(text="Готово", on_press=self.finish_selection)

            self.label_selected = Label(text="Выбранные ограничения: None", size_hint_y=None, height=40)

            layout.add_widget(self.label_restriction)
            layout.add_widget(self.entry_restriction)
            layout.add_widget(self.label_discount)
            layout.add_widget(self.entry_discount)
            layout.add_widget(self.button_add)
            layout.add_widget(self.label_selected)
            layout.add_widget(self.button_done)

            self.add_widget(layout)

        def add_restriction(self, instance):
            """Добавляем ограничение в список"""
            restriction_desc = self.entry_restriction.text.strip()
            discount = self.entry_discount.text.strip()

            if restriction_desc and discount:
                try:
                    discount = int(discount)
                    self.restrictions.append(f"{restriction_desc} (-{discount} ОП)")
                    self.label_selected.text = f"Выбранные ограничения: {', '.join(self.restrictions)}"
                    self.entry_restriction.text = ""
                    self.entry_discount.text = ""
                except ValueError:
                    self.show_error("Ошибка", "Скидка должна быть числом.")

        def finish_selection(self, instance):
            """Сохраняем ограничения и переходим к следующему шагу"""
            effects_screen = self.manager.get_screen("effects")
            effects_screen.selected_effects.append(f"Ограничения: {', '.join(self.restrictions)}")
            self.manager.current = "effects"
            """Очистка списка ограничений"""
            self.restrictions = []
            self.entry_restriction.text = ""
            self.entry_discount.text = ""
            self.label_selected.text = "Выбранные ограничения: None"

        def show_error(self, title, message):
            """Всплывающее окно ошибки"""
            popup = Popup(title=title, content=Label(text=message), size_hint=(0.6, 0.3))
            popup.open()

def calculate_damage_cost(damage_str):
    """Рассчитывает стоимость урона по формату 'Урон: 2d8'."""
    if not damage_str or "Урон:" not in damage_str:
        return 0

    try:
        # Извлекаем часть после "Урон:"
        dice_part = damage_str.split(":")[1].strip()

        if "единицы" in dice_part:
            num = int(dice_part.split("x")[0])
            return num * 5  # 5 ОП за каждую единицу урона
        else:
            num, dice_type = dice_part.split("x")
            num = int(num)

            if dice_type == "d4":
                return 5 if num == 1 else (num - 1) * 20 + 5
            elif dice_type == "d6":
                return 10 if num == 1 else (num - 1) * 25 + 10
            elif dice_type == "de":
                return num * 25
            elif dice_type == "d8":
                return 20 if num == 1 else (num - 1) * 30 + 20
            elif dice_type == "d10":
                return 30 if num == 1 else (num - 1) * 35 + 30
            elif dice_type == "d12":
                return num * 40
    except:
        return 0

def calculate_healing_cost(healing_str):
    """Рассчитывает стоимость лечения по формату 'Лечение: 3d6'."""
    if not healing_str or "Лечение:" not in healing_str:
        return 0

    try:
        # Извлекаем часть после "Лечение:"
        dice_part = healing_str.split(":")[1].strip()

        if "единицы" in dice_part:
            num = int(dice_part.split("x")[0])
            return num * 4  # 4 ОП за каждую единицу лечения
        else:
            num, dice_type = dice_part.split("x")
            num = int(num)

            if dice_type == "d4":
                return 5 if num == 1 else (num - 1) * 20 + 5
            elif dice_type == "d6":
                return 10 if num == 1 else (num - 1) * 25 + 10
            elif dice_type == "de":
                return num * 25
            elif dice_type == "d8":
                return 20 if num == 1 else (num - 1) * 30 + 20
            elif dice_type == "d10":
                return 30 if num == 1 else (num - 1) * 35 + 30
            elif dice_type == "d12":
                return num * 40
    except:
        return 0


class FinalSummaryScreen(Screen):
    """Финальный экран с исправленным отображением текста"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = FloatLayout()

        # Основной контейнер с прокруткой
        self.scroll = ScrollView(
            size_hint=(0.95, 0.75),
            pos_hint={'center_x': 0.5, 'top': 0.85},
            do_scroll_x=False,  # Отключаем горизонтальную прокрутку
            bar_width=10
        )

        # Контейнер для текста
        self.text_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=[20, 10],
            spacing=10
        )
        self.text_layout.bind(minimum_height=self.text_layout.setter('height'))

        self.scroll.add_widget(self.text_layout)
        self.layout.add_widget(self.scroll)

        # Кнопки
        btn_layout = BoxLayout(
            size_hint=(0.9, 0.1),
            pos_hint={'center_x': 0.5, 'y': 0.02},
            spacing=10
        )

        self.btn_restart = Button(text="Новая способность")
        self.btn_save = Button(text="Сохранить PNG")
        self.btn_exit = Button(text="Выход")

        btn_layout.add_widget(self.btn_restart)
        btn_layout.add_widget(self.btn_save)
        btn_layout.add_widget(self.btn_exit)

        self.layout.add_widget(btn_layout)
        self.add_widget(self.layout)

        # Привязка событий
        self.btn_restart.bind(on_press=self.restart_creation)
        self.btn_save.bind(on_press=self.save_as_png)
        self.btn_exit.bind(on_press=self.finish)

    def on_pre_enter(self):
        """Обновляем содержимое перед показом экрана"""
        self.text_layout.clear_widgets()

        app = App.get_running_app()
        user_data = getattr(app, "user_data", {})

        # Получаем данные
        name = user_data.get("entry_name", "Без названия")
        description = user_data.get("entry_description", "Нет описания")
        total_op, effect_details = calculate_total_op(user_data)

        # Создаем текстовые блоки с переносами
        name_label = Label(
            text=f"[size=28][b]{name}[/b][/size]",
            size_hint_y=None,
            height=60,
            halign='center',
            valign='middle',
            color=(0.9, 0.9, 0.9, 1),
            markup=True
        )

        desc_label = Label(
            text=f"[size=20]{description}[/size]",
            size_hint_y=None,
            height=self.calculate_text_height(description, 60),
            halign='left',
            valign='top',
            text_size=(Window.width * 0.9, None),
            markup=True
        )

        params_label = Label(
            text=self.format_effects(effect_details),
            size_hint_y=None,
            height=self.calculate_effects_height(effect_details),
            halign='left',
            valign='top',
            text_size=(Window.width * 0.9, None),
            markup=True
        )

        total_label = Label(
            text=f"[size=24][b]Общая стоимость: [color=#4CAF50]{total_op} ОП[/color][/b][/size]",
            size_hint_y=None,
            height=60,
            halign='center',
            valign='middle',
            markup=True
        )

        self.text_layout.add_widget(name_label)
        self.text_layout.add_widget(desc_label)
        self.text_layout.add_widget(params_label)
        self.text_layout.add_widget(total_label)

    def calculate_text_height(self, text, min_height):
        """Вычисляем высоту текста с учетом переносов"""
        label = Label(text=text, text_size=(Window.width * 0.9, None))
        label.texture_update()
        return max(label.texture_size[1] + 20, min_height)

    def calculate_effects_height(self, effects):
        """Вычисляем высоту блока с эффектами"""
        text = self.format_effects(effects)
        label = Label(text=text, text_size=(Window.width * 0.9, None))
        label.texture_update()
        return label.texture_size[1] + 20

    def format_effects(self, effects):
        """Форматируем список эффектов для отображения"""
        if not effects:
            return "Параметры не указаны"

        formatted = "[size=16][b]Параметры:[/b][/size]\n"
        for param, cost in effects.items():
            formatted += f"• {param}: [b]{cost} ОП[/b]\n"
        return formatted

    def restart_creation(self, instance):
        """Сброс всех данных и перезапуск."""
        app = App.get_running_app()
        app.user_data.clear()
        self.manager.current = "creation"

    def finish(self, instance):
        """Завершение работы приложения."""
        App.get_running_app().stop()

    def save_as_png(self, instance):
        """Сохраняет текущий экран в виде PNG-изображения."""
        # Получаем название способности из user_data
        app = App.get_running_app()
        ability_name = app.user_data.get("entry_name", "ability_summary").strip()

        # Убираем недопустимые символы для имени файла
        valid_chars = "-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        ability_name = "".join(c for c in ability_name if c in valid_chars)

        # Если название пустое, используем имя по умолчанию
        if not ability_name:
            ability_name = "ability_summary"

        # Указываем имя файла
        filename = f"{ability_name}.png"

        # Добавляем фон перед сохранением
        with self.canvas.before:
            Color(*BG_COLOR)  # Используем цвет фона, определенный в начале файла
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)

        # Сохраняем текущий экран в PNG
        try:
            self.export_to_png(filename)

            # Убираем фон после сохранения
            self.canvas.before.remove(self.bg_rect)

            # Показываем сообщение об успешном сохранении
            popup = Popup(
                title="Сохранение",
                content=Label(text=f"Сводка сохранена как {filename}"),
                size_hint=(0.6, 0.3),
            )
            popup.open()
        except Exception as e:
            # Если произошла ошибка, показываем сообщение
            popup = Popup(
                title="Ошибка",
                content=Label(text=f"Не удалось сохранить файл: {str(e)}"),
                size_hint=(0.6, 0.3),
            )
            popup.open()



def calculate_duration_cost(duration):
    """Рассчитывает стоимость ОП за продолжительность."""
    if "Раунд" in duration:  # Проверяем, содержит ли строка "Раунд"
        rounds = int(re.findall(r'\d+', duration)[0]) if re.findall(r'\d+', duration) else 1
        return 5 + (rounds - 1) * 10  # Базовая стоимость 5 ОП + 10 ОП за каждый дополнительный раунд
    elif "Минут" in duration:  # Проверяем, содержит ли строка "Минут"
        minutes = int(re.findall(r'\d+', duration)[0]) if re.findall(r'\d+', duration) else 1
        return 50 + minutes * 20  # Базовая стоимость 50 ОП + 20 ОП за каждую минуту
    elif "Час" in duration:  # Проверяем, содержит ли строка "Час"
        hours = int(re.findall(r'\d+', duration)[0]) if re.findall(r'\d+', duration) else 1
        return 120 + hours * 30  # Базовая стоимость 120 ОП + 30 ОП за каждый час
    elif duration == "До конца сцены":
        return 40  # Фиксированная стоимость 40 ОП
    elif duration == "Постоянное действие":
        return 350  # Фиксированная стоимость 350 ОП
    return 0  # Для моментальных эффектов

def calculate_total_op(user_data):
    """Рассчитывает общую стоимость ОП с учетом всех элементов."""
    effects = user_data.get("selected_effects", [])

    # Инициализация переменных для хранения результатов
    effect_details = {}
    total_op = 0

    # Обработка параметров
    action_type = user_data.get("spinner_action_type", "Основное")
    target_area = user_data.get("spinner_action_area",
                                user_data.get("target_area", "Одна цель"))
    duration = user_data.get("spinner_duration", "Моментально")
    probability = user_data.get("spinner_probability", "Проверка")
    range_value = int(user_data.get("entry_range", "1") or 1)

    # Стоимость параметров
    action_costs = {
        "Основное": 0,
        "Бонусное действие": 15,
        "Ответное действие": 20,
        "Свободное действие": 35,
    }

    probability_costs = {
        "Проверка": 0,
        "Автоматический успех": 40,
        "Состязание": 20,
    }

    # Расчет стоимости параметров
    total_op += action_costs.get(action_type, 0)
    effect_details[f"Тип действия: {action_type}"] = action_costs.get(action_type, 0)

    # Область действия
    if target_area == "На себя":
        cost = 0
    elif target_area == "Одна цель":
        cost = 10
    elif target_area.startswith("Несколько целей"):
        # Извлекаем количество целей из строки, например, "Несколько целей (3)"
        num_targets = int(re.findall(r'\d+', target_area)[0]) if re.findall(r'\d+', target_area) else 2
        cost = 10 + (num_targets - 1) * 5  # Базовая стоимость 10 ОП + 5 ОП за каждую дополнительную цель
    elif target_area.startswith("Площадь"):
        # Извлекаем размер площади и дальность перемещения (если есть)
        area_size = int(re.findall(r'\d+', target_area)[0]) if re.findall(r'\d+', target_area) else 3
        cost = (area_size // 3) * 10  # Базовая стоимость: 10 ОП за каждые 3 м²

        # Если включено перемещение, добавляем стоимость
        if "перемещение" in target_area:
            move_range = int(re.findall(r'\d+', target_area.split("перемещение")[-1])[0]) if re.findall(r'\d+',
                                                                                                        target_area.split(
                                                                                                            "перемещение")[
                                                                                                            -1]) else 3
            cost += (move_range // 3) * 5  # 5 ОП за каждые 3 м дальности перемещения
    else:
        cost = 0

    effect_details[f"Область действия: {target_area}"] = cost
    total_op += cost

    duration_cost = calculate_duration_cost(duration)
    # Продолжительность
    effect_details[f"Продолжительность: {duration}"] = duration_cost
    total_op += duration_cost

    # Вероятность успеха
    total_op += probability_costs.get(probability, 0)
    effect_details[f"Вероятность успеха: {probability}"] = probability_costs.get(probability, 0)

    # Дальность
    if 2 <= range_value <= 50:
        total_op += range_value
        effect_details[f"Дальность: {range_value} м"] = range_value
    elif 51 <= range_value <= 100:
        total_op += 50 + (range_value - 50) // 5
        effect_details[f"Дальность: {range_value} м"] = 50 + (range_value - 50) // 5
    elif 101 <= range_value <= 300:
        total_op += 60 + (range_value - 100) // 10
        effect_details[f"Дальность: {range_value} м"] = 60 + (range_value - 100) // 10
    elif range_value > 300:
        total_op += 80 + (range_value - 300) // 50
        effect_details[f"Дальность: {range_value} м"] = 80 + (range_value - 300) // 50
    elif range_value == 0 or 1:
        total_op += 0
        effect_details[f"Дальность: {range_value} м"] = 0
    else:
        total_op += 100
        effect_details[f"Дальность: {range_value} м"] = 100

    print("Effects before calculation:", effects)
    # Обработка эффектов
    for effect in effects:
        try:
            # Обработка призыва существ
            if "Создание существа" in effect:
                creatures = user_data.get("created_creatures", [])
                for creature in creatures:
                    effect_details[
                        f"Создание существа: {creature['name']} (ПО: {creature['po']}, {creature['control']})"
                    ] = creature['cost']
                    total_op += creature['cost']

            # Обработка превращения
            elif "Превращение" in effect:
                transformations = user_data.get("transformations", [])
                for transform in transformations:
                    cost = transform['po'] * 25
                    effect_details[f"Превращение: {transform['name']} (ПО: {transform['po']})"] = cost
                    total_op += cost

            # Обработка дополнительных действий
            elif "Доп. действия" in effect:
                actions = effect.split(":")[-1].strip().split(", ")
                cost = len(actions) * 25  # 25 ОП за каждое дополнительное действие
                effect_details[f"Доп. действия: {', '.join(actions)}"] = cost
                total_op += cost

            elif "Перемещение" in effect:
                distance = int(re.findall(r'\d+', effect)[0]) if re.findall(r'\d+', effect) else 0
                if distance <= 5:
                    cost = distance * 5
                elif distance <= 15:
                    cost = distance * 3
                elif distance <= 50:
                    cost = distance * 2
                elif distance <= 100:
                    cost = 100 + (distance - 50)
                else:
                    cost = 300
                effect_details[f"Перемещение: {distance} м"] = cost
                total_op += cost

            # Обработка дескрипторов
            elif "Дескрипторы" in effect:
                descriptors = effect.split(":")[-1].strip().split(", ")
                cost = len(descriptors) * 20  # 20 ОП за каждый дескриптор
                effect_details[f"Дескрипторы: {', '.join(descriptors)}"] = cost
                total_op += cost

            # Обработка бонусов и штрафов
            elif "Бонусы/Штрафы" in effect:
                bonuses = user_data.get("bonuses", [])
                for bonus in bonuses:
                    characteristic = bonus["characteristic"]
                    value = bonus["value"]
                    absolute_value = bonus["absolute_value"]

                    # Расчет стоимости по формуле: (|value| - 1) * 15 + 20
                    cost = (absolute_value - 1) * 15 + 20

                    # Определяем тип (бонус или штраф)
                    effect_type = "Бонус" if value > 0 else "Штраф"

                    # Формируем запись с указанием типа
                    effect_details[f"{effect_type}: {characteristic}: {value}"] = cost
                    total_op += cost


            # Обработка щитов
            elif "Щит" in effect:
                value = int(re.findall(r'\d+', effect)[0]) if re.findall(r'\d+', effect) else 10
                cost = value * 2 + 20
                effect_details[f"Щит: {effect}"] = cost
                total_op += cost

            # Обработка баррикад
            elif "Баррикада" in effect:
                value = int(re.findall(r'\d+', effect)[0]) if re.findall(r'\d+', effect) else 10
                cost = value + 20  # Введенное количество + 20
                effect_details[f"Баррикада: {effect}"] = cost
                total_op += cost

            #uron i lechenie
            elif "Урон" in effect:
                cost = calculate_damage_cost(effect)
                effect_details[effect] = cost
                total_op += cost
            elif "Лечение" in effect:
                cost = calculate_healing_cost(effect)
                effect_details[effect] = cost
                total_op += cost

            # Обработка прочих эффектов
            elif "Прочие эффекты" in effect:
                effects_list = effect.split(":")[-1].strip().split(", ")
                cost = len(effects_list) * 20  # 20 ОП за каждый эффект
                effect_details[f"Прочие эффекты: {', '.join(effects_list)}"] = cost
                total_op += cost

            # Обработка ограничений
            elif "Ограничения" in effect:
                restrictions = effect.split(":")[-1].strip().split(", ")
                discount = sum(map(int, re.findall(r"-\d+", " ".join(restrictions))))
                total_op = max(total_op - abs(discount), 10)  # Применяем скидку
                effect_details[f"Ограничения: {', '.join(restrictions)}"] = discount

        except ValueError:
            # Если что-то пошло не так (например, некорректный ввод), стоимость = 0
            effect_details[effect] = 0
            total_op += 0

    return total_op, effect_details


class AbilityApp(App):
    def build(self):
        sm = ThemedScreenManager()
        sm.add_widget(AbilityCreationScreen(name="creation"))
        sm.add_widget(TargetSelectionScreen(name="target"))
        sm.add_widget(ActionSelectionScreen(name="action"))
        sm.add_widget(MovementSelectionScreen(name="movement"))
        sm.add_widget(DurationSelectionScreen(name="duration"))
        sm.add_widget(ProbabilitySelectionScreen(name="probability"))
        sm.add_widget(RangeSelectionScreen(name="range"))
        sm.add_widget(EffectsSelectionScreen(name="effects"))
        sm.add_widget(DamageSelectionScreen(name="damage"))
        sm.add_widget(HealingSelectionScreen(name="healing"))
        sm.add_widget(ExtraActionSelectionScreen(name="extra_action"))
        sm.add_widget(ExtraActionDescriptionScreen(name="extra_action_desc"))
        sm.add_widget(DescriptorsSelectionScreen(name="descriptors"))
        sm.add_widget(BonusesSelectionScreen(name="bonuses"))
        sm.add_widget(CreatureCreationScreen(name="creature"))
        sm.add_widget(TransformationScreen(name="transformation"))
        sm.add_widget(ShieldSelectionScreen(name="shield"))
        sm.add_widget(ShieldConfigScreen(name="shield_config"))
        sm.add_widget(BarrierConfigScreen(name="barrier_config"))
        sm.add_widget(OtherEffectsScreen(name="other_effects"))
        sm.add_widget(RestrictionScreen(name="restriction"))
        sm.add_widget(FinalSummaryScreen(name="final_summary"))
        return sm


if __name__ == "__main__":
    AbilityApp().run()

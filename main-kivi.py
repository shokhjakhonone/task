from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput


class CalculatorApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        self.text_input = TextInput(font_size=40, size_hint=(1, 0.5))
        layout.add_widget(self.text_input)

        buttons = [
            ['7', '8', '9', '/'],
            ['4', '5', '6', '*'],
            ['1', '2', '3', '-'],
            ['0', '.', '=', '+'],
            ['C']
        ]

        for row in buttons:
            button_row = BoxLayout()
            for label in row:
                button = Button(text=label, font_size=40)
                button.bind(on_press=self.on_button_press)
                button_row.add_widget(button)
            layout.add_widget(button_row)

        return layout

    def on_button_press(self, instance):
        current_text = self.text_input.text
        button_text = instance.text

        if button_text == '=':
            try:
                result = str(eval(current_text, {}, {}))
                self.text_input.text = result
            except:
                self.text_input.text = 'Error'
        elif button_text == 'C':
            self.text_input.text = ''
        else:
            self.text_input.text = current_text + button_text


if __name__ == '__main__':
    CalculatorApp().run()

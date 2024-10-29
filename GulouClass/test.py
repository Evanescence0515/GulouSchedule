from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label

class TestApp(App):
    def build(self):
        return  Button(text="show", on_press=self.anim_btn)

    def anim_btn(self, *args):
        popup = Popup(title='Test popup', 
            content=Label(text='Hello world'), 
            size_hint=(None, None), 
            size=(400, 400),
            separator_color=[.9,.4,.2,1],
        ).open()

if __name__ == "__main__":
    TestApp().run()
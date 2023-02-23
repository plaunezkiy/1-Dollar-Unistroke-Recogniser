from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Ellipse, Line, Rectangle
import numpy as np
from recogniser import StrokePoint, OneDollarRecogniser


class StrokeCanvasWidget(Widget):
    stroke = None
    recogniser = None

    def __init__(self, *args, **kwargs):
        self.recogniser = OneDollarRecogniser()
        super().__init__(*args, **kwargs)

    def train(self, label):
        points = self.get_stroke_points()
        self.recogniser.train(label, points)
    
    def recognise(self):
        points = self.get_stroke_points()
        print(self.recogniser.recongise(points))
    
    def clear_canvas(self):
        self.canvas.clear()

    def on_touch_down(self, touch):
        if Widget.on_touch_down(self, touch):
            return True
        with self.canvas:
            # Draw the starting point in yellow
            Color(1,1,0)
            d = 10
            Ellipse(pos=(touch.x-d/2, touch.y-d/2), size=(d, d))
            # Change color to white and start the line
            Color(1, 1, 1)
            touch.ud["line"] = Line(points=(touch.x, touch.y))
            self.stroke = touch.ud["line"]
    
    def on_touch_move(self, touch):
        # As the stroke keeps going, keep adding points to the line
        touch.ud["line"].points += [touch.x, touch.y]
        with self.canvas:
            # Mark every point in green to show that the point has been
            Color(0.3, 0.8, 0)
            d = 4
            Ellipse(pos=(touch.x-d/2, touch.y-d/2), size=(d, d))

    def get_stroke_points(self):
        # if the stroke is recorded, return the points
        if self.stroke:
            points = self.tupelize_points(self.stroke.points)
            return points
        return []
    
    def tupelize_points(self, points):
        """
        [x0, y0, x1, y1] -> [(x0, y0), (x1, y1)]
        takes a continuous array of stroke points and coverts
        it into an array of StrokePoint objects
        """
        a = iter(points)
        to_stroke_point = lambda point: StrokePoint([point[0], point[1]])
        return list(map(to_stroke_point, zip(a, a)))
    
    def on_touch_up(self, touch):
        return
        # points = self.get_stroke_points()
        # recogniser = OneDollarRecogniser()
        # resampled_points = recogniser.resample(points)
        # with self.canvas.before:
        #     Color(1, 0.5, 0.5)
        #     for point in resampled_points:
        #         d = 3
        #         Ellipse(pos=(point.x-d/2, point.y-d/2), size=(d, d))
            # centroid = recogniser.calculate_centroid(resampled_points)
            # Ellipse(pos=(centroid.x, centroid.y), size=(10, 10))
            # angle = recogniser.calculate_indicative_angle(resampled_points, centroid)
            # # rotate
            # r_points = recogniser.rotate_by(resampled_points, centroid, angle)
            # # scale
            # s_points = recogniser.scale(r_points)
            # s_centroid = recogniser.calculate_centroid(s_points)
            # # translate
            # t_points = recogniser.translate(s_points, s_centroid)
            # Ellipse(pos=(centroid.x, centroid.y))
            # Line(points=list(np.concatenate(t_points)))



class OneDollarRecongniserApp(App):
    draw_mode = True

    def switch_mode(self, button):
        if self.draw_mode:
            self.draw_mode = False
            button.text = "Train Mode"
        else:
            self.draw_mode = True
            button.text = "Draw Mode"

    def build(self):
        main = FloatLayout()

        canvas = StrokeCanvasWidget()
        canvas.bind(size=self._update_rect, pos=self._update_rect)
        with canvas.canvas.before:
            Color(1,1,1)
            self.rect = Rectangle(size=canvas.size, pos=canvas.pos)
        # canvas.bind(size=self._update_rect, pos=self._update_rect)
        
        mode_switch_controls = BoxLayout(size_hint=(1, 0.1), pos_hint={'top': 1.0})
        mode_button = Button(text="Draw Mode")
        mode_button.bind(on_release=lambda b: self.switch_mode(b))
        mode_switch_controls.add_widget(mode_button)

        controls = BoxLayout(size_hint=(1, 0.1), pos_hint={'bottom': 1.0})
        label_input = TextInput()

        trn_button = Button(text="Train")
        trn_button.bind(on_release=lambda _: canvas.train(label_input.text))
        
        rcg_button = Button(text="Recognise")
        rcg_button.bind(on_release=lambda _: canvas.recognise())

        clr_button = Button(text="Clear")
        clr_button.bind(on_release=lambda _: canvas.clear_canvas())

        controls.add_widget(label_input)
        controls.add_widget(trn_button)
        controls.add_widget(rcg_button)
        controls.add_widget(clr_button)
        
        main.add_widget(canvas)
        main.add_widget(mode_switch_controls)
        main.add_widget(controls)

        return main
    
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


if __name__ == "__main__":
    OneDollarRecongniserApp().run()

from math import sqrt, atan2, cos, sin, radians
import numpy as np
import os
import matplotlib.pyplot as plt


class StrokePoint(np.ndarray):
    def __new__(cls, input_array, your_new_attr=None):        
        obj = np.asarray(input_array).view(cls)
        # obj.x = input_array[0]
        # obj.y = input_array[1]
        return obj
    
    @property
    def get_x(self):
        return self.x

    @property
    def get_y(self):
        return self.y 

    def __array_finalize__(self, obj):
        if obj is None: return
        # self.x = getattr(obj, 'x', None)
        # self.y = getattr(obj, 'y', None)
    
    def get_distance(self, point):
        return sqrt((point[0] - self[0]) ** 2 + (point[1] - self[1]) ** 2)
    
    def to_cont_array(self):
        return 


class OneDollarRecogniser(object):
    PHI = (1 + sqrt(5)) / 2
    # number of normalised points
    N = 64
    # side of the scaled square in px
    SIZE = 250
    indicative_angle = 0
    centroid = (None, None)
    points = []
    resampled_points = []

    def normalise(self, points):
        res_points = self.resample(points)
        centroid = self.calculate_centroid(res_points)
        angle = self.calculate_indicative_angle(res_points, centroid)
        # rotate
        r_points = self.rotate_by(res_points, centroid, angle)
        # scale
        s_points = self.scale(r_points)
        s_centroid = self.calculate_centroid(s_points)
        # translate
        t_points = self.translate(s_points, s_centroid)
        t_points = s_points

        return t_points

    def train(self, label, points):
        normalised_points = self.normalise(points)
        with open(f"templates/{label}.txt", "w") as template:
            template.write(label + "\n")
            for point in normalised_points:
                template.write(f"{point[0]},{point[1]}\n")

    def recongise(self, points):
        normalised_points = self.normalise(points)
        return self.match_to_template(normalised_points)

    def resample(self, points):
        """
        Resample the stroke points to get an array of 
        N equidistant points representing the stroke
        """
        x_min = min(points, key=lambda p: p[0])[1]
        y_min = min(points, key=lambda p: p[1])[1]
        for point in points:
            point[0] -= x_min
            point[1] -= y_min

        # Clear the array
        resampled_points = []
        # M = total stroke length
        M = 0
        for i in range(1, len(points)):
            M += points[i].get_distance(points[i-1])
        # I = length of a single increment
        I = M / (self.N - 1)
        D = 0
        clone_points = points[:]
        resampled_points.append(clone_points[0])
        
        i = 1
        while i < len(clone_points):
            # not using `point` because the enumeration is overwritten by inserts
            if i > 0:
                prev_point = clone_points[i-1]
                d = clone_points[i].get_distance(prev_point)
                if (d + D) >= I:
                    # Interpolate (I - D to account for the already covered distance)
                    qx = clone_points[i-1][0] + (I - D) * (clone_points[i][0] - clone_points[i-1][0]) / d
                    qy = clone_points[i-1][1] + (I - D) * (clone_points[i][1] - clone_points[i-1][1]) / d
                    q = StrokePoint([qx, qy])
                    resampled_points.append(q)
                    clone_points.insert(i, q)
                    # reset the running length
                    D = 0
                else:
                    D += d
            i += 1
        if len(resampled_points) == self.N - 1:
            resampled_points.append(clone_points[-1])
        return resampled_points

    def rotate_by(self, points, centroid, indicative_angle):
        """
        Rotates the stroke to align the centroid 
        and the first point at 0 degrees
        """
        rotated_points = []
        for point in points:
            qx = (point[0] - centroid[0]) * cos(indicative_angle) - (point[1] - centroid[1]) * sin(indicative_angle) + centroid[0]
            qy = (point[0] - centroid[0]) * sin(indicative_angle) + (point[1] - centroid[1]) * cos(indicative_angle) + centroid[1]
            rotated_points.append(StrokePoint([qx, qy]))
        return rotated_points
    
    def scale(self, points):
        """
        Scales the stroke to fit into a box of 
        given `width` and `height`
        """
        x_max = max(points, key=lambda p: p[0])[0]
        x_min = min(points, key=lambda p: p[0])[0]
        y_max = max(points, key=lambda p: p[1])[1]
        y_min = min(points, key=lambda p: p[1])[1]

        x_factor = self.SIZE / (x_max - x_min)
        y_factor = self.SIZE / (y_max - y_min)

        multiplier = StrokePoint([x_factor, y_factor])
        points *= multiplier
        return points

    def translate(self, points, centroid):
        """
        Translate the stroke to put the centroid at the origin
        """
        points -= centroid
        return points
    
    def match_to_template(self, points):
        """
        Loops through the templates and returns the highest
        probability of the stroke being the template and the template
        """
        b = float("inf")
        T = ""
        d = 0
        templates = {}
        t_path = os.path.join(os.getcwd(), "templates")
        for root, dirs, files in os.walk(t_path):
            for name in files:
                # load strokes
                strk_list = []
                with open(os.path.join(t_path, name), 'r') as f:
                    label = next(f).strip()
                    for line in f:
                        # clear linebreaks and split + convert to StrokePoints
                        point_str = line.strip().split(',')
                        point = StrokePoint([float(point_str[0]), float(point_str[1])])
                        strk_list.append(point)
            
                templates[label] = strk_list
                centroid = self.calculate_centroid(points)
                # For rotation invariance, try out angles to find the one with lowest distance
                for angle in range(-45, 45, 2):
                    r_points = self.rotate_by(points, centroid, radians(angle))
                    for t_point, r_point in zip(strk_list, r_points):
                        d += t_point.get_distance(r_point)
                    d /= self.SIZE
                    # Uncomment for visualisations
                    # plt.title(f"{label}, {angle}, {round(d, 2)}")
                    # plt.scatter(*zip(*strk_list))
                    # plt.scatter(*zip(*r_points))
                    # plt.show()
                    if d < b:
                        b = d
                        T = label
            score = 1 - b / (1/2 * sqrt(2) * self.SIZE)
            return (T, score)

    def calculate_centroid(self, points):
        """
        Based on a set of stroke points,
        calculate the centroid of the shape
        """
        x_sum = 0
        y_sum = 0
        for point in points:
            x_sum += point[0]
            y_sum += point[1]
        return StrokePoint([x_sum / self.N, y_sum / self.N])
    
    def calculate_indicative_angle(self, points, centroid):
        """
        Calculates the indicative angle of the stroke
        """
        first_point = points[0]
        return atan2(centroid[1] - first_point[1], centroid[0] - first_point[0])

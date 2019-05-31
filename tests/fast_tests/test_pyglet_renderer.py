from flow.renderer.pyglet_renderer import PygletRenderer as Renderer
import os
import unittest

os.environ['TEST_FLAG'] = 'True'


class TestPygletRenderer(unittest.TestCase):
    """Tests pyglet_renderer"""

    def test_pyglet_renderer(self):
        # Ring road network polygons
        network = \
            [[36.64, -1.6500000000000001, 38.15, -1.62, 39.69, -1.52,
              41.22, -1.37, 42.74, -1.1500000000000001, 44.26, -0.88, 45.77,
              -0.53, 47.25, -0.13, 48.72, 0.32, 50.17, 0.84, 51.61, 1.41,
              53.01, 2.05, 54.39, 2.74, 55.730000000000004, 3.48,
              57.050000000000004, 4.2700000000000005, 58.34, 5.12, 59.59, 6.03,
              60.800000000000004, 6.98, 61.97, 7.97, 63.11, 9.02, 64.2, 10.11,
              65.25, 11.25, 66.24, 12.42, 67.19, 13.63, 68.1, 14.88, 68.95,
              16.17, 69.74, 17.490000000000002, 70.48, 18.830000000000002,
              71.17, 20.21, 71.81, 21.61, 72.38, 23.05, 72.9, 24.5,
              73.35000000000001, 25.97, 73.75, 27.45, 74.10000000000001,
              28.96, 74.37, 30.48, 74.59, 32.0, 74.74, 33.53, 74.84, 35.07,
              74.87, 36.58],
             [-1.6500000000000001, 36.58, -1.62, 35.07, -1.52, 33.53, -1.37,
              32.0, -1.1500000000000001, 30.48, -0.88, 28.96, -0.53, 27.45,
              -0.13, 25.97, 0.32, 24.5, 0.84, 23.05, 1.41, 21.61, 2.05, 20.21,
              2.74, 18.830000000000002, 3.48, 17.490000000000002,
              4.2700000000000005, 16.17, 5.12, 14.88, 6.03, 13.63, 6.98, 12.42,
              7.97, 11.25, 9.02, 10.11, 10.11, 9.02, 11.25, 7.97, 12.42, 6.98,
              13.63, 6.03, 14.88, 5.12, 16.17, 4.2700000000000005,
              17.490000000000002, 3.48, 18.830000000000002, 2.74, 20.21, 2.05,
              21.61, 1.41, 23.05, 0.84, 24.5, 0.32, 25.97, -0.13, 27.45,
              -0.53, 28.96, -0.88, 30.48, -1.1500000000000001, 32.0, -1.37,
              33.53, -1.52, 35.07, -1.62, 36.58, -1.6500000000000001],
             [74.87, 36.64, 74.84, 38.15, 74.74, 39.69, 74.59, 41.22, 74.37,
              42.74, 74.10000000000001, 44.26, 73.75, 45.77, 73.35000000000001,
              47.25, 72.9, 48.72, 72.38, 50.17, 71.81, 51.61, 71.17, 53.01,
              70.48, 54.39, 69.74, 55.730000000000004, 68.95,
              57.050000000000004, 68.1, 58.34, 67.19, 59.59, 66.24,
              60.800000000000004, 65.25, 61.97, 64.2, 63.11, 63.11, 64.2,
              61.97, 65.25, 60.800000000000004, 66.24, 59.59, 67.19, 58.34,
              68.1, 57.050000000000004, 68.95, 55.730000000000004, 69.74,
              54.39, 70.48, 53.01, 71.17, 51.61, 71.81, 50.17, 72.38, 48.72,
              72.9, 47.25, 73.35000000000001, 45.77, 73.75, 44.26,
              74.10000000000001, 42.74, 74.37, 41.22, 74.59, 39.69, 74.74,
              38.15, 74.84, 36.64, 74.87],
             [36.58, 74.87, 35.07, 74.84, 33.53, 74.74, 32.0, 74.59, 30.48,
              74.37, 28.96, 74.10000000000001, 27.45, 73.75, 25.97,
              73.35000000000001, 24.5, 72.9, 23.05, 72.38, 21.61, 71.81, 20.21,
              71.17, 18.830000000000002, 70.48, 17.490000000000002, 69.74,
              16.17, 68.95, 14.88, 68.1, 13.63, 67.19, 12.42, 66.24, 11.25,
              65.25, 10.11, 64.2, 9.02, 63.11, 7.97, 61.97, 6.98,
              60.800000000000004, 6.03, 59.59, 5.12, 58.34, 4.2700000000000005,
              57.050000000000004, 3.48, 55.730000000000004, 2.74, 54.39, 2.05,
              53.01, 1.41, 51.61, 0.84, 50.17, 0.32, 48.72, -0.13, 47.25,
              -0.53, 45.77, -0.88, 44.26, -1.1500000000000001, 42.74, -1.37,
              41.22, -1.52, 39.69, -1.62, 38.15, -1.6500000000000001, 36.64]]

        # Renderer parameters
        mode = "drgb"
        save_render = False
        sight_radius = 25
        pxpm = 3
        show_radius = True

        # initialize a pyglet renderer
        renderer = Renderer(
            network,
            mode,
            save_render=save_render,
            sight_radius=sight_radius,
            pxpm=pxpm,
            show_radius=show_radius)

        # ensure that the attributes match their correct values
        self.assertEqual(renderer.mode, mode)
        self.assertEqual(renderer.save_render, save_render)
        self.assertEqual(renderer.sight_radius, sight_radius)
        self.assertEqual(renderer.pxpm, pxpm)
        self.assertEqual(renderer.show_radius, show_radius)


if __name__ == '__main__':
    # unittest.main() FIXME
    pass

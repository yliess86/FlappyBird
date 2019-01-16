import numpy as np

class Vector2D:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __eq__(self, vector):
        assert isinstance(vector, Vector2D)
        return self.x == vector.x and self.y == vector.y

    def __neg__(self, vector):
        assert isinstance(vector, Vector2D)
        return not (self == vector)

    def __neg__(self):
        return Vector2D(-self.x, -self.y)

    def __abs__(self):
        return Vector2D(abs(self.x), abs(self.y))

    def __add__(self, vector):
        assert isinstance(vector, Vector2D)
        return Vector2D(self.x + vector.x, self.y + vector.y)

    def __radd__(self, vector):
        assert isinstance(vector, Vector2D)
        return vector + self

    def __iadd__(self, vector):
        assert isinstance(vector, Vector2D)
        self.x += vector.x
        self.y += vector.y
        return self

    def __sub__(self, vector):
        assert isinstance(vector, Vector2D)
        return Vector2D(self.x - vector.x, self.y - vector.y)

    def __rsub__(self, vector):
        assert isinstance(vector, Vector2D)
        return -vector + self

    def __isub__(self, vector):
        assert isinstance(vector, Vector2D)
        self.x -= vector.x
        self.y -= vector.y
        return self

    def __mul__(self, value):
        assert isinstance(value, (int, float))
        return Vector2D(self.x * value, self.y * value)

    def __rmul__(self, value):
        assert isinstance(value, (int, float))
        return self * value

    def __truediv__(self, value):
        assert isinstance(value, (int, float))
        assert value != 0
        return Vector2D(self.x / value, self.y / value)

    def __floordiv__(self, value):
        assert isinstance(value, (int, float))
        assert value != 0
        return Vector2D(self.x // value, self.y // value)

    def __pow__(self, value):
        assert isinstance(value, (int, float))
        return Vector2D(self.x ** value, self.y ** value)

    def dot(self, vector):
        assert isinstance(vector, Vector2D)
        return Vector2D(self.x * vector.x, self.y * vector.y)

    def squared_magnitude(self):
        return self.x ** 2 + self.y ** 2

    def magnitude(self):
        return np.sqrt(self.squared_magnitude())

    def to_tuple(self):
        return (self.x, self.y)

    def __str__(self):
        return f'({self.x} {self.y})'

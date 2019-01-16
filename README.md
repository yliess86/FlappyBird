# ECS: Entity Component System

ECS pour Entity Component System ou Entité Composant Système en français, est un pattern utilisé principalement dans le domaine du jeu vidéo. Il permet une grande souplesse en profitant d'une approche orientée data.

L'intérêt pour nous d'étudier ce système est de comprendre ce qui se trouve derrière la prochaine version de Unity 2019 qui utilisera ce pattern. Unity est aujourd'hui l'un des moteurs de jeux les plus utilisés sur le marché et commence à s'orienter vers la performance par défaut.

Pour aborder les idées de l'ECS, rien de mieux que d'essayer d'implémenter un moteur de jeux simple suivant ce pattern. C'est ce que nous allons faire dans ce tutoriel. Nous allons réaliser ensemble un clone de FlappyBird utilisant le pattern ECS en python.

[![VIDEO](https://i9.ytimg.com/vi_webp/9dG4CCyK9bA/mqdefault.webp?sqp=CLTQ_uEF&rs=AOn4CLCKGNBnZvM8REQNOxju5PWpxiVAtw)](https://www.youtube.com/watch?v=9dG4CCyK9bA)

## Vocabulaire

### Entité

Une entité représente un objet du jeu. Elle ne possède aucune données à proprement parler si ce n'est un indentifiant unique.

### Composant

Les composants quant à eux représentent des propriétés d'un objet telles que sa position, sa vélocité, ... etc. Aucun code n'est présent dans les composants. Ils servent à décrire les données et les entités se caractérisent par un ensemble de composants qui leur sont attachés.

### Système

Un système implémente une fonction update ou process qui s'occupe de parcourir l'ensemble des entités possédant les composants dont ils a besoin, et de transformer ces derniers.

Le plus dur dans le pattern ECS est de changer sa façon de penser. En effet, nous ne sommes pas pour la plupart habitués à ce pattern et pensons de manière object par défaut.

* [I/ ECS Implementation](#ecs_implementation)
* [II/ Vector2D Class](#vector2d_class)
* [III/ FLappyBird Clone](#flappybird_clone)

## I/ ECS Implementation <a name="#ecs_implementation"></a>

Commençons par créer un fichier *ecs.py*. En termes de dépendances, nous avons besoin uniquement de la bibliothèque *lru_cache* pour la gestion du cache.

```python
from lru_cache import _lru_cache
```

Comme nous l'avons dit précédemment, un système implémente uniquement une méthode update ou process. De plus il doit avoir accès au manageur qui lui donnera la possibilité de query les entités dont il a besoin par composants. Ici nous appellerons ce manager *world*.

```python
class System:
    world = None

    def update(self, *args, **kwargs):
        raise NotImplementedError
```

Pour finir l'implémentation de notre système ECS il nous suffit d'implémenter ce fameux manageur. *World* doit être en mesure dans un premier temps d'avoir accès à l'ensemble des sytèmes, des entités et des composants mais aussi du générateur d'ID pour créeer des entités. Nous ajoutons à cette liste un set d'entités nécéssitant d'être détruites puisque cette opération intérviendra à l'itération suivante dans le process.

```python
class World:
    def __init__(self):
        self._systems        = []
        self._next_entity_id = 0
        self._components     = {}
        self._entities       = {}
        self._dead_entities  = set()
```

Ajoutons maintenant à cette classe quelques methodes.
* Ajouter un système
* Supprimer un système
* Accéder à un système

```python
class World:
  ...

  def add_system(self, system_instance, priority=0):
      assert issubclass(system_instance.__class__, System)
      system_instance.priority = priority
      system_instance.world = self
      self._systems.append(system_instance)
      self._systems.sort(key=lambda system: system.priority, reverse=True)

  def remove_system(self, system_type):
      for system in self._systems:
          if type(system) == system_type:
              system.world = None
              self._systems.remove(system)

  def get_system(self, system_type):
      for system in self._systems:
          if type(system) == system_type:
              return system
```

* Ajouter une entité
* Supprimer une entité

```python
class World:
  ...

  def create_entity(self, *components):
        self._next_entity_id += 1
        for component in components:
            self.add_component(self._next_entity_id, component)
        return self._next_entity_id

    def delete_entity(self, entity, immediate=False):
        if immediate:
            for component_type in self._entities[entity]:
                self._components[component_type].discard(entity)

                if not self._components[component_type]:
                    del self._components[component_type]

                del self._entities[entity]
                self.clear_cache()

        else:
            self._dead_entities.add(entity)
```

* Ajouter un composant à une entité
* Supprimer un composant d'une entité

```python
class World:
  ...

  def add_component(self, entity, component_instance):
        component_type = type(component_instance)

        if component_type not in self._components:
            self._components[component_type] = set()

        self._components[component_type].add(entity)

        if entity not in self._entities:
            self._entities[entity] = {}

        self._entities[entity][component_type] = component_instance
        self.clear_cache()

  def remove_component(self, entity, component_type):
      self._components[component_type].discard(entity)

      if not self._components[component_type]:
          del self._components[component_type]

      del self._entities[entity][component_type]

      if not self._entities[entity]:
          del self._entities[entity]

      self.clear_cache()
      return entity

  def has_component(self, entity, component_type):
      return component_type in self._entities[entity]
```


* Query les entités possédant un composant en particulier
* Query les entités possédant un ensemble de composants

C'est à ce moment là que nous utiliserons le cache pour accélerer l'accès aux composants d'entités qui reviennent régulièrement dans les traitements.

```python
class World:
  ...

  def _get_component(self, component_type):
        entity_db = self._entities

        for entity in self._components.get(component_type, []):
            yield entity, entity_db[entity][component_type]

    def _get_components(self, *component_types):
        entity_db    = self._entities
        component_db = self._components

        try:
            for entity in set.intersection(*[component_db[ct] for ct in component_types]):
                yield entity, [entity_db[entity][ct] for ct in component_types]
        except KeyError:
            pass

    @_lru_cache()
    def get_component(self, component_type):
        return [query for query in self._get_component(component_type)]

    @_lru_cache()
    def get_components(self, *component_types):
        return [query for query in self._get_components(*component_types)]
```

* Nettoyer les entités à supprimer

```python
class World:
  ...

  def _clear_dead_entities(self):
        for entity in self._dead_entities:
            for component_type in self._entities[entity]:
                self._components[component_type].discard(entity)

                if not self._components[component_type]:
                    del self._components[component_type]

            del self._entities[entity]

        self._dead_entities.clear()
        self.clear_cache()
```

* Update l'ensemble des systèmes

```python
class World:
  ...

  def _update(self, *args, **kwargs):
        for system in self._systems:
            system.update(*args, **kwargs)

    def update(self, *args, **kwargs):
        self._clear_dead_entities()
        self._update(*args, **kwargs)
```

* Nettoyer l'ensemble des données
* Nettoyer le cache

```python
class World:
  ...

  def clear_cache(self):
      self.get_component.cache_clear()
      self.get_components.cache_clear()

  def clear_database(self):
      self._next_entity_id = 0
      self._dead_entities.clear()
      self._components.clear()
      self._entities.clear()
      self.clear_cache()
```

Nous disposons donc maintenant d'un système d'ECS opérationnel et prêt à l'emploi.

Cette implémentation du pattern ECS n'est pas la plus optimale et ne met pas à profit l'aspect performance de l'ECS. En effet il aurait fallu notamment créer un système de job pour pouvoir distribuer les transformations qu'apportent les systèmes sur les composants sur plusieurs thread. Il y a également des façons d'organiser les databases de composants, d'entités et de systèmes plus optimales. Seulement nous n'irons pas plus loin pour des raisons pédagogiques. Si vous souhaitez en savoir plus n'hésitez pas à vous documenter sur le web, il existe énormément de ressources sur le sujet. Ce tutoriel n'est qu'un innitiation au sujet.

## II/ Vector2D Class <a name="#vector2d_class"></a>

Pour nous faciliter la vie lors de la création du jeu que nous allons réaliser par la suite, créons une classe *Vector2D*. Nous allons pour cela commencer par créer un fichier *maths.py* dans lequel nous implémenterons cette class. Cette class doit intégrer plusieurs methodes qui sont ni plus ni moins qu'un ensemble d'opérations basiques.

```python
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
```

## III/ FLappyBird Clone <a name="#flappybird_clone"></a>

Dans cette dernière partie, je ne vais pas vous détailler tout le code. Vous pourrez retrouver la totalité du code à la fin de cette page. Cependant il y aura assez d'informations, pour vous permettre de comprendre le code dans son entièreté.

Pour creer un jeu en ECS il suffit donc de créer un ensemble de composants et de systèmes puis d'attribuer aux entités ces derniers.

Prenons l'exemple d'un système de gravité. Nous avons besoin pour cela d'un *Transform* contenant la position et la rotation de l'object mais aussi d'un *RigidBody* content la vélocité et l'accélération de ce dernier.

```python
from maths import Vector2D

class TransformComponent(object):
    def __init__(self, x, y, rot=None):
        self.pos = Vector2D(x, y)
        self.rot = rot

class RigidBodyComponent(object):
    def __init__(self, vel_x=0, vel_y=0, acc_x=0, acc_y=0):
        self.vel = Vector2D(vel_x, vel_y)
        self.acc = Vector2D(acc_x, acc_y)
```

Il suffit maintenant d'implémenter un système permettant d'appliquer une transformation sur ces composants.

```python
from ecs import System

class GravitySystem(System):
    def __init__(self, force=-9.8):
        super().__init__()
        self.force = force

    def update(self, *args, **kwargs):
        components = self.world.get_component(RigidBodyComponent)
        if components is None: return

        for ent, rigid in components:
            rigid.acc += Vector2D(0, self.force)

class MovementSystem(System):
    def __init__(self):
        super().__init__()

    def update(self, dt, *args, **kwargs):
        components = self.world.get_components(TransformComponent, RigidBodyComponent)
        if components is None: return

        for ent, (trans, rigid) in components:
            last_vel   = Vector2D(rigid.vel.x, rigid.vel.y)
            rigid.vel += rigid.acc * dt
            trans.pos += 0.5 * (last_vel + rigid.vel) * dt

            rigid.acc = Vector2D()
```

Nous pouvons donc maintenant creer des entités, leur attribuer ces composants et ainsi déclarer les systèmes permettant de leur appliquer ces transformations pour finir par mettre à jour le manageur *world*. Biensûr nous devons prendre en compte que le système de Gravité doit avoir lieu avant celui du mouvement.

```python
from ecs import World
from time import time

world   = World()

gravity = world.add_system(GravitySystem(force=-9.8), priority=1)
gravity = world.add_system(MovementSystem(), priority=0)

player  = world.create_entity(
  TransformComponent(100, 100),
  RigidBodyComponent()
)

last_time = time()

while True:
  current_time = time()
  dt           = current_time - last_time
  last_time    = current_time

  world.update(dt)
```

Ca y est, nous sommes maintenant capables de créer un jeu vidéo en suivant le pattern ECS. Dans le repo git qui suit, vous trouverez l'implémentation complète du clone de FlappyBird. Le code est assez simple à comprendre. Pour des raisons de simplicité, j'ai décidé d'utiliser *Pygame* comme bibliothèque graphique.

[Clone FlappyBird Github](https://github.com/yliess86/FlappyBird)

from functools import lru_cache as _lru_cache

class System:
    world = None

    def update(self, *args, **kwargs):
        raise NotImplementedError

class World:
    def __init__(self):
        self._systems        = []
        self._next_entity_id = 0
        self._components     = {}
        self._entities       = {}
        self._dead_entities  = set()

    def clear_cache(self):
        self.get_component.cache_clear()
        self.get_components.cache_clear()

    def clear_database(self):
        self._next_entity_id = 0
        self._dead_entities.clear()
        self._components.clear()
        self._entities.clear()
        self.clear_cache()

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

    def try_component(entity, component_type):
        if component_type in self._entities[entity]:
            return self._entities[entity][component_type]
        else:
            return None

    def _clear_dead_entities(self):
        for entity in self._dead_entities:
            for component_type in self._entities[entity]:
                self._components[component_type].discard(entity)

                if not self._components[component_type]:
                    del self._components[component_type]

            del self._entities[entity]

        self._dead_entities.clear()
        self.clear_cache()

    def _update(self, *args, **kwargs):
        for system in self._systems:
            system.update(*args, **kwargs)

    def update(self, *args, **kwargs):
        self._clear_dead_entities()
        self._update(*args, **kwargs)

CachedWorld = World

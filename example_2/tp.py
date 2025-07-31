from typing import TypedDict

type EntityID = int
type ComponentID = str
type SystemID = str
type Component = object
type WorldID = str
type System = callable
type EntityMap = dict[EntityID, dict[ComponentID, Component]]
type ComponentMap = dict[ComponentID, dict[EntityID, Component]]
type SystemMap = dict[SystemID, System]

class WorldData(TypedDict):
    entities: EntityMap
    components: ComponentMap
    systems: SystemMap
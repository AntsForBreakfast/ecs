from typing import Iterable
from tp import *

def add_components(
    world: WorldData,
    eid: EntityID,
    components: tuple[tuple[ComponentID, Component], ...],
) -> None:
    for cid, component in components:
        if eid not in world['entities']:
            world['entities'][eid] = {}
        if cid not in world['components']:
            world['components'][cid] = {}

        world['entities'][eid][cid] = component
        world['components'][cid][eid] = component


def add_component(
    world: WorldData,
    eid: EntityID,
    cid: ComponentID,
    component: Component,
) -> None:
    if eid not in world['entities']:
        world['entities'][eid] = {}
    if cid not in world['components']:
        world['components'][cid] = {}

    world['entities'][eid][cid] = component
    world['components'][cid][eid] = component

def remove_entity(
    world: WorldData,
    eid: EntityID,
) -> None:
    emap, cmap = world.get('entities', {}), world.get('components', {})
    if eid in emap:
        del emap[eid]

        for cid, entities in cmap.items():
            if eid in entities:
                del cmap[cid][eid]

def quary_components(
    world: WorldData, cids: tuple[ComponentID, ...]
) -> dict[EntityID, dict[ComponentID, Component]]:
    emap = world.get('entities', {})
    quary = {}
    comp_count = len(cids)

    temp = {}
    for eid, components in emap.items():
        temp = {}

        for cid in cids:
            if cid in components:
                temp[cid] = components[cid]

        if len(temp) == comp_count:
            quary[eid] = {}
            quary[eid] = temp

    return quary

def run_systems(
    world:WorldData, events:Iterable[object], game_state, dt: float
) -> None:
    for system in world['systems'].values():
        system(world, events, game_state, dt)
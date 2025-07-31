from importlib.resources import files
from random import random, choice

import pygame
from pygame.colordict import THECOLORS
from pgcooldown import Cooldown

type EntityID = int
type ComponentID = str
type SystemID = str
type Component = object
type System = callable
type EntityMap = dict[EntityID, dict[ComponentID, Component]]
type ComponentMap = dict[ComponentID, dict[EntityID, Component]]
type SystemMap = dict[SystemID, System]

DISPLAY_SIZE = pygame.Vector2(1920, 1080)
FPS = 60
DT_MAX = 3 / FPS
SPEED = 100
SHRAPNEL_SPEED = 500


def create_surface(
    size: tuple[int, int], fill_color: str | None = None, color_key: str | None = None
) -> pygame.Surface:

    surface = pygame.Surface(size)

    if fill_color is not None:
        surface.fill(fill_color)

    if color_key is not None:
        surface.set_colorkey(color_key)

    return surface


def add_components(
    emap: EntityMap,
    cmap: ComponentMap,
    eid: EntityID,
    components: tuple[tuple[ComponentID, Component], ...],
) -> tuple[EntityMap, ComponentMap]:
    for cid, component in components:
        if eid not in emap:
            emap[eid] = {}
        if cid not in cmap:
            cmap[cid] = {}

        emap[eid][cid] = component
        cmap[cid][eid] = component

    return emap, cmap


def add_component(
    emap: EntityMap,
    cmap: ComponentMap,
    eid: EntityID,
    cid: ComponentID,
    component: Component,
) -> tuple[EntityMap, ComponentMap]:
    if eid not in emap:
        emap[eid] = {}
    if cid not in cmap:
        cmap[cid] = {}

    emap[eid][cid] = component
    cmap[cid][eid] = component

    return emap, cmap


def remove_entity(
    emap: EntityMap,
    cmap: ComponentMap,
    eid: EntityID,
) -> tuple[EntityMap, ComponentMap]:
    if eid in emap:
        del emap[eid]

        for cid, entities in cmap.items():
            if eid in entities:
                del cmap[cid][eid]

    return emap, cmap


def make_square(
    emap: EntityMap,
    cmap: ComponentMap,
    eid: EntityID,
    pos: pygame.Vector2,
    boundary: pygame.FRect,
    audio: pygame.Sound,
) -> tuple[EntityMap, ComponentMap]:
    speed = pygame.Vector2(1, 0).rotate(random() * 360) * SPEED
    image = create_surface((16, 16), choice(list(THECOLORS)))
    lifetime = Cooldown(random() * 3 + 3)

    return add_components(
        emap,
        cmap,
        eid,
        (
            ("pos", pos),
            ("speed", speed),
            ("image", image),
            ("boundary", boundary),
            ("lifetime", lifetime),
            ("explode", True),
            ("audio", audio),
        ),
    )


def mk_shrapnel(
    emap: EntityMap, cmap: ComponentMap, eid: EntityID, pos: pygame.Vector2
) -> tuple[EntityMap, ComponentMap]:
    speed = (
        pygame.Vector2(1, 0).rotate(random() * 360)
        * SHRAPNEL_SPEED
        * (random() * 0.5 + 0.5)
    )
    image = create_surface((8, 8), color_key="black")
    pygame.draw.circle(image, "yellow", (4, 4), 4)
    lifetime = Cooldown(random() * 0.2 + 0.1)

    return add_components(
        emap,
        cmap,
        eid,
        (("pos", pos), ("speed", speed), ("image", image), ("lifetime", lifetime)),
    )


def quary_components(
    emap: EntityMap, cids: tuple[ComponentID, ...]
) -> dict[EntityID, dict[ComponentID, Component]]:
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


def speed_system(
    emap: EntityMap, cmap: ComponentMap, dt: float, eid: EntityID
) -> tuple[EntityMap, ComponentMap, EntityID]:
    for components in quary_components(emap, ("pos", "speed")).values():
        pos, speed = components.values()
        pos += speed * dt

    return emap, cmap, eid


def lifetime_system(
    emap: EntityMap, cmap: ComponentMap, dt: float, eid: EntityID
) -> tuple[EntityMap, ComponentMap, EntityID]:
    for eid, components in emap.items():
        if not components["lifetime"].cold():
            continue
        add_component(emap, cmap, eid, "dead", True)

    return emap, cmap, eid


def dead_system(
    emap: EntityMap, cmap: ComponentMap, dt: float, eid: EntityID
) -> tuple[EntityMap, ComponentMap, EntityID]:
    for eid in quary_components(emap, ("dead",)):
        emap, cmap = remove_entity(emap, cmap, eid)
    return emap, cmap, eid


def boundary_system(
    emap: EntityMap, cmap: ComponentMap, dt: float, eid: EntityID
) -> tuple[EntityMap, ComponentMap, EntityID]:
    for components in quary_components(
        emap, ("pos", "speed", "boundary", "image")
    ).values():
        position, speed, boundary, image = components.values()
        if not (0 < position.x < (boundary.width - image.width)):
            speed.x = -speed.x
        if not (0 < position.y < (boundary.height - image.height)):
            speed.y = -speed.y

    return emap, cmap, eid


def explode_system(
    emap: EntityMap, cmap: ComponentMap, dt: float, eid: EntityID
) -> tuple[EntityMap, ComponentMap, EntityID]:
    for components in quary_components(
        emap, ("pos", "dead", "explode", "audio")
    ).values():
        pos, dead, explode, audio = components.values()

        for _ in range(5):
            eid += 1
            emap, cmap = mk_shrapnel(emap, cmap, eid, pos.copy())

        audio.play()

    return emap, cmap, eid


def run_systems(
    emap: EntityMap, cmap: ComponentMap, smap: SystemMap, dt: float, eid: EntityID
) -> tuple[EntityMap, ComponentMap, EntityID]:
    for system in smap.values():
        emap, cmap, eid = system(emap, cmap, dt, eid)

    return emap, cmap, eid


def draw_entities(surface: pygame.Surface, emap: EntityMap) -> None:
    for components in quary_components(emap, ("image", "pos")).values():
        image, pos = components.values()
        surface.blit(image, pos)


def main() -> None:
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode(DISPLAY_SIZE.xy)
    clock = pygame.time.Clock()

    sound = pygame.mixer.Sound(files("pygame.examples.data") / "car_door.wav")
    pygame.mixer.set_num_channels(64)

    entity_id: EntityID = 0
    entities: EntityMap = {}
    components: ComponentMap = {}
    systems: SystemMap = {
        "speed": speed_system,
        "boundary": boundary_system,
        "lifetime": lifetime_system,
        "explode": explode_system,
        "dead": dead_system,
    }

    running = True
    while running:
        dt = min(clock.tick(FPS) / 1000.0, DT_MAX)

        # Events
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False

        if pygame.mouse.get_pressed()[0]:
            mouse = pygame.mouse.get_pos()
            for _ in range(5):
                entity_id += 1
                entities, components = make_square(
                    entities,
                    components,
                    entity_id,
                    pygame.Vector2(mouse),
                    pygame.FRect(0, 0, *DISPLAY_SIZE.xy),
                    sound,
                )

        # Systems
        entities, components, entity_id = run_systems(
            entities, components, systems, dt, entity_id
        )

        # Render
        screen.fill("black")
        draw_entities(screen, entities)
        pygame.display.flip()


if __name__ == "__main__":
    main()

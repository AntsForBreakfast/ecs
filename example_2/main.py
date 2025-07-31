import pygame

from ecs import add_components, quary_components, run_systems
from tp import *

"""Example of switching between levels with ecs"""

"""How to make collidable system that react only when collided and only when all inside"""

DISPLAY_SIZE = (1920, 1080)
FPS = 60


def velocity_system(
    world:WorldData, events, game_state: dict, dt: float
):
    for components in quary_components(world, ("speed", "velocity")).values():
        speed, velocity = components.values()

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    velocity.x = -speed.x
                if event.key == pygame.K_d:
                    velocity.x = speed.x
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    velocity.x = 0
                if event.key == pygame.K_d:
                    velocity.x = 0


def movement_system(
    world:WorldData, events, game_state: dict, dt: float
):
    for components in quary_components(world, ("position", "velocity")).values():
        position, velocity = components.values()
        position += velocity


def collision_system(
    world:WorldData, events, game_state: dict, dt: float
):
    """Triggers when collider is all inside collidable"""
    emap, cmap = world.get('entities', {}), world.get('components', {})

    for collider_components in quary_components(
        world, ("position", "size", "collider")
    ).values():
        collider_position, collider_size, collider = collider_components.values()

        if collider:
            for collidable_id, collidable_components in quary_components(
                world, ("position", "size", "trigger", "collidable")
            ).items():
                collidable_position, collidable_size, trigger, collidable = (
                    collidable_components.values()
                )
                if (
                    collidable
                    and collider_position.x >= collidable_position.x
                    and collider_position.y >= collidable_position.y
                    and collider_position.x + collider_size.x
                    <= collidable_position.x + collidable_size.x
                    and collider_position.y + collider_size.y
                    <= collidable_position.y + collidable_size.y
                ):
                    world['components']["trigger"][collidable_id] = True
                    world['entities'][collidable_id]["trigger"] = True


def trigger_system(
    world:WorldData, events, game_state: dict, dt: float
):
    for entity_id, components in quary_components(
        world, ("trigger", "collider", "collidable")
    ).items():
        trigger, collider, collidable = components.values()
        if trigger:
            world['entities'][entity_id]["collider"] = False
            world['components']["collider"][entity_id] = False
            world['entities'][entity_id]["collidable"] = False
            world['components']["collidable"][entity_id] = False


def transition_system(
    world:WorldData, events, game_state: dict, dt: float
):
    for entity_id, components in quary_components(
        world, ("trigger", "transition", "position")
    ).items():
        trigger, transition, position = components.values()

        if trigger:
            game_state["world"] = transition
            world['entities'][entity_id]["trigger"] = False
            world['components']["trigger"][entity_id] = False

            for entity_id, components in quary_components(
                world, ("position", "velocity", "collider")
            ).items():
                pos, vel, _ = components.values()
                pos.xy = (935, 1030)
                vel.xy = (0, 0)


def draw_entities(surface: pygame.Surface, world: WorldData) -> None:
    for components in quary_components(world, ("image", "position")).values():
        image, pos = components.values()
        surface.blit(image, pos)


def main() -> None:
    pygame.init()

    screen = pygame.display.set_mode(DISPLAY_SIZE)
    clock = pygame.time.Clock()

    entity_id: EntityID = 0
    worlds: dict[WorldID, WorldData] = {
        "level_1": {
            "entities": {},
            "components": {},
            "systems": {
                "velocity": velocity_system,
                "movement": movement_system,
                "collision": collision_system,
                "trigger": trigger_system,
                "transition": transition_system,
            },
        },
        "level_2": {
            "entities": {},
            "components": {},
            "systems": {
                "velocity": velocity_system,
                "movement": movement_system,
                "collision": collision_system,
                "trigger": trigger_system,
                "transition": transition_system,
            },
        },
        "level_3": {
            "entities": {},
            "components": {},
            "systems": {
                "velocity": velocity_system,
                "movement": movement_system,
                "collision": collision_system,
                "trigger": trigger_system,
                "transition": transition_system,
            },
        },
    }
    game_state = {"world": "level_1"}

    # LEVEL 1
    entity_id += 1
    player: EntityID = entity_id
    player_size = pygame.Vector2((50, 50))
    player_image = pygame.Surface(player_size)
    pygame.draw.rect(player_image, "pink", ((0, 0), player_size))
    add_components(
        worlds["level_1"],
        player,
        (
            ("position", pygame.Vector2(935, 1030)),
            ("size", player_size),
            ("speed", pygame.Vector2(10, 0)),
            ("velocity", pygame.Vector2(0, 0)),
            ("image", player_image),
            ("collider", True),
        ),
    )

    entity_id += 1
    red_teleporter: EntityID = entity_id
    red_teleporter_position = pygame.Vector2(1570, 930)
    red_teleporter_size = pygame.Vector2(150, 150)
    red_teleporter_image = pygame.Surface(red_teleporter_size)
    pygame.draw.rect(red_teleporter_image, "red", ((0, 0), red_teleporter_size))
    add_components(
        worlds["level_1"],
        red_teleporter,
        (
            ("position", red_teleporter_position),
            ("size", red_teleporter_size),
            ("image", red_teleporter_image),
            ("trigger", False),
            ("transition", "level_2"),
            ("collidable", True),
        ),
    )

    # LEVEL 2
    entity_id += 1
    player: EntityID = entity_id
    player_size = pygame.Vector2((50, 50))
    player_image = pygame.Surface(player_size)
    pygame.draw.rect(player_image, "pink", ((0, 0), player_size))
    add_components(
        worlds["level_2"],
        player,
        (
            ("position", pygame.Vector2(935, 1030)),
            ("size", player_size),
            ("speed", pygame.Vector2(10, 0)),
            ("velocity", pygame.Vector2(0, 0)),
            ("image", player_image),
            ("collider", True),
        ),
    )

    entity_id += 1
    green_teleporter: EntityID = entity_id
    green_teleporter_position = pygame.Vector2(1570, 930)
    green_teleporter_size = pygame.Vector2(150, 150)
    green_teleporter_image = pygame.Surface(green_teleporter_size)
    pygame.draw.rect(green_teleporter_image, "green", ((0, 0), green_teleporter_size))
    add_components(
        worlds["level_2"],
        green_teleporter,
        (
            ("position", green_teleporter_position),
            ("size", green_teleporter_size),
            ("image", green_teleporter_image),
            ("trigger", False),
            ("transition", "level_3"),
            ("collidable", True),
        ),
    )

    entity_id += 1
    purple_teleporter: EntityID = entity_id
    purple_teleporter_position = pygame.Vector2(200, 930)
    purple_teleporter_size = pygame.Vector2(150, 150)
    purple_teleporter_image = pygame.Surface(purple_teleporter_size)
    pygame.draw.rect(
        purple_teleporter_image, "purple", ((0, 0), purple_teleporter_size)
    )
    add_components(
        worlds["level_2"],
        purple_teleporter,
        (
            ("position", purple_teleporter_position),
            ("size", purple_teleporter_size),
            ("image", purple_teleporter_image),
            ("trigger", False),
            ("transition", "level_1"),
            ("collidable", True),
        ),
    )

    # LEVEL 3
    entity_id += 1
    player: EntityID = entity_id
    player_size = pygame.Vector2((50, 50))
    player_image = pygame.Surface(player_size)
    pygame.draw.rect(player_image, "pink", ((0, 0), player_size))
    add_components(
        worlds["level_3"],
        player,
        (
            ("position", pygame.Vector2(935, 1030)),
            ("size", player_size),
            ("speed", pygame.Vector2(10, 0)),
            ("velocity", pygame.Vector2(0, 0)),
            ("image", player_image),
            ("collider", True),
        ),
    )

    entity_id += 1
    orange_teleporter: EntityID = entity_id
    orange_teleporter_position = pygame.Vector2(200, 930)
    orange_teleporter_size = pygame.Vector2(150, 150)
    orange_teleporter_image = pygame.Surface(orange_teleporter_size)
    pygame.draw.rect(
        orange_teleporter_image, "orange", ((0, 0), orange_teleporter_size)
    )
    add_components(
        worlds["level_3"],
        orange_teleporter,
        (
            ("position", orange_teleporter_position),
            ("size", orange_teleporter_size),
            ("image", orange_teleporter_image),
            ("trigger", False),
            ("transition", "level_2"),
            ("collidable", True),
        ),
    )

    running = True
    while running:
        dt = clock.tick(FPS) / 1000

        # Events
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        run_systems(
            worlds[game_state["world"]],
            events,
            game_state,
            dt,
        )

        # Render
        screen.fill("gray")
        draw_entities(screen, worlds[game_state["world"]])
        pygame.display.flip()


if __name__ == "__main__":
    main()

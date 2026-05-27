def choose_move(observation):
    resources = observation.get('resources', [])
    enemies = observation.get('enemies', [])
    allies = observation.get('allies', [])
    territory = observation.get('territory', [])
    position = observation.get('position', (0, 0))
    grid_width = observation.get('grid_width', 10)
    grid_height = observation.get('grid_height', 10)

    x, y = position

    # Select target based on priority: resources, enemies, territory, center
    target = None
    if resources:
        target = min(resources, key=lambda p: abs(p[0] - x) + abs(p[1] - y))
    elif enemies:
        target = min(enemies, key=lambda p: abs(p[0] - x) + abs(p[1] - y))
    elif territory:
        sx = sum(pos[0] for pos in territory) / len(territory)
        sy = sum(pos[1] for pos in territory) / len(territory)
        target = (sx, sy)
    else:
        target = (grid_width / 2, grid_height / 2)

    tx, ty = target

    dx, dy = 0, 0
    delta_x = tx - x
    delta_y = ty - y

    # Normalize movement to -1, 0, 1
    if delta_x > 0:
        dx = 1
    elif delta_x < 0:
        dx = -1
    
    if delta_y > 0:
        dy = 1
    elif delta_y < 0:
        dy = -1

    return [dx, dy]

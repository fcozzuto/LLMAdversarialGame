def choose_move(observation):
    own_pos = observation.get('own', {}).get('position', (0, 0))
    resource_positions = observation.get('resources', [])
    opponents = observation.get('opponents', [])
    territory_control_points = observation.get('territory_control_points', [])

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    own_x, own_y = own_pos

    # Pursue the nearest resource if any
    if resource_positions:
        target = min(resource_positions, key=lambda pos: dist(own_pos, pos))
        tx, ty = target
        dx = (tx - own_x)
        dy = (ty - own_y)
        dx = (dx > 0) - (dx < 0)
        dy = (dy > 0) - (dy < 0)
        return [dx, dy]

    # Pursue the nearest opponent if any
    if opponents:
        opponent_positions = [op.get('position', (0, 0)) for op in opponents]
        target = min(opponent_positions, key=lambda pos: dist(own_pos, pos))
        tx, ty = target
        dx = (tx - own_x)
        dy = (ty - own_y)
        dx = (dx > 0) - (dx < 0)
        dy = (dy > 0) - (dy < 0)
        return [dx, dy]

    # Move towards the nearest territory control point if any
    if territory_control_points:
        target = min(territory_control_points, key=lambda pos: dist(own_pos, pos))
        tx, ty = target
        dx = (tx - own_x)
        dy = (ty - own_y)
        dx = (dx > 0) - (dx < 0)
        dy = (dy > 0) - (dy < 0)
        return [dx, dy]

    # Default to staying in place
    return [0, 0]

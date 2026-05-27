def choose_move(observation):
    width = observation.get('width', 0)
    height = observation.get('height', 0)
    own_pos = observation.get('players', {}).get('own', {}).get('pos', [0, 0])
    resources = observation.get('resources', [])
    enemies = observation.get('players', {}).get('enemies', [])
    territory_control = observation.get('territory', {}).get('owner', [])

    x, y = own_pos

    def direction_towards(target_x, target_y, from_x, from_y):
        dx = 1 if target_x > from_x else -1 if target_x < from_x else 0
        dy = 1 if target_y > from_y else -1 if target_y < from_y else 0
        return dx, dy

    # Resource collection priority
    for r in resources:
        if r is None:
            continue
        rx, ry = r
        dist = abs(rx - x) + abs(ry - y)
        if dist == 1:
            return [rx - x, ry - y]
        elif dist > 1:
            dx_candidate, dy_candidate = direction_towards(rx, ry, x, y)
            return [dx_candidate, dy_candidate]

    # Pursue or evade enemies
    for enemy in enemies:
        if enemy is None:
            continue
        ex, ey = enemy.get('pos', [0, 0])
        dist = abs(ex - x) + abs(ey - y)
        if dist == 1:
            return [ex - x, ey - y]
        elif dist > 1:
            dx_candidate, dy_candidate = direction_towards(ex, ey, x, y)
            return [dx_candidate, dy_candidate]

    # Move towards territory to control
    for idx, owner in enumerate(territory_control):
        if owner is None:
            continue
        if owner != 'own':
            tx = idx % width
            ty = idx // width
            dist = abs(tx - x) + abs(ty - y)
            if dist == 1:
                return [tx - x, ty - y]
            elif dist > 1:
                dx_candidate, dy_candidate = direction_towards(tx, ty, x, y)
                return [dx_candidate, dy_candidate]

    # Default move: stay put
    return [0, 0]

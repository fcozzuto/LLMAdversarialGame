def choose_move(observation):
    own_pos = observation.get('self', {}).get('position', (0, 0))
    resources = observation.get('resources', [])
    opponents = observation.get('opponents', [])
    territory = observation.get('territory', {})

    def safe_get(d, key, default):
        return d.get(key, default) if isinstance(d, dict) else default

    def closest_point(points, origin):
        min_dist = float('inf')
        closest_pt = None
        for p in points:
            dist = abs(p[0] - origin[0]) + abs(p[1] - origin[1])
            if dist < min_dist:
                min_dist = dist
                closest_pt = p
        return closest_pt

    resource_points = safe_get(observation, 'resources', [])
    opponent_positions = []
    for opp in safe_get(observation, 'opponents', []):
        if isinstance(opp, dict):
            pos = safe_get(opp, 'position', None)
            if pos:
                opponent_positions.append(pos)
    territory_positions = []
    for t_value in safe_get(observation, 'territory', {}).values():
        if isinstance(t_value, dict):
            pos = safe_get(t_value, 'position', None)
            if pos:
                territory_positions.append(pos)

    target = None
    if resource_points:
        target = closest_point(resource_points, own_pos)
    elif opponent_positions:
        target = closest_point(opponent_positions, own_pos)
    elif territory_positions:
        target = closest_point(territory_positions, own_pos)

    if target is None:
        return [0, 0]

    dx = target[0] - own_pos[0]
    dy = target[1] - own_pos[1]
    dx = max(-1, min(1, dx))
    dy = max(-1, min(1, dy))
    return [dx, dy]

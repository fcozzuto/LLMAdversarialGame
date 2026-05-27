def choose_move(observation):
    wx = observation.get('grid_width', 0)
    wy = observation.get('grid_height', 0)
    pos = observation.get('self_position', [0, 0])
    x, y = pos[0], pos[1]
    resources = observation.get('resources', [])
    opponent_pos = observation.get('opponent_position', None)
    territory_info = observation.get('territory', {})
    settlers = observation.get('settlers', [])
    enemy_resources = observation.get('enemy_resources', [])
    
    territory_map = territory_info.get('map', {})
    
    def get_targets():
        targets = []
        # Prioritize resources
        if resources:
            targets.extend(resources)
        # Pursue opponent if present
        if opponent_pos:
            targets.append(opponent_pos)
        # Territory control points (prefer unclaimed or less controlled)
        unclaimed_or_max_owner = max(territory_map.values(), default='')
        for pos_str, owner in territory_map.items():
            if owner != 'self':
                targets.append([int(pos_str.split(',')[0]), int(pos_str.split(',')[1])])
        # Settlers nearby to prevent clustering
        for settler in settlers:
            if abs(settler[0] - x) + abs(settler[1] - y) < 3:
                targets.append(settler)
        return targets
    
    targets = get_targets()
    
    if targets:
        def dist(p):
            return abs(p[0] - x) + abs(p[1] - y)
        target = min(targets, key=dist)
        tx, ty = target
        dx = 0
        dy = 0
        if tx > x:
            dx = 1
        elif tx < x:
            dx = -1
        if ty > y:
            dy = 1
        elif ty < y:
            dy = -1
        # Normalize movement
        dx = max(-1, min(1, dx))
        dy = max(-1, min(1, dy))
        return [dx, dy]
    else:
        return [0, 0]

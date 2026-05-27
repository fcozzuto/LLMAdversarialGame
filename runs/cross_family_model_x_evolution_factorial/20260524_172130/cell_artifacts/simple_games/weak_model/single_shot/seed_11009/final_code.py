def choose_move(observation):
    # Defensive retrieval of relevant info
    resources = observation.get('resources', [])
    opponents = observation.get('opponents', [])
    allies = observation.get('allies', [])
    enemies = observation.get('enemies', [])
    territory = observation.get('territory', [])
    position = observation.get('position', (0, 0))
    # Determine if resources are nearby
    if resources:
        # Find closest resource
        resource_deltas = [(res[0] - position[0], res[1] - position[1]) for res in resources]
        # Select the resource with minimal Manhattan distance
        min_dist = None
        best_delta = (0, 0)
        for dx, dy in resource_deltas:
            dist = abs(dx) + abs(dy)
            if min_dist is None or dist < min_dist:
                min_dist = dist
                best_delta = (dx, dy)
        dx, dy = best_delta
        # Clamp move to [-1, 1]
        dx = max(-1, min(1, dx))
        dy = max(-1, min(1, dy))
        return [dx, dy]
    # Else, attempt pursuit of enemy if present
    elif enemies:
        # Find closest enemy
        enemy_deltas = [(en[0] - position[0], en[1] - position[1]) for en in enemies]
        min_dist = None
        best_delta = (0, 0)
        for dx, dy in enemy_deltas:
            dist = abs(dx) + abs(dy)
            if min_dist is None or dist < min_dist:
                min_dist = dist
                best_delta = (dx, dy)
        dx, dy = best_delta
        dx = max(-1, min(1, dx))
        dy = max(-1, min(1, dy))
        return [dx, dy]
    # Else, territorial expansion or wandering
    else:
        # Simple heuristic: move towards the nearest owned territory if available
        if territory:
            territory_deltas = [
                (t[0] - position[0], t[1] - position[1]) for t in territory
            ]
            min_dist = None
            best_delta = (0, 0)
            for dx, dy in territory_deltas:
                dist = abs(dx) + abs(dy)
                if min_dist is None or dist < min_dist:
                    min_dist = dist
                    best_delta = (dx, dy)
            dx, dy = best_delta
            dx = max(-1, min(1, dx))
            dy = max(-1, min(1, dy))
            return [dx, dy]
        # Otherwise, random walk (here, just stay still for simplicity)
        return [0, 0]

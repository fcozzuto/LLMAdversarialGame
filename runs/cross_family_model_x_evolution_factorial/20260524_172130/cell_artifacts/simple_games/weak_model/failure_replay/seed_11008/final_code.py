def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    env = observation.get("environment_name", "resource_collection")
    
    # Defensive get for opponent position
    ox, oy = observation.get("opponent_position", (sx, sy))
    
    # For pursuit_evasion environment
    if env == "pursuit_evasion":
        role = observation.get("self_role", "pursuer")
        if role == "pursuer":
            dx = 0 if ox == sx else (1 if ox > sx else -1)
            dy = 0 if oy == sy else (1 if oy > sy else -1)
            return [dx, dy]
        corners = [
            [0, 0],
            [0, observation.get("grid_height", 1) - 1],
            [observation.get("grid_width", 1) - 1, 0],
            [observation.get("grid_width", 1) - 1, observation.get("grid_height", 1) - 1],
        ]
        # Choose furthest corner
        target = max(corners, key=lambda item: abs(item[0] - ox) + abs(item[1] - oy))
        dx = 0 if target[0] == sx else (1 if target[0] > sx else -1)
        dy = 0 if target[1] == sy else (1 if target[1] > sy else -1)
        return [dx, dy]

    # For territory_control environment
    if env == "territory_control":
        targets = observation.get("unclaimed_cells") or observation.get("opponent_territory") or []
        if not targets:
            return [0, 0]
        best = min(targets, key=lambda item: abs(item[0] - sx) + abs(item[1] - sy))
        dx = 0 if best[0] == sx else (1 if best[0] > sx else -1)
        dy = 0 if best[1] == sy else (1 if best[1] > sy else -1)
        return [dx, dy]

    # For resource collection environment
    resources = observation.get("resources") or []
    if not resources:
        # No resources - move towards opponent or stay still
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        return [dx, dy]
    best = min(resources, key=lambda item: abs(item[0] - sx) + abs(item[1] - sy))
    dx = 0 if best[0] == sx else (1 if best[0] > sx else -1)
    dy = 0 if best[1] == sy else (1 if best[1] > sy else -1)
    return [dx, dy]

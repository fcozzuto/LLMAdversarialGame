def choose_move(observation):
    env = observation.get("environment_name", "resource_collection")
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    grid_width = observation.get("grid_width", 1)
    grid_height = observation.get("grid_height", 1)

    # Pursuit/Evasion behavior
    if env == "pursuit_evasion":
        role = observation.get("self_role", "pursuer")
        if role == "pursuer":
            dx = 0 if ox == sx else (1 if ox > sx else -1)
            dy = 0 if oy == sy else (1 if oy > sy else -1)
            return [dx, dy]
        corners = [
            [0, 0],
            [0, grid_height - 1],
            [grid_width - 1, 0],
            [grid_width - 1, grid_height - 1]
        ]
        target = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
        dx = 0 if target[0] == sx else (1 if target[0] > sx else -1)
        dy = 0 if target[1] == sy else (1 if target[1] > sy else -1)
        return [dx, dy]

    # Territory Control behavior
    if env == "territory_control":
        targets = (
            observation.get("unclaimed_cells") or
            observation.get("opponent_territory") or
            []
        )
        if not targets:
            return [0, 0]
        best = min(targets, key=lambda t: abs(t[0] - sx) + abs(t[1] - sy))
        dx = 0 if best[0] == sx else (1 if best[0] > sx else -1)
        dy = 0 if best[1] == sy else (1 if best[1] > sy else -1)
        return [dx, dy]

    # Resource collection behavior
    resources = observation.get("resources") or []
    if not resources:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        return [dx, dy]
    # Move towards the closest resource
    best = min(resources, key=lambda r: abs(r[0]-sx)+abs(r[1]-sy))
    dx = 0 if best[0] == sx else (1 if best[0] > sx else -1)
    dy = 0 if best[1] == sy else (1 if best[1] > sy else -1)
    return [dx, dy]

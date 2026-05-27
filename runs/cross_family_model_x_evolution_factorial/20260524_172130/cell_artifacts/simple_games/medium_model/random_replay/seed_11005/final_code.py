def choose_move(observation):
    env = observation.get("environment_name", "resource_collection")

    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    # Pursuit-Evasion logic
    if env == "pursuit_evasion":
        role = observation.get("self_role", "pursuer")
        if role == "pursuer":
            dx = 0 if ox == sx else (1 if ox > sx else -1)
            dy = 0 if oy == sy else (1 if oy > sy else -1)
            return [dx, dy]

        # Evader: move away from opponent or towards a far corner
        grid_w = observation.get("grid_width", 1)
        grid_h = observation.get("grid_height", 1)
        corners = [
            [0, 0],
            [0, grid_h - 1],
            [grid_w - 1, 0],
            [grid_w - 1, grid_h - 1],
        ]
        target = max(corners, key=lambda item: abs(item[0] - ox) + abs(item[1] - oy))
        dx = 0 if target[0] == sx else (1 if target[0] > sx else -1)
        dy = 0 if target[1] == sy else (1 if target[1] > sy else -1)
        return [dx, dy]

    # Territory Control logic
    if env == "territory_control":
        targets = observation.get("unclaimed_cells") or observation.get("opponent_territory") or []
        if not targets:
            return [0, 0]
        best = min(targets, key=lambda item: abs(item[0] - sx) + abs(item[1] - sy))
        dx = 0 if best[0] == sx else (1 if best[0] > sx else -1)
        dy = 0 if best[1] == sy else (1 if best[1] > sy else -1)
        return [dx, dy]

    # Resource collection logic (default path)
    resources = observation.get("resources") or []
    if not resources:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        return [dx, dy]

    best = min(resources, key=lambda item: abs(item[0] - sx) + abs(item[1] - sy))
    dx = 0 if best[0] == sx else (1 if best[0] > sx else -1)
    dy = 0 if best[1] == sy else (1 if best[1] > sy else -1)
    return [dx, dy]

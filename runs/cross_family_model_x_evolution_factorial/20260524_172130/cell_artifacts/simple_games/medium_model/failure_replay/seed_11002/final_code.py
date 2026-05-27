def choose_move(observation):
    obs = observation or {}
    env = obs.get("environment_name", "resource_collection")
    sx, sy = obs.get("self_position", (0, 0))
    ox, oy = obs.get("opponent_position", (sx, sy))

    # Pursuit-Evasion mode
    if env == "pursuit_evasion":
        role = obs.get("self_role", "pursuer")
        if role == "pursuer":
            dx = 0 if ox == sx else (1 if ox > sx else -1)
            dy = 0 if oy == sy else (1 if oy > sy else -1)
            return [dx, dy]

        grid_w = obs.get("grid_width", 1)
        grid_h = obs.get("grid_height", 1)
        corners = [
            [0, 0],
            [0, grid_h - 1],
            [grid_w - 1, 0],
            [grid_w - 1, grid_h - 1],
        ]
        target = min(corners, key=lambda item: abs(item[0] - ox) + abs(item[1] - oy))
        dx = 0 if target[0] == sx else (1 if target[0] > sx else -1)
        dy = 0 if target[1] == sy else (1 if target[1] > sy else -1)
        return [dx, dy]

    # Territory control mode
    if env == "territory_control":
        targets = obs.get("unclaimed_cells") or obs.get("opponent_territory") or []
        if not targets:
            return [0, 0]
        best = min(targets, key=lambda item: abs(item[0] - sx) + abs(item[1] - sy))
        dx = 0 if best[0] == sx else (1 if best[0] > sx else -1)
        dy = 0 if best[1] == sy else (1 if best[1] > sy else -1)
        return [dx, dy]

    # Resource collection mode (default)
    resources = obs.get("resources") or []
    if not resources:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        return [dx, dy]

    best = min(resources, key=lambda item: abs(item[0] - sx) + abs(item[1] - sy))
    dx = 0 if best[0] == sx else (1 if best[0] > sx else -1)
    dy = 0 if best[1] == sy else (1 if best[1] > sy else -1)
    return [dx, dy]

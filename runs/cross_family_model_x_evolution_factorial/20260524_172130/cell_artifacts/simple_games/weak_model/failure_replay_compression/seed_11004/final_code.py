def choose_move(observation):
    env = observation.get("environment_name", "")
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    grid_width = observation.get("grid_width", 1)
    grid_height = observation.get("grid_height", 1)

    # Pursuit/Evasion
    if env == "pursuit_evasion":
        role = observation.get("self_role", "")
        if role == "pursuer":
            dx = 0 if ox == sx else (1 if ox > sx else -1)
            dy = 0 if oy == sy else (1 if oy > sy else -1)
            return [dx, dy]
        corners = [
            [0, 0],
            [0, grid_height - 1],
            [grid_width - 1, 0],
            [grid_width - 1, grid_height - 1],
        ]
        target = max(corners, key=lambda item: abs(item[0] - ox) + abs(item[1] - oy))
        dx = 0 if target[0] == sx else (1 if target[0] > sx else -1)
        dy = 0 if target[1] == sy else (1 if target[1] > sy else -1)
        return [dx, dy]

    # Territory Control
    if env == "territory_control":
        targets = []
        if "unclaimed_cells" in observation and observation.get("unclaimed_cells") is not None:
            targets = observation.get("unclaimed_cells", [])
        elif "opponent_territory" in observation and observation.get("opponent_territory") is not None:
            targets = observation.get("opponent_territory", [])
        if not targets:
            return [0, 0]
        best = min(targets, key=lambda item: abs(item[0] - sx) + abs(item[1] - sy))
        dx = 0 if best[0] == sx else (1 if best[0] > sx else -1)
        dy = 0 if best[1] == sy else (1 if best[1] > sy else -1)
        return [dx, dy]

    # Resource collection
    resources = observation.get("resources") or []
    if resources:
        best_resource = min(resources, key=lambda item: abs(item[0] - sx) + abs(item[1] - sy))
        dx = 0 if best_resource[0] == sx else (1 if best_resource[0] > sx else -1)
        dy = 0 if best_resource[1] == sy else (1 if best_resource[1] > sy else -1)
        return [dx, dy]

    # Default fallback movement: move towards opponent or stay put
    dx = 0 if ox == sx else (1 if ox > sx else -1)
    dy = 0 if oy == sy else (1 if oy > sy else -1)
    return [dx, dy]

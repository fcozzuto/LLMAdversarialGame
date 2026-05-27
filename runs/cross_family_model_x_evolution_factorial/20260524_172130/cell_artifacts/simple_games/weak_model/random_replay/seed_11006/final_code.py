def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    env = observation.get("environment_name", "resource_collection")
    dx, dy = 0, 0

    if env == "pursuit_evasion":
        role = observation.get("self_role", "pursuer")
        ox, oy = observation.get("opponent_position", [sx, sy])

        if role == "pursuer":
            dx = 0 if ox == sx else (1 if ox > sx else -1)
            dy = 0 if oy == sy else (1 if oy > sy else -1)
            return [dx, dy]
        else:
            corners = [
                [0, 0],
                [0, observation.get("grid_height", 1) - 1],
                [observation.get("grid_width", 1) - 1, 0],
                [observation.get("grid_width", 1) - 1, observation.get("grid_height", 1) - 1]
            ]
            ox, oy = observation.get("opponent_position", [sx, sy])
            target = min(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
            dx = 0 if target[0] == sx else (1 if target[0] > sx else -1)
            dy = 0 if target[1] == sy else (1 if target[1] > sy else -1)
            return [dx, dy]

    if env == "territory_control":
        targets = observation.get("unclaimed_cells") or observation.get("opponent_territory") or []
        if targets:
            best = min(targets, key=lambda c: abs(c[0] - sx) + abs(c[1] - sy))
            dx = 0 if best[0] == sx else (1 if best[0] > sx else -1)
            dy = 0 if best[1] == sy else (1 if best[1] > sy else -1)
            return [dx, dy]
        else:
            dx, dy = 0, 0
            return [dx, dy]

    resources = observation.get("resources") or []
    if resources:
        best = min(resources, key=lambda c: abs(c[0] - sx) + abs(c[1] - sy))
        dx = 0 if best[0] == sx else (1 if best[0] > sx else -1)
        dy = 0 if best[1] == sy else (1 if best[1] > sy else -1)
        return [dx, dy]

    # Default move towards opponent or center
    ox, oy = observation.get("opponent_position", [sx, sy])
    dx = 0 if ox == sx else (1 if ox > sx else -1)
    dy = 0 if oy == sy else (1 if oy > sy else -1)
    return [dx, dy]

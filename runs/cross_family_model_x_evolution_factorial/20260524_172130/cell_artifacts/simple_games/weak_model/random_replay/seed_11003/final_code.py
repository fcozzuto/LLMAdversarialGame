def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    env = observation.get("environment_name", "resource_collection")
    grid_width = observation.get("grid_width", 10)
    grid_height = observation.get("grid_height", 10)

    # Defensive extraction with default values
    resources = observation.get("resources") or []
    unclaimed_cells = observation.get("unclaimed_cells") or []
    opponent_territory = observation.get("opponent_territory") or []
    role = observation.get("self_role", "pursuer")
    targets = []

    if env == "pursuit_evasion":
        if role == "pursuer":
            dx = 0 if ox == sx else (1 if ox > sx else -1)
            dy = 0 if oy == sy else (1 if oy > sy else -1)
            return [dx, dy]
        # Move towards opponent's position if no specific pursuit
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        return [dx, dy]

    elif env == "territory_control":
        targets = unclaimed_cells or opponent_territory
        if not targets:
            return [0,0]
        best = min(targets, key=lambda c: abs(c[0] - sx) + abs(c[1] - sy))
        dx = 0 if best[0] == sx else (1 if best[0] > sx else -1)
        dy = 0 if best[1] == sy else (1 if best[1] > sy else -1)
        return [dx, dy]

    # For resource collection
    if resources:
        best_resource = min(resources, key=lambda c: abs(c[0] - sx) + abs(c[1] - sy))
        dx = 0 if best_resource[0] == sx else (1 if best_resource[0] > sx else -1)
        dy = 0 if best_resource[1] == sy else (1 if best_resource[1] > sy else -1)
        return [dx, dy]
    else:
        # No resources, move towards opponent or default to a random step
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        return [dx, dy]

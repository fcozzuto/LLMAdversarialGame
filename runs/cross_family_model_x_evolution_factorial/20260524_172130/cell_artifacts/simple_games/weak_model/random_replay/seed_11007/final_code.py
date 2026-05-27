def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    environment = observation.get("environment_name", "resource_collection")
    grid_width = observation.get("grid_width", 1)
    grid_height = observation.get("grid_height", 1)
    def get_closest_target(targets):
        if not targets:
            return None
        return min(targets, key=lambda pos: abs(pos[0] - sx) + abs(pos[1] - sy))
    def move_towards(target):
        dx, dy = 0, 0
        if target:
            if target[0] > sx:
                dx = 1
            elif target[0] < sx:
                dx = -1
            if target[1] > sy:
                dy = 1
            elif target[1] < sy:
                dy = -1
        return dx, dy
    if environment == "pursuit_evasion":
        role = observation.get("self_role", "pursuer")
        if role == "pursuer":
            return list(move_towards((ox, oy)))
        corners = [[0, 0], [0, grid_height - 1], [grid_width - 1, 0], [grid_width - 1, grid_height - 1]]
        target = get_closest_target(corners)
        return list(move_towards(target))
    elif environment == "territory_control":
        targets = observation.get("unclaimed_cells") or observation.get("opponent_territory") or []
        target = get_closest_target(targets)
        if not target:
            return [0, 0]
        return list(move_towards(target))
    else:
        resources = observation.get("resources") or []
        target = get_closest_target(resources)
        if not target:
            dx = 0 if ox == sx else (1 if ox > sx else -1)
            dy = 0 if oy == sy else (1 if oy > sy else -1)
            return [dx, dy]
        return list(move_towards(target))

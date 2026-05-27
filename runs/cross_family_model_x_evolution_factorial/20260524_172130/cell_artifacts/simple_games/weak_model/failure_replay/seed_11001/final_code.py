def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    env = observation.get("environment_name", "resource_collection")
    
    def get_field(data, key, default=None):
        return data.get(key, default) if isinstance(data, dict) else default
    
    # Pursuit-evasion behavior
    if env == "pursuit_evasion":
        role = get_field(observation, "self_role", "pursuer")
        if role == "pursuer":
            dx = 0 if ox == sx else (1 if ox > sx else -1)
            dy = 0 if oy == sy else (1 if oy > sy else -1)
            return [dx, dy]
        else:
            corners = [
                [0, 0],
                [0, get_field(observation, "grid_height", 1) - 1],
                [get_field(observation, "grid_width", 1) - 1, 0],
                [get_field(observation, "grid_width", 1) - 1, get_field(observation, "grid_height", 1) - 1],
            ]
            target = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
            dx = 0 if target[0] == sx else (1 if target[0] > sx else -1)
            dy = 0 if target[1] == sy else (1 if target[1] > sy else -1)
            return [dx, dy]
    # Territory control
    if env == "territory_control":
        targets = get_field(observation, "unclaimed_cells") or get_field(observation, "opponent_territory") or []
        if not targets:
            return [0,0]
        best = min(targets, key=lambda t: abs(t[0] - sx) + abs(t[1] - sy))
        dx = 0 if best[0] == sx else (1 if best[0] > sx else -1)
        dy = 0 if best[1] == sy else (1 if best[1] > sy else -1)
        return [dx, dy]
    # Resource collection
    resources = get_field(observation, "resources") or []
    if not resources:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        return [dx, dy]
    best_res = min(resources, key=lambda r: abs(r[0] - sx) + abs(r[1] - sy))
    dx = 0 if best_res[0] == sx else (1 if best_res[0] > sx else -1)
    dy = 0 if best_res[1] == sy else (1 if best_res[1] > sy else -1)
    return [dx, dy]

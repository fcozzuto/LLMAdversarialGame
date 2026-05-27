def choose_move(observation):
    env = observation.get("environment_name", "resource_collection")
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    
    def move_towards(target_x, target_y):
        dx = 0
        dy = 0
        if target_x > sx:
            dx = 1
        elif target_x < sx:
            dx = -1
        if target_y > sy:
            dy = 1
        elif target_y < sy:
            dy = -1
        return [dx, dy]
    
    if env == "pursuit_evasion":
        role = observation.get("self_role", "pursuer")
        if role == "pursuer":
            return move_towards(ox, oy)
        corners = [
            [0, 0],
            [0, observation.get("grid_height", 1) - 1],
            [observation.get("grid_width", 1) - 1, 0],
            [observation.get("grid_width", 1) - 1, observation.get("grid_height", 1) - 1],
        ]
        target = max(corners, key=lambda item: abs(item[0] - ox) + abs(item[1] - oy))
        return move_towards(target[0], target[1])
    if env == "territory_control":
        targets = observation.get("unclaimed_cells") or observation.get("opponent_territory") or []
        if not targets:
            return [0, 0]
        best = min(targets, key=lambda item: abs(item[0] - sx) + abs(item[1] - sy))
        return move_towards(best[0], best[1])
    resources = observation.get("resources") or []
    if not resources:
        return move_towards(ox, oy)
    best_res = min(resources, key=lambda item: abs(item[0] - sx) + abs(item[1] - sy))
    return move_towards(best_res[0], best_res[1])

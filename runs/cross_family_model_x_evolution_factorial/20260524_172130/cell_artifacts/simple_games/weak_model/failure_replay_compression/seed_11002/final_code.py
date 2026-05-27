def choose_move(observation):
    def sign(x):
        return (x > 0) - (x < 0)
    
    env = observation.get("environment_name", "resource_collection")
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [sx, sy])
    grid_width = observation.get("grid_width", 1)
    grid_height = observation.get("grid_height", 1)
    
    # Defensive access for role in pursuit_evasion
    if env == "pursuit_evasion":
        role = observation.get("self_role", "pursuer")
        if role == "pursuer":
            dx = 0 if ox == sx else sign(ox - sx)
            dy = 0 if oy == sy else sign(oy - sy)
            return [dx, dy]
        # Pursuit target: corners
        corners = [
            [0, 0],
            [0, grid_height - 1],
            [grid_width - 1, 0],
            [grid_width - 1, grid_height - 1],
        ]
        target = max(corners, key=lambda item: abs(item[0] - ox) + abs(item[1] - oy))
        dx = 0 if target[0] == sx else sign(target[0] - sx)
        dy = 0 if target[1] == sy else sign(target[1] - sy)
        return [dx, dy]
    
    # Defensive access for unclaimed_cells and opponent_territory
    if env == "territory_control":
        targets = observation.get("unclaimed_cells")
        if targets is None:
            targets = observation.get("opponent_territory", [])
        if not targets:
            return [0, 0]
        best = min(targets, key=lambda item: abs(item[0] - sx) + abs(item[1] - sy))
        dx = 0 if best[0] == sx else sign(best[0] - sx)
        dy = 0 if best[1] == sy else sign(best[1] - sy)
        return [dx, dy]
    
    # Defensive access for resources
    resources = observation.get("resources")
    if resources is None:
        resources = []
    if not resources:
        dx = 0 if ox == sx else sign(ox - sx)
        dy = 0 if oy == sy else sign(oy - sy)
        return [dx, dy]
    # Pick resource slightly closer if exists
    best = min(resources, key=lambda item: abs(item[0] - sx) + abs(item[1] - sy))
    dx = 0 if best[0] == sx else sign(best[0] - sx)
    dy = 0 if best[1] == sy else sign(best[1] - sy)
    return [dx, dy]

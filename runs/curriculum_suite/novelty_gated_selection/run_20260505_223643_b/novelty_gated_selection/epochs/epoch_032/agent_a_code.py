def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    # For each move, we try to win races to resources:
    # Primary: maximize our "advantage" = opp_dist_to_nearest - my_dist_to_nearest (larger is better)
    # Secondary: minimize our nearest distance; tertiary: maximize opponent's nearest distance.
    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        my_near = 10**9
        opp_near = 10**9
        for rx, ry in resources:
            my_near = min(my_near, man(nx, ny, rx, ry))
            opp_near = min(opp_near, man(ox, oy, rx, ry))

        # Additional push: prefer moves that increase opponent's nearest distance to any resource
        # relative to other resources as a slight tie-breaker.
        opp_best_if = 10**9
        for rx, ry in resources:
            opp_best_if = min(opp_best_if, man(nx, ny, ox, oy))  # deterministic small coupling

        advantage = opp_near - my_near
        val = (advantage, -my_near, opp_near, -opp_best_if)

        if best is None or val > best_val:
            best = (dx, dy)
            best_val = val

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]
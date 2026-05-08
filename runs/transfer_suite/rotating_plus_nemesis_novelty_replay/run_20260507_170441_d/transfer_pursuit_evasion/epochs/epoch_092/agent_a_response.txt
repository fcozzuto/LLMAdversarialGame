def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        try:
            x, y = int(o[0]), int(o[1])
        except Exception:
            continue
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role) or ("evade" in role)

    def nearest_obstacle_dist(x, y):
        md = 10**9
        for (px, py) in obstacles:
            d = abs(px - x) + abs(py - y)
            if d < md:
                md = d
        return md if obstacles else 999999

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        dist = abs(nx - ox) + abs(ny - oy)
        nd = nearest_obstacle_dist(nx, ny)
        # Pursuer: minimize distance; Evader: maximize distance.
        val = dist + (0.15 * (1 if nd <= 1 else 0) - 0.02 * nd)
        # Add slight bias to keep moving roughly in the direction of objective.
        dir_bias = (abs(dx) + abs(dy)) * 0.001
        if is_evader:
            # maximize: invert
            val = -val - dir_bias
        else:
            val = val + dir_bias

        if best is None or val < best_val:
            best = [dx, dy]
            best_val = val

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]
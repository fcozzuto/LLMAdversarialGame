def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    role = observation.get("self_role", "pursuer")
    want_far = (role == "evader")

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def min_obst_dist(nx, ny):
        if not obstacles:
            return 999
        m = 999
        for ax, ay in obstacles:
            d = abs(ax - nx) + abs(ay - ny)
            if d < m:
                m = d
                if m == 0:
                    return 0
        return m

    best = None
    best_score = -10**30 if not want_far else -10**30
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dist2 = (ox - nx) * (ox - nx) + (oy - ny) * (oy - ny)
        md = min_obst_dist(nx, ny)
        # For pursuer: minimize distance, stay away from obstacles.
        # For evader: maximize distance, stay away from obstacles.
        score = (-dist2 if not want_far else dist2) + (0.08 * md)
        if best is None or score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]
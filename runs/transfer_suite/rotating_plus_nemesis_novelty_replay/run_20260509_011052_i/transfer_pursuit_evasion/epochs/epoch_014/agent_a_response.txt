def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    role = (observation.get("self_role") or "").lower()
    is_pursuer = ("purs" in role) or ("chaser" in role) or ("seeker" in role)

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    def nearest_corner_dist(x, y):
        return min(abs(x - cx) + abs(y - cy) for cx, cy in corners)

    obs_adj = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
    def obstacle_risk(x, y):
        r = 0
        for dx, dy in obs_adj:
            if (x + dx, y + dy) in obstacles:
                r += 1
        return r

    def score_candidate(nx, ny):
        d = max(abs(nx - ox), abs(ny - oy))  # capture when exact overlap (radius 0)
        my_corner = nearest_corner_dist(nx, ny)
        opp_corner = nearest_corner_dist(ox, oy)
        # Pursuer: minimize distance, but prefer staying away from obstacles to avoid getting pinned.
        # Evader: maximize distance, prefer to run toward the far corner.
        stay_clear = -obstacle_risk(nx, ny)
        if is_pursuer:
            return (-d, -abs(my_corner - opp_corner), stay_clear)
        else:
            return (d, my_corner, -stay_clear)

    best = None
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        sc = score_candidate(nx, ny)
        if best is None or sc > best if not is_pursuer else sc > best:
            best = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]
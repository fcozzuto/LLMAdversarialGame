def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = "evader" in role

    obstacles = observation.get("obstacles", []) or []
    obs_set = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def nearest_obs_dist(x, y):
        if not obs_set:
            return 99
        best = 99
        for ax, ay in obs_set:
            d = abs(x - ax) + abs(y - ay)
            if d < best:
                best = d
        return best

    def edge_penalty(x, y):
        # discourage/encourage depending on role
        m = min(x, y, w - 1 - x, h - 1 - y)
        return m  # higher is more central

    best_move = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obs_set:
            continue

        d_to_opp = abs(nx - ox) + abs(ny - oy)
        nd = nearest_obs_dist(nx, ny)

        # obstacle proximity penalty
        obs_pen = 0
        if nd == 0:
            obs_pen = 10**7
        elif nd == 1:
            obs_pen = 400
        elif nd == 2:
            obs_pen = 120
        elif nd == 3:
            obs_pen = 40

        center = edge_penalty(nx, ny)

        if is_evader:
            # maximize distance from pursuer; slightly prefer staying away from edges
            score = (d_to_opp * 1000) + (center * 5) + (nd * 2) - obs_pen
        else:
            # minimize distance to pursuer; prefer central moves if tie
            score = (-d_to_opp * 1000) + (center * 2) + (nd * 1) - obs_pen

        if best_score is None:
            best_score = score
            best_move = (dx, dy)
        else:
            if score > best_score:
                best_score = score
                best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]
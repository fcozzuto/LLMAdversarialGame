def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    evader = ("evader" in role) or ("runner" in role) or ("escape" in role)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    turn_par = int(observation.get("turn_index", 0) or 0) % 2
    if turn_par:
        moves = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]

    def min_obs_d(x, y):
        md = 10**9
        for (ax, ay) in obstacles:
            d = abs(x - ax) + abs(y - ay)
            if d < md:
                md = d
        return md if obstacles else 10

    best_dxdy = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        man = abs(nx - ox) + abs(ny - oy)
        sq = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        od = min_obs_d(nx, ny)

        # Repel obstacles; stronger when close.
        obs_pen = 0.0
        if obstacles:
            if od <= 1:
                obs_pen = 1000.0
            elif od == 2:
                obs_pen = 120.0
            else:
                obs_pen = 18.0 / (od + 1)

        if evader:
            # Prefer larger distance; also avoid running into obstacle-adjacent squares.
            val = (sq, man, od)  # maximize
            score = (val[0] - obs_pen, val[1] - obs_pen * 0.1, val[2])
            better = (best_val is None) or (score > best_val)
        else:
            # Pursuer: minimize distance; avoid obstacle adjacency.
            score = (-sq - obs_pen, -man - obs_pen * 0.2, od)  # maximize on negative
            better = (best_val is None) or (score > best_val)

        if better:
            best_val = score
            best_dxdy = (dx, dy)

    return [best_dxdy[0], best_dxdy[1]]
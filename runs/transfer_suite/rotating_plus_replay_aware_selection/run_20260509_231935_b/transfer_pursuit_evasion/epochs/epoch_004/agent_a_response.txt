def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = {(int(x), int(y)) for x, y in obstacles}

    sr = str(observation.get("self_role", "")).lower()
    orr = str(observation.get("opponent_role", "")).lower()
    am_evader = ("evad" in sr) and not ("evad" in orr)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def free_adj(x, y):
        c = 0
        for dx, dy in deltas:
            nx = clamp(x + dx, 0, w - 1)
            ny = clamp(y + dy, 0, h - 1)
            if (nx, ny) not in obs:
                c += 1
        return c

    best = None
    best_move = [0, 0]

    # Deterministic ordering for tie-break
    ordered = sorted(deltas, key=lambda d: (d[0], d[1]))

    for dx, dy in ordered:
        nx = clamp(sx + dx, 0, w - 1)
        ny = clamp(sy + dy, 0, h - 1)
        if (nx, ny) in obs:
            nx, ny = sx, sy
            dx, dy = 0, 0

        dist = abs(nx - ox) + abs(ny - oy)
        adj = free_adj(nx, ny)

        # Score: if evader, maximize distance; else minimize distance.
        if am_evader:
            key = (dist, adj, -nx, -ny)  # prefer going to opposite "north-west"
        else:
            key = (-dist, adj, nx, ny)   # prefer moving toward opponent

        if best is None or key > best:
            best = key
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]
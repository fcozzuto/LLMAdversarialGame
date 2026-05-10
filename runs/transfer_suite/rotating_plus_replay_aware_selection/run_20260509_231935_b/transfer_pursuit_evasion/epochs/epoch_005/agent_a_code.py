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
    self_is_evader = ("evad" in sr) and not ("evad" in orr)

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

    # Deterministic tie-break
    ordered = sorted(deltas, key=lambda d: (d[0], d[1]))

    best_score = None
    best_move = [0, 0]

    for dx, dy in ordered:
        nx, ny = clamp(sx + dx, 0, w - 1), clamp(sy + dy, 0, h - 1)
        if (nx, ny) in obs:
            nx, ny, dx, dy = sx, sy, 0, 0

        dist = abs(nx - ox) + abs(ny - oy)
        mobility = free_adj(nx, ny)

        if self_is_evader:
            # maximize distance; keep mobility
            score = dist * 10 + mobility
        else:
            # minimize distance; avoid low mobility and avoid giving opponent an immediate advantage
            score = -dist * 10 + mobility * 0.5

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move
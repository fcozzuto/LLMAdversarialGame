def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def clamp(v, lo, hi):
        if v < lo:
            return lo
        if v > hi:
            return hi
        return v

    best = None
    best_val = None
    for dx, dy in dirs:
        nx = clamp(sx + dx, 0, w - 1)
        ny = clamp(sy + dy, 0, h - 1)
        if (nx, ny) in obstacles:
            continue
        d = abs(nx - ox) + abs(ny - oy)
        # Prefer moves that decrease distance to opponent; small tie-breakers for being mobile.
        if observation.get("self_role") == "evader":
            val = d
        else:
            val = -d
        free = 0
        for adx, ady in dirs:
            tx, ty = nx + adx, ny + ady
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) not in obstacles:
                free += 1
        val = val * 1000 + free
        if best is None or val > best_val:
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]
def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def cell_set(key):
        s = set()
        for t in observation.get(key) or []:
            try:
                s.add((int(t[0]), int(t[1])))
            except Exception:
                pass
        return s

    obstacles = cell_set("obstacles")

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        dist = abs(nx - ox) + abs(ny - oy)
        # small tie-breakers: prefer horizontal/vertical then staying still last
        tie = (0 if dx == 0 or dy == 0 else 1, 1 if (dx == 0 and dy == 0) else 0)
        val = (dist, tie)
        if best is None or val < best_val:
            best = [dx, dy]
            best_val = val

    if best is not None:
        return best

    # If blocked everywhere, return deterministic safe-ish fallback
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h:
            return [dx, dy]
    return [0, 0]
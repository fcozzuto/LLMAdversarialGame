def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            oset.add((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in oset:
            continue
        d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        # Intercept: strongly prefer smallest distance; if tie, prefer not increasing distance and avoiding staying.
        stay_pen = 1 if (dx == 0 and dy == 0) else 0
        cur_d2 = (sx - ox) * (sx - ox) + (sy - oy) * (sy - oy)
        inc_pen = 1 if d2 > cur_d2 else 0
        key = (d2, inc_pen, stay_pen, dx == 0 and dy == 0)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    return [int(best[0]), int(best[1])]
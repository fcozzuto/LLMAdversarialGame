def choose_move(observation):
    w = int(observation.get("grid_width", 8)) or 8
    h = int(observation.get("grid_height", 8)) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    self_role = observation.get("self_role", "")
    obstacles = observation.get("obstacles", []) or []
    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            try:
                oset.add((int(p[0]), int(p[1])))
            except:
                pass

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            ok = inside(nx, ny) and (nx, ny) not in oset
            if ok:
                candidates.append((dx, dy))

    if not candidates:
        return [0, 0]

    def dist(x, y, tx, ty):
        return abs(x - tx) + abs(y - ty)

    evader = (self_role == "evader")
    best = None
    best_key = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        d = dist(nx, ny, ox, oy)
        # Prefer moving while keeping deterministic tie-breaking: diagonal > straight > stay, then sign order
        diag_bonus = 0 if (dx == 0 or dy == 0) else -0.01
        stay_pen = 0.02 if (dx == 0 and dy == 0) else 0.0
        if not evader:
            key = (d, stay_pen, -diag_bonus, -dx, -dy)
        else:
            key = (-d, stay_pen, -diag_bonus, -dx, -dy)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    return [int(best[0]), int(best[1])]
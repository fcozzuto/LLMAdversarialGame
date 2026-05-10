def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    evader = ("evader" in role) or ("run" in role) or ("escape" in role) or ("flee" in role)
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or blocked(nx, ny):
            continue
        dist2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        # small obstacle-avoidance: prefer positions with more legal neighbors
        legal_neighbors = 0
        for ddx, ddy in moves:
            tx, ty = nx + ddx, ny + ddy
            if inside(tx, ty) and not blocked(tx, ty):
                legal_neighbors += 1
        val = (dist2 if evader else -dist2) + (legal_neighbors * 0.01)
        if best_val is None:
            best, best_val = [dx, dy], val
        else:
            if (val > best_val) if (evader) else (val > best_val):
                best, best_val = [dx, dy], val

    if best is None:
        return [0, 0]
    return best
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
    is_evader = ("evader" in role) or ("escape" in role) or ("flee" in role) or ("run" in role)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    def legal_neighbors(x, y):
        c = 0
        for ddx, ddy in moves:
            tx, ty = x + ddx, y + ddy
            if inside(tx, ty) and not blocked(tx, ty):
                c += 1
        return c

    best_move = [0, 0]
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or blocked(nx, ny):
            continue
        dist2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        neigh = legal_neighbors(nx, ny)
        # Deterministic tie-break: fixed order in moves list; compute scalar value only
        if is_evader:
            # Maximize distance; also prefer fewer dead-ends (more neighbors)
            val = dist2 * 1000 + neigh
        else:
            # Minimize distance; also prefer fewer dead-ends (more neighbors)
            val = -dist2 * 1000 + neigh
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]
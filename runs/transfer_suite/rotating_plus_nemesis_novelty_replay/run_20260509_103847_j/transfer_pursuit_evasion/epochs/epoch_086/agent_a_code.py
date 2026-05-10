def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    is_evader = ("evad" in role) or ("escap" in role) or ("run" in role) or ("runner" in role)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def dist_measure(x, y):
        # Chebyshev is effective for diagonal movement and capture radius 0
        return max(abs(x - ox), abs(y - oy))

    def wall_margin(x, y):
        return min(x, y, w - 1 - x, h - 1 - y)

    best_move = [0, 0]
    if is_evader:
        best_key = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = dist_measure(nx, ny)
            # Prefer larger distance; if tied, avoid corners (bigger wall margin);
            # if still tied, prefer more mobility.
            free = 0
            for ddx, ddy in deltas:
                tx, ty = nx + ddx, ny + ddy
                if legal(tx, ty):
                    free += 1
            key = (d, wall_margin(nx, ny), free, -abs(nx - ox) - abs(ny - oy))
            if best_key is None or key > best_key:
                best_key = key
                best_move = [dx, dy]
    else:
        best_key = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = dist_measure(nx, ny)
            # Prefer smaller distance; if tied, increase mobility; if still tied, drift toward opponent.
            free = 0
            for ddx, ddy in deltas:
                tx, ty = nx + ddx, ny + ddy
                if legal(tx, ty):
                    free += 1
            key = (-d, free, (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy))
            if best_key is None or key > best_key:
                best_key = key
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]
def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inside(x, y): return 0 <= x < w and 0 <= y < h

    obst = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y):
                obst.add((x, y))

    res = []
    for p in observation.get("resources") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y) and (x, y) not in obst:
                res.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not res:
        tx, ty = (w - 1 if sx < w - 1 else 0), (h - 1 if sy < h - 1 else 0)
    else:
        # Pick a target that is near and also "safer" vs opponent
        best_t = None
        best_key = None
        for rx, ry in res:
            d1 = cheb(sx, sy, rx, ry)
            d2 = cheb(ox, oy, rx, ry)
            key = (d1 - 0.75 * d2, d1, d2, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best_t = (rx, ry)
        tx, ty = best_t

    # Evaluate one-step moves
    best_m = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obst:
            continue

        d_self = cheb(nx, ny, tx, ty)
        d_opp = cheb(ox, oy, tx, ty)

        # Encourage moving toward target; discourage letting opponent get closer.
        # If landing on a resource (current list), strongly prefer.
        land_is_res = 1 if (nx, ny) in set(res) else 0

        # Additional local safety: avoid getting adjacent to opponent
        adj_opp = 1 if cheb(nx, ny, ox, oy) <= 1 else 0

        val = (d_self - 1.6 * d_opp - 8.0 * land_is_res + 3.0 * adj_opp, d_self, -land_is_res, nx, ny)
        if best_val is None or val < best_val:
            best_val = val
            best_m = (dx, dy)

    # Fallback: if all moves blocked, stay
    return [int(best_m[0]), int(best_m[1])]
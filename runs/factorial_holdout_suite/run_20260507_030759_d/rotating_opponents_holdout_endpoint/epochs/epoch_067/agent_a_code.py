def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b, c, d):
        return abs(a - c) if abs(a - c) > abs(b - d) else abs(b - d)

    def valid_cell(x, y):
        return inb(x, y) and (x, y) not in blocked

    valid_res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and valid_cell(x, y):
                valid_res.append((x, y))
    if not valid_res:
        moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        best = (0, 0)
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid_cell(nx, ny):
                continue
            opp_d = cheb(nx, ny, ox, oy)
            key = (opp_d, -abs(nx - w // 2) - abs(ny - h // 2), -cheb(nx, ny, 0, 0))
            if best_key is None or key > best_key:
                best_key = key
                best = (dx, dy)
        return [best[0], best[1]]

    # Pick target where we are relatively closer than opponent (Chebyshev distance).
    best_target = None
    best_key = None
    for tx, ty in valid_res:
        self_d = cheb(sx, sy, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        key = (opp_d - self_d, -self_d, -abs(tx - ox) - abs(ty - oy), -abs(tx - (w - 1 - sx)) - abs(ty - (h - 1 - sy)))
        if best_key is None or key > best_key:
            best_key = key
            best_target = (tx, ty)

    tx, ty = best_target

    dx_pref = 0 if tx == sx else (1 if tx > sx else -1)
    dy_pref = 0 if ty == sy else (1 if ty > sy else -1)

    # Greedy local move with obstacle-aware evaluation.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid_cell(nx, ny):
            continue
        self_d = cheb(nx, ny, tx, ty)
        opp_d = cheb(nx, ny, ox, oy)

        # Prefer moving toward target while also denying opponent.
        to_target = -self_d
        deny = opp_d
        align = (1 if dx == dx_pref else 0) + (1 if dy == dy_pref else 0)
        key = (align, to_target, deny, -(abs(nx - tx) + abs(ny - ty)))
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)

    return [int(best[0]), int(best[1])]
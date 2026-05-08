def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role_s = str(observation.get("self_role", "")).lower()
    i_am_pursuer = any(k in role_s for k in ("pursuer", "chaser", "catch", "pursuit"))

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x, y, tx, ty):
        dx = abs(x - tx)
        dy = abs(y - ty)
        return dx if dx >= dy else dy

    def free_adj(x, y):
        s = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if valid(nx, ny):
                    s += 1
        return s

    if i_am_pursuer:
        best = (10**9, None)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            if nx == ox and ny == oy:
                return [dx, dy]
            d = cheb(nx, ny, ox, oy)
            # Prefer reducing distance; prefer moves with more local freedom to avoid wall-trap.
            sc = (d, -free_adj(nx, ny), dx, dy)
            if sc < best:
                best = (sc, [dx, dy])
        return best[1] if best[1] is not None else [0, 0]

    # Evader: run to maximize distance from pursuer; also avoid getting boxed near obstacles.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    # Deterministic target: farthest corner from pursuer.
    tx, ty = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    best = (-10**9, None)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Combine: keep away from pursuer, and drift toward chosen corner.
        dist_away = cheb(nx, ny, ox, oy)
        drift = -cheb(nx, ny, tx, ty)
        # Penalize tightness to resist wall-run cuts.
        tight_pen = -free_adj(nx, ny)  # tight => smaller free_adj => larger negative, penalize by adding tightness magnitude
        sc = dist_away * 10 + drift + tight_pen * 0.1
        if sc > best[0] or (sc == best[0] and (dx, dy) < tuple(best[1] or (1, 1))):
            best = (sc, [dx, dy])
    return best[1] if best[1] is not None else [0, 0]
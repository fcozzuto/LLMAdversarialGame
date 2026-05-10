def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    is_evader = ("evad" in role) or ("escap" in role) or ("run" in role) or ("runner" in role)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x, y):
        dx = abs(x - ox)
        dy = abs(y - oy)
        return dx if dx >= dy else dy

    def obstacle_proximity(x, y):
        # Chebyshev distance to nearest obstacle cell (0 if on obstacle, but legality prevents)
        best = 10**9
        for (bx, by) in blocked:
            d = abs(x - bx)
            e = abs(y - by)
            dd = d if d >= e else e
            if dd < best:
                best = dd
                if best == 1:
                    break
        return best if best != 10**9 else 9

    def wall_margin(x, y):
        left = x
        right = w - 1 - x
        top = y
        bottom = h - 1 - y
        m = left if left < right else right
        m = top if top < m else m
        return bottom if bottom < m else m

    best = None
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        d = cheb(nx, ny)
        prox = obstacle_proximity(nx, ny)
        wm = wall_margin(nx, ny)

        if is_evader:
            # Avoid getting boxed: prefer staying away from obstacles and boundaries,
            # but still maximize distance from pursuer.
            key = (d * 100, prox * 5 + wm, wm, -((nx == ox) or (ny == oy)))
        else:
            # Pursuer: greedily minimize distance; avoid tight obstacle proximity.
            key = (-d * 100, -(prox * 2 + wm), wm)

        if best is None or key > best:
            best = key
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]
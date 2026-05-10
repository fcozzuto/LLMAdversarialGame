def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    if resources:
        best = None
        best_key = (-10**9, -10**9, -10**9, -10**9)
        for x, y in resources:
            sd = cheb(sx, sy, x, y)
            od = cheb(ox, oy, x, y)
            race = od - sd  # want positive
            # tie-break toward states that are hard for opponent: small sd, large od
            key = (race, od, -sd, -(x * 9 + y))
            if key > best_key:
                best_key = key
                best = (x, y)
        tx, ty = best
    else:
        # fallback: move to reduce distance to opponent (spoil) or to nearest corner deterministically
        tx, ty = (w - 1, 0) if (sx + sy) % 2 == 0 else (0, h - 1)

    dx0 = 0 if tx == sx else (1 if tx > sx else -1)
    dy0 = 0 if ty == sy else (1 if ty > sy else -1)

    # Prefer move that reduces cheb distance the most, then avoids obstacles.
    candidates = []
    for dx in (dx0, 0, -dx0):
        for dy in (dy0, 0, -dy0):
            if dx0 == 0 and dy != dy0 and dy != 0 and dy != -dy0:
                continue
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                candidates.append((cheb(nx, ny, tx, ty), cheb(nx, ny, ox, oy), dx, dy))
    if candidates:
        candidates.sort(key=lambda t: (-t[0], t[1], t[2], t[3]))
        # candidates stores (next_dist_to_target, dist_to_opponent, dx, dy) with we want smaller target dist
        candidates.sort(key=lambda t: (t[0], t[1], abs(t[2]) + abs(t[3]), t[2], t[3]))
        return [int(candidates[0][2]), int(candidates[0][3])]

    # If all preferred moves blocked, try any safe adjacent deterministically.
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [int(dx), int(dy)]
    return [0, 0]
def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    role = str(observation.get("self_role") or "").lower()
    purs_me = ("purs" in role) or (role == "pursuer")
    target_res = None
    best_rd = None
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                d = dist(sx, sy, rx, ry)
                if best_rd is None or d < best_rd:
                    best_rd = d
                    target_res = (rx, ry)

    def want_value(nx, ny):
        if target_res is not None:
            rx, ry = target_res
            d = dist(nx, ny, rx, ry)
            # If we are pursuer, prefer getting to resources and opponent; else, prefer distancing.
            if purs_me:
                return -(d + 0.35 * dist(nx, ny, ox, oy))
            return d + 0.35 * dist(nx, ny, ox, oy)
        # No resources: pure opponent chase or evade.
        d = dist(nx, ny, ox, oy)
        return -d if purs_me else d

    best = None
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        v = want_value(nx, ny)
        if bestv is None or v > bestv:
            bestv = v
            best = [dx, dy]

    if best is not None:
        return best

    # Fallback: stay if possible, else first legal move
    if legal(sx, sy):
        return [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if legal(nx, ny):
            return [dx, dy]
    return [0, 0]
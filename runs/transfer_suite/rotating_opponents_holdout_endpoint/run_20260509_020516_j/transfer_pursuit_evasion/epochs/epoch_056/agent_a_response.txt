def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for it in observation.get("obstacles") or []:
        try:
            if isinstance(it, dict):
                x, y = it.get("x"), it.get("y")
            else:
                x, y = it[0], it[1]
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def sqdist(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    def opp_best(nx, ny):
        best = None
        best_d = None
        for odx, ody in moves:
            tx, ty = ox + odx, oy + ody
            if not valid(tx, ty):
                tx, ty = ox, oy
            d = sqdist(nx, ny, tx, ty)
            if best_d is None or d < best_d:  # pursuit_direct: minimize distance
                best_d = d
                best = (tx, ty)
        return best

    scored = []
    for dx, dy in moves:
        tx, ty = sx + dx, sy + dy
        if not valid(tx, ty):
            tx, ty = sx, sy
        ox2, oy2 = opp_best(tx, ty)
        d2 = sqdist(tx, ty, ox2, oy2)
        # small tie-break: prefer movement that increases manhattan distance
        md = abs(tx - ox) + abs(ty - oy)
        scored.append((d2, md, dx, dy))

    scored.sort(key=lambda t: (-t[0], -t[1], t[2], t[3]))
    return [int(scored[0][2]), int(scored[0][3])]
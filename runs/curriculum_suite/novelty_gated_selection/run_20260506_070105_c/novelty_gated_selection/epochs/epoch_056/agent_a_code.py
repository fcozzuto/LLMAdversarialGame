def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = observation.get("obstacles", []) or []
    obstacles = set((int(o[0]), int(o[1])) for o in obs if len(o) >= 2)

    res = observation.get("resources", []) or []
    resources = []
    for r in res:
        if len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if (x, y) not in obstacles:
                resources.append((x, y))

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            myd = md(sx, sy, rx, ry)
            opd = md(ox, oy, rx, ry)
            ahead = (1 if rx > sx else -1 if rx < sx else 0) * (rx - sx) + (1 if ry > sy else -1 if ry < sy else 0) * (ry - sy)
            key = (-(opd - myd), myd, -ahead, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)

        tx, ty = best
        dx = 1 if tx > sx else (-1 if tx < sx else 0)
        dy = 1 if ty > sy else (-1 if ty < sy else 0)
        if dx == 0 and dy == 0:
            dx = 1 if ox <= sx else -1 if ox > sx else 0
            dy = 1 if oy <= sy else -1 if oy > sy else 0
        return [int(dx), int(dy)]

    dx = 1 if ox > sx else (-1 if ox < sx else 0)
    dy = 1 if oy > sy else (-1 if oy < sy else 0)
    return [int(dx), int(dy)]
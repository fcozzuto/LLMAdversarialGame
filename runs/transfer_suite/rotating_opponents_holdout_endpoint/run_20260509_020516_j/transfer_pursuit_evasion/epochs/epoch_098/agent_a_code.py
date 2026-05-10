def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    res_list = observation.get("resources") or []
    resources = []
    for r in res_list:
        try:
            if isinstance(r, dict):
                x, y = r.get("x"), r.get("y")
            else:
                x, y = r[0], r[1]
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                resources.append((x, y))
        except Exception:
            pass

    def clamp(x, y):
        if x < 0:
            x = 0
        elif x >= w:
            x = w - 1
        if y < 0:
            y = 0
        elif y >= h:
            y = h - 1
        return x, y

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = None

    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)
        if (nx, ny) in obstacles:
            continue
        opp_d = dist2(nx, ny, ox, oy)
        if resources:
            mind = 10**18
            for rx, ry in resources:
                d = dist2(nx, ny, rx, ry)
                if d < mind:
                    mind = d
            score = (-mind, opp_d)
        else:
            score = (0, opp_d)
        if best is None or score > best_score:
            best_score = score
            best = (dx, dy)

    return [best[0], best[1]] if best is not None else [0, 0]